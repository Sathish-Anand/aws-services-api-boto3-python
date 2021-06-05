import os
import shutil
from pathlib import Path

def roundoff(x, decimalpoints=1):
    try:
        return round(float(x), decimalpoints)
    except Exception:
        return x

def switch_workspace(folder):
    current_dir = os.getcwd()
    dirpath = Path(current_dir, folder)
    if dirpath.exists() and dirpath.is_dir():
        shutil.rmtree(str(dirpath))
    os.makedirs(str(folder))
    os.chdir(str(dirpath))
    return current_dir

def switch_back(dir):
    os.chdir(str(dir))