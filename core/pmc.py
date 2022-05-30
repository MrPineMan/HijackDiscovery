#!/usr/python3
from http.server import executable
import subprocess
import threading
from fileinput import filename
from os import getcwd, remove
from os.path import join
from shutil import copyfile
from time import sleep
from traceback import print_exception

import psutil
from config import settings
from genericpath import exists, isfile
from logzero import logger
from procmon_parser import (Column, ProcmonLogsReader, Rule, RuleAction,
                            RuleRelation, dump_configuration,
                            load_configuration)
from utils.generic import file_to_path, mkdir, path_to_file
import pandas as pd

class Runner(threading.Thread):
    def __init__(self, filter):
        threading.Thread.__init__(self)
        self.filter = filter

    def __enter__(self):
        procmon_cmd = [settings.PROCMON_BIN, "/minimized", "/quiet", "/accepteula", "/loadconfig", f"{self.filter}"]
        subprocess.Popen(procmon_cmd, shell=False)


    def __exit__(self, exc_type, exc_value, tb):
        procmon_stop_cmd = [settings.PROCMON_BIN, "/terminate"]
        subprocess.run(procmon_stop_cmd)
        
        if exc_type is not None:
            print_exception(exc_type, exc_value, tb)
            return False # uncomment to pass exception through
        return True

class Procmon(object):

    def __init__(self, outdir):
        self.outdir = outdir

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            print_exception(exc_type, exc_value, tb)
            return False # uncomment to pass exception through
        return True


    def generate_filter(self, executable):
        executable_fname = path_to_file(executable)
        filter = join(self.outdir, f"{executable_fname}.pmc")
        
        if isfile(filter):
            return filter

        # Define new rules
        rules = [
            Rule('Process_Name', 'is', executable_fname, 'include'),
            Rule('Path', 'contains', '.dll', 'include')
        ]
        # Load template config file (The template does not have any filters enabled.)
        with open(settings.PROCMON_TEMPLATE, "rb") as f:
            config = load_configuration(f)        

        # Apply new rules
        config["FilterRules"] = rules

        # Dump modified config
        with open(filter, "wb") as f:
            dump_configuration(config, f)

        return filter


    def run(self, executable, filter):
        filename = path_to_file(executable)

        if isfile(filename):
            return self.filter(join(self.outdir, f"{filename}.csv"))

        try: 
            remove(settings.DEFAULT_PROCMON_LOG_OUTFILE)
        except FileNotFoundError:
            pass

        with Runner(filter) as r:

            logger.debug(f"Start Procmon with filter file: {executable}")
            # High-end, cutting-edge, state of the art timeout implementation 
            sleep(3)
            # Run the copied application for {timeout} seconds
            timeout = 5 # seconds 
            subp = subprocess.Popen(executable, shell=True)
            p = psutil.Process(subp.pid)
            try:
                p.wait(timeout=timeout)
            except psutil.TimeoutExpired:
                p.kill()
                pass                

        # I'm tired, bit more sleep is required (to properly exit) ;)
        sleep(2)
        return self.save(filename, filter)

    def save(self, filename, filter):
        outfile = join(self.outdir, f"{filename}.csv")
        procmon_cmd = [settings.PROCMON_BIN, "/accepteula", "/loadconfig", filter, "/quiet", "/minimized",  "/openlog", settings.DEFAULT_PROCMON_LOG_OUTFILE, "/saveapplyfilter", "/saveas", outfile]
        subprocess.run(procmon_cmd)
        # We're not in a hurry, grab another coffee, we cant fail at this point! Saving the crown juwels.
        sleep(2)
        logger.debug(f"Procmon output saved to: {outfile}")  
        return self.filter(csvfile=outfile)


    def filter(self, csvfile):
        df = pd.read_csv(csvfile)
        # Filter on Path and Result
        df = df[df.Result == "FAST IO DISALLOWED"]
        # Replace to match the csv path's: C:\\Users\\ 
        # with the output path's: C:\Users\
        df = df[df.Path.str.contains(self.outdir.replace("\\","\\\\"))]
        df.Path.to_csv(csvfile) # Overwrite
        return (csvfile, df)

