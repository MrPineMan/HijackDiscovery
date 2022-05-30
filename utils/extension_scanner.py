import os
from pathlib import Path
from typing import Mapping

def run_fast_scandir(dir:str, ext:list):    # dir: str, ext: list
    subfolders, files = [], []

    for f in os.scandir(dir):
        if f.is_dir():
            subfolders.append(f.path)
        if f.is_file():
            if os.path.splitext(f.name)[1].lower() in ext:
                files.append(f.path)

    for dir in list(subfolders):
        sf, f = run_fast_scandir(dir, ext)
        subfolders.extend(sf)
        files.extend(f)
    return subfolders, files


def write_to_file(fname, data):
    with open(fname, 'w+') as file:
        if isinstance(data, list):
            for item in data:
                file.write(item + '\n')

folder = "C:\\Windows\\System32"
subfolders, files = run_fast_scandir(folder, [".dll"])
write_to_file('output-libraries.txt', files)

subfolders, files = run_fast_scandir(folder, [".exe"])
write_to_file('output-applications.txt', files)


