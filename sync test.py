import mysql.connector
import os
from os.path import isfile
import hashlib

connection = mysql.connector.connect(host='localhost',
                                     database='Notes',
                                     user='root',
                                     password='NEA')
cursor = connection.cursor()

buffer_size = 65536
directory = "Folder"


def convert_to_blob(filename):
	with open(filename, 'rb') as file:
		blob_data = file.read()
	return blob_data


def scan_files(path):
	out = []
	for i in os.listdir(path):
		if not isfile(path + "/" + i):
			out = out + scan_files(path + "/" + i)
		else:
			print(f"Found file {path + '/' + i}")
			out.append(path + "/" + i)
	return out


def hash_file(file):
	md5 = hashlib.md5()
	with open(file, 'rb') as f:
		while True:
			data = f.read(buffer_size)
			if not data:
				break
			md5.update(data)
	return md5.hexdigest()


def compare_files(file):
	cursor.execute(f"SELECT hash FROM test WHERE filename = '{file}'")
	db_hash = cursor.fetchall()[0][0]
	local_hash = hash_file(file)
	print(f"===================={file}====================")
	print(f"Local Hash: {local_hash}")
	print(f"DB Hash: {db_hash}")

	if local_hash == db_hash:
		print("Hashes match, skipping file")
	else:
		print("Hashes don't match, checking timestamps")
		cursor.execute(f"SELECT modified FROM test WHERE filename = '{file}'")
		db_timestamp = int(cursor.fetchall()[0][0])
		local_timestamp = round(os.path.getctime(file))
		print(f"Local timestamp: {local_timestamp}")
		print(f"DB timestamp: {db_timestamp}")

		if local_timestamp > db_timestamp:
			print("Local file is newer, uploading")
			update_file(file, local_timestamp, local_hash)

		if local_timestamp < db_timestamp:
			print("Local file is older, downloading")
			download_file(file)
	print("=====================================")


def update_file(file, time, hash):
	# Purpose: Update file in db if local is newer
	cursor.execute(f"UPDATE test SET modified = {time}, hash = '{hash}', content = %s WHERE filename = '{file}'",
	               (mysql.connector.Binary(convert_to_blob(file)),))
	connection.commit()


def create_file(filename, content):
	try:
		# Try and create file
		with open(filename, 'wb+') as f:
			f.write(content)
	except FileNotFoundError:
		# If dir of new file doesn't exist, create folder structure
		path = ""
		for folder in filename.split("/")[:-1]:
			path += folder + "/"
		os.makedirs(path[:-1])
		create_file(filename, content)


def download_file(file):
	# Purpose: Download file from db if db is newer
	cursor.execute(f"SELECT content FROM test WHERE filename = '{file}'")
	content = cursor.fetchall()[0][0]
	create_file(file, content)


def upload_file(file):
	cursor.execute(f"INSERT INTO test value('{file}', '{round(os.path.getctime(file))}', '{hash_file(file)}', %s)",
	               (mysql.connector.Binary(convert_to_blob(file)),))
	connection.commit()


if not os.path.exists(directory):
	print("IMPORTANT: Folder doesn't exist, creating")
	os.makedirs(directory)
local_files = scan_files(directory)

cursor.execute("SELECT filename FROM test")
db_files = cursor.fetchall()

for i in range(len(db_files)):
	# Fix formatting of db_files
	db_files[i] = db_files[i][0]

for i in db_files:
	if i in local_files:
		# Existing files in db and local
		compare_files(i)
	else:
		# New file in db
		print(f"New file in DB, downloading {i}")
		download_file(i)

# Find new files that aren't in the db
for i in list(set(local_files) - set(db_files)):
	# New file local
	print(f"{i} is new to the db and will be uploaded")
	upload_file(i)
