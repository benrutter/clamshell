import os
import sys
import subprocess
import time
import shutil
import glob

from send2trash import send2trash


def get_splitter():
    if os.name == 'nt':
        return '\\'
    return '/'

def get_home():
    if os.name == 'nt':
        return os.environ['USERPROFILE']
    else:
        return '/home'


splitter = get_splitter()
home = get_home()
original_path = sys.path.copy()

def coerce(value, default):
    if value:
        return value
    return default

def try_else_none(function):
    def wrapped_function(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except:
            return None
    return wrapped_function

def try_else_empty_list(function):
    def wrapped_function(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except:
            return []
    return wrapped_function

@try_else_none
def get_created_datetime(file):
    created = os.path.getctime(file)
    created = time.ctime(created)
    return created

@try_else_none
def get_modified_datetime(file):
    modified = os.path.getmtime(file)
    modified = time.ctime(modified)
    return modified

@try_else_none
def get_type(file):
    if os.path.isfile(file):
        return 'file'
    else:
        return 'directory'

def files(path=None, recursive=False):
    if path is None:
        path = '**'
    elif path[-1] == splitter:
        path += '**'
    elif path [-1] != '*':
        path += f'{splitter}**'
    file_info = [{
        'name': i,
        'path': os.path.abspath(i),
        'created': get_created_datetime(i),
        'modified': get_modified_datetime(i),
        'type': get_type(i),
    } for i in glob.glob(path, recursive=recursive)]
    return file_info

def map_all_dirs(parent, current_depth=0, max_depth=2):
    # if we've hit bottom depth, we'll return empty list
    if current_depth > max_depth:
        return []
    # otherwise, let's add all children to the list
    # and then return it
    new_dirs = [i['path'] for i in files(parent) if i['type'] == 'directory']
    # lets get rid of windows non-dot "AppData" which will map too many things
    new_dirs = [i for i in new_dirs if 'AppData' not in i]
    # then add recursive steps
    to_recur = new_dirs.copy()
    for i in to_recur:
        new_dirs += map_all_dirs(i, current_depth+1, max_depth)
    return new_dirs

directory_map = map_all_dirs(home)

def goto(path='.'):
    old_location = os.getcwd()
    if isinstance(path, dict):
        path = path['path']
    try:
        os.chdir(path)
    except:
        match = [i for i in directory_map if i.endswith(path)]
        assert len(match) > 0, 'No matching directory found'
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
        path = path['path']
    send2trash(path)
    return f'[green]{path} sent to recycle bin[/green]'

def move(source: str, destination: str):
    if isinstance(source, dict):
        source = source['path']
    shutil.move(source, destination)
    return f'[green]{source} moved to {destination}[/green]'

def copy(source: str, destination: str):
    if isinstance(source, dict):
        source = source['path']
    shutil.copy(source, destination)
    return 'f[green]{source} copied to {destination}[/green]'

def read(source: str):
    if isinstance(source, dict):
        source = source['path']
    with open(source, 'r') as file:
        output = file.read()
    return output

def make_file(path: str):
    with open(path, 'w'):
        pass
    return f'[green]{path} created[/green]'

def make_directory(path: str):
    os.makedirs(path, exist_ok=False)
    return f'[green]{path} created[/green]'

def get_prompt():
    cwd = os.getcwd()
    return f" 🐚 {cwd} $ "

def get_continuation_prompt():
    return " ... "


def sandwich_split(string, splitters=[' ', '"', "'"]):
    split = splitters[0]
    segments = []
    accumulator = ''
    for char in string:
        # if the char is out current split
        # then this accumulator is over
        if char == split:
            accumulator += char
            segments.append(accumulator)
            accumulator = ''
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
    pieces = [i for i in pieces if i != '']
    return pieces

def run(command: str):
    pieces = break_into_pieces(command)
    proc = subprocess.Popen(pieces, stdout=subprocess.PIPE)
    return proc.communicate()[0].decode()

@try_else_empty_list
def file_line_matches(search_string: str, file_to_search: dict):
    matches = []
    with open(file_to_search['path'], 'r') as match:
        lines = match.readlines()
    for i, line in enumerate(lines):
        if search_string in line:
            matches.append({
                'name': file_to_search['name'],
                'path': file_to_search['path'],
                'line_number': i,
                'line': line,
            })
    return matches

def search(search_string: str, path: str = None, recursive=False):
    files_to_search = files(path, recursive)
    files_to_search = [i for i in files_to_search if i['type'] == 'file']
    matches = []
    for file_to_search in files_to_search:
        matches += file_line_matches(search_string, file_to_search)
    return matches

