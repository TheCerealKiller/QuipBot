import csv

prompts = []

prefix_len = len("Question: ")

with open("raw.txt", 'r') as raw:
    for l in raw.readlines():
        if (l.startswith("Question: ")):
            prompts.append(l[prefix_len:])

with open("prompts.txt", 'w') as f:
    f.write(''.join(prompts))
