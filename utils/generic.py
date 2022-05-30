
import os
import csv
import glob
import pickle
from distutils.util import strtobool
from enum import unique
from os import makedirs
from os.path import exists, join, splitext
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
from config import settings
from logzero import logger


def is_valid_folder(parser, arg):
    if not exists(arg):
        parser.error(f"The file {arg} does not exist!")
    return file_to_path(arg)


def path_to_file(path):
    return str(Path(path).name)
    
def file_to_path(fname):
    return str(Path(fname).resolve())

def uniquify(path):
    filename, extension = splitext(path)
    counter = 1

    while exists(path):
        path = f"{filename}({str(counter)}){extension}"
        counter += 1
    return path

def to_pickle_file(itemlist:list, outfile):
    outfile = uniquify(f"{file_to_path(outfile)}.pckl")

    with open(outfile, 'wb') as fp:
        pickle.dump(itemlist, fp)
    logger.info(f"List saved to pickle file: {outfile}")
    
    return outfile

def to_text_file(data, outfile):
    outfile = f"{outfile}.txt"

    with open(outfile, 'w+') as fp:
        if isinstance(data, list):
            for item in data:
                fp.write(f"{item}\n")
        fp.write(str(data))

    logger.debug(f"List saved to text file: {outfile}")
    
    return outfile

def list_to_file(itemlist:list, outfile):
    # if settings.DEBUG_MODE:
    #     to_pickle_file(itemlist, outfile)
    to_text_file(itemlist, outfile)

    return True

def pickle_file_to_list(infile):
    infile = file_to_path(infile)

    with open (infile, 'rb') as fp:
        itemlist = pickle.load(fp)
    logger.info(f"Input file {infile} contains {len(itemlist)} entries")
    return itemlist

def mkdir(dirname, exist_ok=True):
    try:
        makedirs(dirname, exist_ok=exist_ok)
    except OSError as e:
        logger.error(e)
        raise OSError(e)
    return dirname

def to_df_csv(data, outdir, fname):
    outfile = f"{join(outdir, fname)}.csv"
    df = pd.DataFrame(data)
    df.to_csv(path_or_buf=outfile, index=False)
    logger.info(f"File saved to: {outfile}")
    
    return outfile
# def to_csv(self, fname:str, dataframe=None):
#     outfile = uniquify(f'{join(self.outdir, fname)}.csv')
#     logger.info(f"Save dataframe as: {outfile}")
#     dataframe.to_csv(outfile, encoding='utf-8', index=False)
#     return outfile 


def query_yes_no(question, default='no'):
    if default is None:
        prompt = " [y/n] "
    elif default == 'yes':
        prompt = " [Y/n] "
    elif default == 'no':
        prompt = " [y/N] "
    else:
        raise ValueError(f"Unknown setting '{default}' for default.")

    while True:
        try:
            resp = input(question + prompt).strip().lower()
            if default is not None and resp == '':
                return default == 'yes'
            else:
                return strtobool(resp)
        except ValueError:
            print("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")


# subfolders, files = search_extensions(folder, [".jpg"])
def search_extensions(dir, ext):    # dir: str, ext: list
    subfolders, files = [], []
    try:
        for f in os.scandir(dir):
            if f.is_dir():
                subfolders.append(f.path)
            if f.is_file():
                if os.path.splitext(f.name)[1].lower() in ext:
                    files.append(f.path)
    except PermissionError:
        pass


    for dir in list(subfolders):
        sf, f = search_extensions(dir, ext)
        subfolders.extend(sf)
        files.extend(f)
    return set(subfolders), set(files)
