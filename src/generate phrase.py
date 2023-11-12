import random


def random_row(rows):
	return rows[random.randint(0, len(rows))] \
		.lower() \
		.strip('\n') + "-"


def gen_phrase(num, words):
	out = ""
	for _ in range(num):
		out += random_row(words)
	return out[:-1]


with open("words.txt") as file:
	file = file.readlines()
	for i in range(10):
		print(gen_phrase(3, file))
