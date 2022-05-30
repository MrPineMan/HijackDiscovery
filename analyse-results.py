import pandas as pd
import ast
import os

path = 'out\\chrome\\' # use your path
all_files = [os.path.join(dirpath, f)
    for dirpath, dirnames, files in os.walk(path)
    for f in files if f == ('summary.csv.txt')]

li = []

for filename in all_files:
    with open(filename, 'r') as f:
        data = ast.literal_eval(f.read())
    list_of_dicts = []
    for value in  data["potentials"]:
        # word_to_check = word_to_check[-30:].replace("\\","\\\\").lower()
        # wordlist = list((map(lambda x: x.lower(), data["hijacks"])))

        # result = any(word_to_check in word for word in wordlist)
        # print(result)
        # d= dict(file=data["file"], autoEvelate=data["autoElevate"], potentials=value)
        d= dict(file=data["file"], autoEvelate=None, potentials=value)
        list_of_dicts.append(d)

        df = pd.DataFrame(list_of_dicts)
        li.append(df)

frame = pd.concat(li, axis=0, ignore_index=True)
frame.to_csv("results.csv")