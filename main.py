#!/usr/bin/env python

"""
Module Docstring
"""

from http.server import executable
from importlib.resources import path
from os import makedirs
from os.path import basename, isfile, join
from re import sub
from shutil import copyfile

from logzero import DEBUG, logfile, logger, loglevel
from pandas import DataFrame
from core.compile import Compile
from utils.generic import to_text_file
from tqdm import tqdm

from config import settings
from core.monitor import FileWatcher
from core.pe import ExtractPE
from core.pmc import Procmon
from core.strings import Strings
from utils.argparse import argument_parser
from utils.datasets import Dataset
from utils.generic import (list_to_file, mkdir, path_to_file, to_df_csv,
                           uniquify, search_extensions)

import pandas as pd
import operator

logfile(settings.LOG_FILE, maxBytes=settings.LOG_MAX_BYTES, backupCount=settings.LOG_BACKUP_COUNT)
loglevel(settings.LOG_LEVEL)

logger.info(f"Log are stored in: {settings.LOG_FILE}")

def setup():
    args = argument_parser()
    if args.debug or settings.DEBUG_MODE:
        settings.DEBUG_MODE = True
        loglevel(DEBUG)
        logger.debug("Logger set to DEBUG")

    # Make an unique output dir to prevent overwriting previous monitors
    app_outdir = mkdir(join(settings.OUTPUT_DIR, args.appname))

    if args.command == "monitor":
        logger.info("Entering monitor mode")
        with FileWatcher(args.directory) as fw:
            fw.run()
            csvfile = to_df_csv(fw.__str__(), outdir, "raw_monitoring_data")

        with Dataset(csvfile) as ds:
            ds.overview()
            ds.dedupe_and_sort(key="fullpath")
            ext_dict = ds.export_extension_lists(outdir)

    elif args.command == "analyse":
        logger.info("Entering analyse mode")
        # for ext, fullpaths in ext_dict.items():
        # if ext.lower() == "exe":

        logger.warning(f"Press CTRL+C to stop")
        # install_dir = "C:\\Program Files (x86)\\Microsoft Office\\"
        install_dir = args.installdir
        findings = []
        try: 
            # Do this action ones at the very end (It take dayysssss)        
            with ExtractPE(app_outdir) as ePE:
                if ePE.check_cache():
                    logger.debug("Loading exports from cache")
                    dll_entries = ePE.load_cache()
                else: 
                    subfolders, libraries = search_extensions(install_dir, [".dll"])
                    logger.info(f"Found {len(libraries)} libraries in installation directory {install_dir}")
                    logger.info("Retrieving all export entries, this might take a while...")
                    dll_entries = ePE.list_exports(list(libraries))

            _, executables = search_extensions(install_dir, [".exe"])
            logger.info(f"Found {len(executables)} executables in installation directory {install_dir}")
            logger.info(
f"""
Automated steps to discover potential DLL hijacks. Testing {len(executables)} items!!
    1) Validate file 
    2) Generate Procmon filter
    3) Copy the file to a temporary folder.
    4) Open Procmon and apply the customized filter.
    5) Run the applications.
    6) Close Procmon and save the results.
""")

            
            for target in executables:

                summary = {}
                # Executable filename.
                filename = path_to_file(target)

                if not isfile(target):
                    logger.warning(f"Skip: {target}")
                    continue
                if any(xs in target for xs in settings.SKIP_LIST):
                    logger.warning(f"Skip: {target}")
                    continue

                summary_outfile = join(app_outdir, filename, "summary.csv")
                if isfile(summary_outfile):
                    continue

                # Executable custom outdir
                outdir = mkdir(uniquify(join(app_outdir, filename)))

                # Full path name of executable in custom outdir 
                tmp_executable = join(outdir, filename)
                try:
                    copyfile(target, tmp_executable)
                except PermissionError:
                    continue

                summary.update(file=target)
                
                # with Strings(outdir) as strings:
                    # summary.update(autoElevate=strings.find_elevated(target))   
                    # summary.update(autoElevate=False)

                with Procmon(outdir) as pm:                
                    # Generate Procmon Filter
                    filter = pm.generate_filter(tmp_executable)

                    # The (filtered) CSV file with loaded DLL's in current directory 
                    procmon_output, df = pm.run(tmp_executable, filter)
                    
                    # Storing DLL paths located in the installation folder
                    matching_files = []
                    # Load CSV file containing the unloaded DLL's
                    # df = pd.read_csv(procmon_output)
                    # List all missing DLL's
                    missing_dlls  = [path_to_file(path.lower()) for path in df.Path.tolist()]
                    summary.update(potentials=df.Path.tolist())
                    
                    # Match missing DLL's with a existing DLL located in the Install directory (based on name)
                    for dll in dll_entries:
                        low_fname = path_to_file(dll["file"].lower())
                        # The DLL is relevant as it is missing by the executables
                        if low_fname in missing_dlls:
                            # Do not add the same DLL twice if it is located in different directories.
                            get_value = operator.itemgetter('file')
                            files = map(get_value, matching_files)
                            if not low_fname in '\t'.join(list(files)):
                                # Add if not listed yet
                                matching_files.append(dll)

                    summary.update(matches=matching_files)

                with Compile(outdir) as cp:
                    # Store the potential successes
                    potential_hijacks = []

                    # variables stores 3 this
                    # file: DLL fullpath and a tuple (dll export function, ordinal)
                    for variables in matching_files:
                        # Creating C code file and def code file with jinja2
                        c_file, def_file = cp.setup(variables)
                        # Compile time! Returns a filename is DLL is created without errors, None is failed
                        compiled_dll = cp.build(variables["file"], c_file, def_file)
                        # Only append successfull builds ;-)
                        if compiled_dll != None: 
                            potential_hijacks.append(compiled_dll)

                        # logger.info(f"{len(potential_hijacks)} potential DLL hijack is discovered {path_to_file(target)} : {potential_hijacks}")
                    summary.update(hijacks=potential_hijacks)
                    to_text_file(summary, summary_outfile)

                findings.append(summary)

        except KeyboardInterrupt:
            pass

        DataFrame.from_dict(findings, orient="index").to_csv(join(outdir, "results.txt"))
        to_text_file(join(outdir, "results.txt"), findings)
    # if ext.lower() != 'dll' and ext.lower() != 'exe':
    #    app_outdir = mkdir(join(outdir, ext))
    #    fname = join(app_outdir, ext)
    #    list_to_file(fullpaths, fname)
    else:
        logger.warning("Required command not found, check --help for more info.")
    
if __name__ == "__main__":
    try:
        setup()
    except KeyboardInterrupt:
        logger.exception("Keyboard interrupt")
        pass
    logger.info(f"Exit gracefully")    
