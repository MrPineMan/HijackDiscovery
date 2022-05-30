
#!/usr/bin/python

from genericpath import isfile
import time
from os.path import join
from traceback import print_exception
from queue import Queue
import pefile
from logzero import logger
from tqdm import tqdm
import json

from utils.generic import mkdir

class ExtractPE(object):

    def __init__(self, outdir):
        
        self._date = time.time()
        # temporary filename
        self.outfile = join(outdir, "dll-export.json")


        self.dataset = []

    def __enter__(self):
        return self

    def check_cache(self):
        return isfile(self.outfile)
    
    def load_cache(self):
        # Opening JSON file
        with open(self.outfile) as json_file:
            return json.load(json_file)


    def __exit__(self, exc_type, exc_value, tb):
        self.dataset = None

        if exc_type is not None:
            print_exception(exc_type, exc_value, tb)
            return False # uncomment to pass exception through
        return True

    def list_exports(self, files):
        # l = glob.glob('c:\\windows\\system32\\*.dll')
        data = []

        for file in tqdm(files):
            try:
                # Parse file
                pe = pefile.PE(file)
                # Get Entry export directories
                d = [pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"]]

                # Parse Entry export directories
                pe.parse_data_directories(directories=d)

                # For Entry export directories symbol
                exports = []
                for symbol in pe.DIRECTORY_ENTRY_EXPORT.symbols:
                    if symbol.name:
                        name = symbol.name.decode('utf-8')
                        # if "@" in name or name.startswith("_"):
                        #     continue
                        # Add typle to list
                        exports.append((name,symbol.ordinal))

                data.append(dict(file=file,exports=exports))
            except Exception as e:
                logger.debug(e)

        json.dump(data, open(self.outfile, 'w+'))
        return data