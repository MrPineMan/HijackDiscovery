from asyncio.subprocess import DEVNULL
import re
import string
from os.path import join
import subprocess
from time import sleep
from traceback import print_exception

from logzero import logger
from utils.generic import list_to_file, mkdir, path_to_file, to_df_csv


class Strings(object):

    def __init__(self, outdir):
        self.outdir = outdir
        # Keep track of the potential arguments for later quick search
        self.dataset = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.dataset = None

        if exc_type is not None:
            print_exception(exc_type, exc_value, tb)
            return False # uncomment to pass exception through
        return True


    def find_elevated(self, file):
        strings_cmd = ["bin\\floss.exe", "--show-metainfo", "--no-stack-strings", "--no-decoded-strings", file]
        output = subprocess.run(strings_cmd, stderr=subprocess.DEVNULL, stdout=subprocess.PIPE)
        auto_eval = "<autoElevate>true</autoElevate>"
        if auto_eval in str(output.stdout):
            return True
        return False
        


    # def extract(self, fullpath, min=4):
    #     # Catch command-line arguments below the min length of 4, 
    #     # for example command '-v' or '/v'
    #     cli_args = ['/','\\','-']
    #     common_args = ['--help', '/?', '-h', '-v', '--version']
    #     counter = 0
    #     with open(fullpath, errors="ignore") as f: 
    #         result = ""
    #         for c in f.read():
    #             if c in string.printable:
    #                 result += c
    #                 continue
    #             if len(result) >= min or set(result).intersection(cli_args):
    #                 if set(result).intersection(cli_args):
    #                     counter = counter + 1 
    #                 yield result
    #             result = ""
    #         if len(result) >= min or set(result).intersection(cli_args):  # catch result at EOF
    #             if set(result).intersection(cli_args):
    #                 counter = counter + 1 
    #             yield result
        
    #     self.dataset.append({
    #         "fullpath":fullpath,
    #         "filename":path_to_file(fullpath),
    #         "counter":counter
    #     })

    # def cli_args(self, itemlist:list):
    #     outdir = mkdir(join(self.outdir, "strings"))
    #     for fullpath in itemlist:
    #         sl = list(self.extract(fullpath))

    #         REGEX_PATTERN = r"(--(\?<option>.+\?)\s+(\?<value>.(\?:[^-].+\?)\?(\?:(\?=--)\|$))\?)+?"
    #         pattern = re.compile(REGEX_PATTERN)

    #         lines_to_log = [line for line in sl if pattern.match(line)]
    #         print(lines_to_log)
    #         if any((match := pattern.match(x)) for x in sl):
    #             print(match.group(0))

            
    #         outfile = join(outdir, path_to_file(fullpath))
    #         print(outfile)
    #         list_to_file(sl, outfile)

    #     to_df_csv(self.dataset, outdir, "potential_argument_count")

    