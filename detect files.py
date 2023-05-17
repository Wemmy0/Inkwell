import os
from os.path import isfile


def scan_dir(path):
	out = []
	for i in os.listdir(path):
		if not isfile(path + "/" + i):
			out = out + scan_dir(path + "/" + i)
		else:
			out.append(path + "/" + i)
	return out


found = scan_dir("/home/tom/PycharmProjects")
print(f"{len(found)} files found")
