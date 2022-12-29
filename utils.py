import os
import time
import shutil
import glob

from send2trash import send2trash


def get_splitter():
    if os.name == 'nt':
        return '\\'
    return '/'

def coerce(value, default):
    if value:
        return value
    return default

splitter = get_splitter()

def try_else_none(function):
    def wrapped_function(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except:
            return None
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
    } for i in glob.glob(path)]
    return file_info

def map_all_dirs(parent, current_depth=0, max_depth=3):
    # if we've hit bottom depth, we'll return empty list
    if current_depth > max_depth:
        return []
    # otherwise, let's add all children to the list
    # and then return it
    new_dirs = [i['path'] for i in files(parent) if i['type'] == 'directory']
    # then add recursive steps
    to_recur = new_dirs.copy()
    for i in to_recur:
        new_dirs += map_all_dirs(i, current_depth+1, max_depth)
    return new_dirs

directory_map = map_all_dirs('/home')
def goto(path='.'):
    if isinstance(path, dict):
        path = path['path']
    try:
        os.chdir(path)
    except:
        match = [i for i in directory_map if i.rsplit(splitter, 1)[-1] == path.rsplit(splitter, 1)[-1]]
        assert len(match) > 0, 'No matching directory found'
        os.chdir(match[0])


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
