import os
import sys
import atexit
from config import LOCK_FILE

def create_lock():
    if os.path.exists(LOCK_FILE):
        print("すでに起動しています。終了します。")
        sys.exit(1)
    with open(LOCK_FILE, 'w') as f:
        f.write(str(os.getpid()))
    atexit.register(remove_lock)

def remove_lock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)
