import os
import sys
import atexit
from updater.config import LOCK_FILE

def create_lock():
    if os.path.exists(LOCK_FILE):
        print("The application is already running. Exiting.")
        sys.exit(1)
    with open(LOCK_FILE, 'w') as f:
        f.write(str(os.getpid()))
    atexit.register(remove_lock)

def remove_lock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)
