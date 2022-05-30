from os.path import join
from logzero import INFO

class Settings():
    AUTHOR = "Vincent Denneman"
    VERSION = "0.1.0"
    LICENSE = "BSD-3"  

    LOG_DIR = "logs"
    LOG_FILENAME = "debug.log"
    LOG_FILE = join(LOG_DIR, LOG_FILENAME)
    LOG_MAX_BYTES = 1000000 # 1MB
    LOG_BACKUP_COUNT = 3
    LOG_LEVEL = INFO
    
    OUTPUT_DIR = "out"
    DEBUG_MODE = False

    PROCMON_TEMPLATE = join("template", "template.pmc")
    DEFAULT_PROCMON_LOG_OUTFILE = "C:\\Users\\Public\\Downloads\\log.pml"
    PROCMON_BIN = "bin\\Procmon.exe"
    CYGWIN64_BIN = "C:\\cygwin64\\bin\\x86_64-w64-mingw32-gcc.exe"

    SKIP_LIST = ["shutdown","logoff","lsaiso","rdpinit","wininit", "reboot", "sysprep"]
