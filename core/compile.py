
from os.path import join, isfile
import subprocess
from sys import stderr
from time import sleep
from traceback import print_exception
from typing import List

from jinja2 import Environment, FileSystemLoader
from logzero import logger
from utils.generic import mkdir, path_to_file, to_text_file
from config import settings

class Compile(object):
    def __init__(self, outdir):
        self.outdir = outdir
        self.file_loader = FileSystemLoader('template')
        self.env = Environment(loader=self.file_loader)
        

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            print_exception(exc_type, exc_value, tb)
            return False # uncomment to pass exception through
        return True

    def setup(self, variables):

        outfile = join(self.outdir, path_to_file(variables["file"]))
        # C file generator
        c_template = self.env.get_template("dll_c.jinja2")
        c_code = c_template.render(dll_exports=variables["exports"])
        with open(f'{outfile}.c', "w+") as f:
            f.write(c_code)

        # Def file generator
        def_template = self.env.get_template("dll_def.jinja2")
        def_code = def_template.render(dll_exports=variables["exports"])    
        with open(f'{outfile}.def', "w+") as f:
            f.write(def_code)

        sleep(1)
        return (f"{outfile}.c", f"{outfile}.def")
        
    def build(self, file, c_file, def_file):
        outfile = join(self.outdir, path_to_file(file))
        # stdout_file = join(self.outdir, f"{file}_stdout")
        # stderr_file = join(self.outdir, f"{file}_stderr")

        # Example:
        # C:\cygwin64\bin\x86_64-w64-mingw32-gcc.exe -shared -mwindows authz.dll.c authz.dll.def -o authz.dll        
        build_cmd = [settings.CYGWIN64_BIN, "-shared", "-mwindows", c_file, def_file, "-o", outfile]
        p = subprocess.run(build_cmd, capture_output=True, text=True) 

        # to_text_file(p.stdout, stdout_file)
        # to_text_file(p.stderr, stderr_file)
        
        # Return filename compiled succesfully.
        return outfile if isfile(outfile) else None
