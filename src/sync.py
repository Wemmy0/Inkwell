import mysql.connector
import os
from os.path import isfile
import hashlib


# Sync is here
class Sync:
    def __init__(self, config, verbose):
        self.path = config["path"]
        config = config["database"]
        if not config["enabled"]:
            self.disabled = True
            return
        try:
            self.connection = mysql.connector.connect(host=config["host"],
                                                      database=config["database"],
                                                      user=config["username"],
                                                      password=config["password"])
            self.disabled = False
        except mysql.connector.errors.DatabaseError as err:
            print(err)
            print(f"❌ Unable to reach {config['username']}@{config['host']}, sync disabled")
            self.disabled = True
            return
        self.cursor = self.connection.cursor()

        self.buffer_size = 65536

        self.uploaded = 0
        self.downloaded = 0
        self.skipped = 0
        self.verbose = verbose

        self.do()

    def convert_to_blob(self, filename):
        with open(filename, 'rb') as file:
            blob_data = file.read()
        return blob_data

    def compare_files(self, file):
        self.cursor.execute(f"SELECT hash FROM test WHERE filename = %s", (file,))
        db_hash = self.cursor.fetchall()[0][0]
        local_hash = self.hash_file(file)
        self.log("=" * 20 + file + "=" * 20)
        self.log(f"Local Hash: {local_hash}")
        self.log(f"DB Hash: {db_hash}")

        if local_hash == db_hash:
            self.log("Hashes match, skipping file")
            self.skipped += 1
        else:
            self.log("Hashes don't match, checking timestamps")
            self.cursor.execute(f"SELECT modified FROM test WHERE filename = %s", (file,))
            db_timestamp = int(self.cursor.fetchall()[0][0])
            local_timestamp = round(os.path.getctime(file))
            self.log(f"Local timestamp: {local_timestamp}")
            self.log(f"DB timestamp: {db_timestamp}")

            if local_timestamp > db_timestamp:
                self.log("Local file is newer, uploading")
                self.update_file(file, local_timestamp, local_hash)

            elif local_timestamp < db_timestamp:
                self.log("Local file is older, downloading")
                self.download_file(file)
            else:
                self.log("Timestamps match, skipping")
                self.skipped += 1
        self.log("=" * (40 + len(file)))

    def update_file(self, file, time, hash):
        try:
            # Purpose: Update file in db if local is newer
            self.cursor.execute(
                "UPDATE test SET modified = %s, hash = %s, content = %s WHERE filename = %s",
                (time, hash, mysql.connector.Binary(self.convert_to_blob(file)), file,))
            self.connection.commit()
            self.uploaded += 1
        except mysql.connector.errors.DataError:
            self.log(f"⚠️ File {file} is too large, skipping")
            self.skipped += 1

    def create_file(self, filename, content):
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
            self.create_file(filename, content)

    def scan_files(self, path):
        out = []
        for i in os.listdir(path):
            if not isfile(path + "/" + i):  # Item is a folder
                out += self.scan_files(path + "/" + i)
            else:
                self.log(f"Found file {path + '/' + i}")
                out.append(path + "/" + i)
        return out

    def download_file(self, file):
        # Purpose: Download file from db if db is newer
        self.cursor.execute("SELECT content FROM test WHERE filename = %s", (file,))
        content = self.cursor.fetchall()[0][0]
        self.create_file(file, content)
        self.downloaded += 1

    def upload_file(self, file):
        try:
            self.cursor.execute(
                "INSERT INTO test value(%s, %s, %s, %s)",
                (file, round(os.path.getctime(file)), self.hash_file(file),
                 mysql.connector.Binary(self.convert_to_blob(file)),))
            self.connection.commit()
            self.uploaded += 1
        except mysql.connector.errors.DataError:
            self.log(f"⚠️ File {file} is too large, skipping")
            self.skipped += 1

    def hash_file(self, file):
        md5 = hashlib.md5()
        with open(file, 'rb') as f:
            while True:
                data = f.read(self.buffer_size)
                if not data:
                    break
                md5.update(data)
        return md5.hexdigest()

    def do(self):
        if not self.disabled:
            if not os.path.exists(self.path):
                self.log("⚠️ New Folder doesn't exist, creating")
                os.makedirs(self.path)

            local_files = self.scan_files(self.path)
            self.cursor.execute("SELECT filename FROM test")
            db_files = self.cursor.fetchall()

            for i in range(len(db_files)):
                # Fix formatting of db_files
                db_files[i] = db_files[i][0]

            for i in db_files:
                if i in local_files:
                    # Existing files in db and local
                    self.compare_files(i)
                else:
                    # New file in db
                    self.log(f"New file in DB, downloading {i}")
                    self.download_file(i)
            # Find new files that aren't in the db

            for i in list(set(local_files) - set(db_files)):
                # New file local
                self.log(f"{i} is new to the db and will be uploaded")
                self.upload_file(i)
            self.report()
            print("✅ Sync successful")

    def report(self):
        print(f"⬆️ {self.uploaded} files\n"
              f"⬇️ {self.downloaded} files\n"
              f"⏭️ {self.skipped} files")
        self.uploaded, self.downloaded, self.skipped = 0, 0, 0

    def close(self):
        if not self.disabled:
            print("Closing sync connection...")
            self.connection.close()

    def log(self, *args):
        if self.verbose:
            print(*args)
