from enum import unique
from os.path import join, splitext, exists
from re import I
from traceback import print_exception
from typing import TypedDict

import pandas as pd
from logzero import logger

from utils.generic import uniquify, list_to_file

class Dataset():
    def __init__(self, data_source):
        # self.data = data 
        self.data_source = data_source
        self.ext_column = "extension"
        self.fullpath_column = "fullpath" 
        self.df = None

    def __enter__(self):
        try:
            self.df = pd.read_csv(self.data_source)
            logger.info(f"Succesfully parsed from CSV: {self.data_source} ")
        except TypeError:
            raise TypeError(f"Unable to parse data to panda dataframe")
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.df = None
        if exc_type is not None:
            print_exception(exc_type, exc_value, tb)
            return False # uncomment to pass exception through
        return True

    def __str__(self):
        return self.df
    
    def dedupe_and_sort(self, key):
        logger.debug("Executing dedupe_and_sort")
        self.df.sort_values(key, ascending=False)
        
        self.df.drop_duplicates(subset=key)
        
    def compute_extension(self):
        logger.debug(f"Enrich dataset with self.ext_column column")
        for index in range(len(self.df.fullpath)):
            fname, file_extension = splitext(self.df.at[index,self.fullpath_column])
            self.df.at[index, self.ext_column] = file_extension[1:]

    def overview(self):
        logger.debug(f"Compute dataframe overview")

        if not self.ext_column in self.df.columns:
            self.compute_extension()
        df = self.df[self.ext_column].value_counts(ascending=True)
        logger.info(f"\n{df}")
        return df

    def filter_on_extension(self, extensions:list):
        logger.debug(f"Filter dataframe on extensions: {extensions}")

        if not self.ext_column in self.df.columns:
            self.compute_extension()

        df = self.df[self.df[self.ext_column].isin(extensions)]
        logger.debug(f"\n{df}")
        return df

    def export_extension_lists(self, outdir):
        # logger.debug(f"Filter dataframe on extensions: {extensions}")

        if not self.ext_column in self.df.columns:
            self.compute_extension()

        # Get list of different extensions found
        unique = self.df[self.ext_column].unique()
        ret = {}
        for ext in unique:
            # select all rows matching self.ext_column == ext 
            ext_items = self.df.loc[self.df[self.ext_column] == ext]
            all_items = ext_items[self.fullpath_column].tolist()
            # Write to file
            outfile = uniquify(join(outdir, f"{ext}_list({len(all_items)})"))
            list_to_file(all_items, outfile)
            # Save in dict
            ret.update({ext: all_items})
        return ret

        