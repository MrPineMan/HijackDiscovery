import argparse
from config import settings
from utils.generic import is_valid_folder 

def argument_parser():
    """ This is executed when run from the command line """
    # top-level parser
    parser = argparse.ArgumentParser(description="Tool to discover new LOLbins/BYOLbins (faster)")
    parser.add_argument("-v", "--version", action="version", 
                    version=f"%(prog)s (version {settings.VERSION})")
    parser.add_argument("-d", "--debug", dest="debug", action="store_true", default=False)
    parser.add_argument("-a", "--appname", dest="appname", required=True, 
                    help="Friendly name of the target application")
                    
    subparsers = parser.add_subparsers(help="help for subcommand", dest="command")

    # create the parser for the "monitor" command
    monitor = subparsers.add_parser("monitor", help="Monitor created/modified/removed DLL/EXE file(s)")
    monitor.add_argument("--directory", dest="directory", required=True, 
                    help="Directory to monitor (including subfolders)")


    # create the parser for the "analyse" command
    analyse = subparsers.add_parser("analyse", help="Analyse DLL/EXE file(s)")
    analyse.add_argument("--installdir", dest="installdir", required=True,
                    help="Install dir", 
                    type=lambda x: is_valid_folder(parser, x))

    return parser.parse_args()
