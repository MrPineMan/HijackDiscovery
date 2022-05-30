import time
from watchdog.observers import Observer
from watchdog.events import RegexMatchingEventHandler

from logzero import logger
from traceback import print_exception

class FileWatcher:
    def __init__(self, fullpath):
        logger.debug("Initalizing Class FileWatcher ")
        self.fullpath = fullpath

        self.go_recursively = True
        self.event_observer = Observer()

        self.regex = [r"^.*\.(exe|dll|vbs|wsf|bat|ps1|EXE|DLL|VBS|WSF|BAT|PS1)$"]
        self.ignore_regex = []
        self.case_sensitive = True
        self.ignore_directories = False
        self.event_handler = RegexMatchingEventHandler(self.regex,
                                                self.ignore_regex,
                                                self.ignore_directories,
                                                self.case_sensitive)

        self.dataset = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.dataset = None

        if exc_type is not None:
            print_exception(exc_type, exc_value, tb)
            return False # uncomment to pass exception through
        return True

    def __str__(self):
        return self.dataset

    def log_event(self, event):
        self.dataset.append({"event_type" : event.event_type, "fullpath": event.src_path, "is_directory": event.is_directory})
        logger.info(f"The {event.src_path} is {event.event_type}")


    def run(self):
        self.start() 
        logger.info(f"Monitoring: {self.fullpath}")
        logger.info(f"Press CTRL+C once to stop monitoring file changes")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

    def start(self):
        self.schedule()
        
        self.event_handler.on_created = self.log_event
        # self.event_handler.on_deleted = self.log_event
        # self.event_handler.on_modified = self.log_event
        # self.event_handler.on_moved = self.log_event
        self.event_observer.start()

    def stop(self):
        self.event_observer.stop()
        self.event_observer.join()

    def schedule(self):
            self.event_observer.schedule(
            self.event_handler,
            self.fullpath,
            recursive=self.go_recursively
        )