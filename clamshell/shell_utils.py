import os
import sys
import subprocess
import time
import shutil
import glob
from typing import List

from send2trash import send2trash

from . import meta_functions
from .types import FileList


def is_windows() -> bool:
    """
    Returns true if os is windows (otherwise false)
    """
    return os.name == "nt"


def get_splitter() -> str:
    """
    Returns character used to split path on operating system
    """
    if is_windows():
        return "\\"
    return "/"


def get_home():
    """
    Returns users home directory
    """
    if is_windows():
        return os.environ["USERPROFILE"]
    return f'/home/{os.environ["USER"]}'


def get_clear_command():
    """
    Returns command called to clear screen (cls/clear)
    """
    if is_windows():
        return "cls"
    return "clear"


@meta_functions.try_else_none
def get_created_datetime(file):
    created = os.path.getctime(file)
    created = time.ctime(created)
    return created


@meta_functions.try_else_none
def get_modified_datetime(file):
    modified = os.path.getmtime(file)
    modified = time.ctime(modified)
    return modified


@meta_functions.try_else_none
def get_type(file):
    if os.path.isfile(file):
        return "file"
    else:
        return "directory"

@meta_functions.try_else_none
def file_metadata(path):
    return {
        "name": path,
        "path": os.path.abspath(path),
        "created": get_created_datetime(path),
        "modified": get_modified_datetime(path),
        "type": get_type(path),
    }

def files(path=None, hidden=False, recursive=0):
    file_info = [file_metadata(i) for i in os.listdir(path)]
    file_info = [i for i in file_info if i is not None]
    if not hidden:
        file_info = [i for i in file_info if not i['name'].startswith('.')]
    file_info = FileList(file_info)
    if recursive == 0:
        return file_info
    for folder in [i['path'] for i in file_info if i['type'] == 'folder']:
        try:
            file_info += FileList(files(folder, recursive-1))
        except:
            pass
    return file_info


def clear():
    os.system(clear_command)


def goto(path="."):
    old_location = os.getcwd()
    if isinstance(path, dict):
        path = path["path"]
    try:
        os.chdir(path)
    except:
        match = [i for i in directory_map if i.endswith(path)]
        assert len(match) > 0, "No matching directory found"
        os.chdir(match[0])
    # now let's add the current directory to the path
    # and remove the previous one
    new_location = os.getcwd()
    if new_location not in sys.path:
        sys.path.append(new_location)
    if old_location not in original_path and old_location in sys.path:
        sys.path.remove(old_location)


def delete(path: str):
    if isinstance(path, dict):
        path = path["path"]
    send2trash(path)
    return f"[green]{path} sent to recycle bin[/green]"


def move(source: str, destination: str):
    if isinstance(source, dict):
        source = source["path"]
    shutil.move(source, destination)
    return f"[green]{source} moved to {destination}[/green]"


def copy(source: str, destination: str):
    if isinstance(source, dict):
        source = source["path"]
    shutil.copy(source, destination)
    return "f[green]{source} copied to {destination}[/green]"


def read(source: str):
    if isinstance(source, dict):
        source = source["path"]
    with open(source, "r") as file:
        output = file.read()
    return output


def make_file(path: str):
    split_path = path.rsplit(splitter, 1)
    if len(split_path) > 1:
        os.makedirs(split_path[0], exist_ok=True)
    with open(path, "w"):
        pass
    return f"[green]{path} created[/green]"


def make_directory(path: str):
    os.makedirs(path, exist_ok=False)
    return f"[green]{path} created[/green]"


def sandwich_split(string, splitters=[" ", '"', "'"]):
    split = splitters[0]
    segments = []
    accumulator = ""
    for char in string:
        # if the char is out current split
        # then this accumulator is over
        if char == split:
            accumulator += char
            segments.append(accumulator)
            accumulator = ""
        # otherwise, if the char is a splitter
        # then
        elif char in splitters:
            split = char
            accumulator += char
        else:
            accumulator += char
    segments.append(accumulator)
    return segments


def break_into_pieces(string):
    pieces = sandwich_split(string)
    pieces = [i.strip() for i in pieces]
    pieces = [i for i in pieces if i != ""]
    return pieces


def run(command: str):
    pieces = break_into_pieces(command)
    proc = subprocess.Popen(pieces, stdout=subprocess.PIPE)
    return proc.communicate()[0].decode()


@meta_functions.try_else_empty_list
def file_line_matches(search_string: str, file_to_search: dict):
    matches = FileList()
    with open(file_to_search["path"], "r") as match:
        lines = match.readlines()
    for i, line in enumerate(lines):
        if search_string in line:
            matches.append(
                {
                    "name": file_to_search["name"],
                    "path": file_to_search["path"],
                    "line_number": i,
                    "line": line,
                }
            )
    return matches


def search(search_string: str, path: str = None, recursive=False):
    files_to_search = files(path, recursive)
    files_to_search = [i for i in files_to_search if i["type"] == "file"]
    matches = []
    for file_to_search in files_to_search:
        matches += file_line_matches(search_string, file_to_search)
    return matches


def pipe(*args):
    result = args[0]
    for call in args[1:]:
        result = call(result)
    return result

def map_all_dirs(parent: str, current_depth: int = 0, max_depth: int = 2) -> List[str]:
    initial_dir = os.getcwd()
    os.chdir(parent)
    # if we've hit bottom depth, we'll return empty list
    if current_depth > max_depth:
        return []
    # otherwise, let's add all children to the list
    # and then return it
    new_dirs: List[str] = [i['path'] for i in files(parent) if i["type"] == "directory"]
    # we'll add home if this is the first run
    if current_depth == 0:
        new_dirs.append(parent)
    # lets get rid of windows non-dot "AppData" which will map too many things
    if is_windows():
        new_dirs = [i for i in new_dirs if "AppData" not in i]
    # then add recursive steps
    to_recur: List[str] = new_dirs.copy()
    for i in to_recur:
        try:
            new_dirs += map_all_dirs(i, current_depth + 1, max_depth)
        except:
            pass
    os.chdir(initial_dir)
    new_dirs = [i for i in new_dirs if i is not None]
    return new_dirs


splitter: str = get_splitter()
home: str = get_home()
original_path: str = sys.path.copy()
clear_command: str = get_clear_command()
directory_map: List[str] = map_all_dirs(home)


def coerce(value, default):
    if value:
        return value
    return default
