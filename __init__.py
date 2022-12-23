import os
import pandas as pd
import glob
import time
from rich import print
from IPython.terminal.prompts import Prompts, Token

if os.name == 'nt':
    SPLITTER = '\\'
else:
    SPLITTER = '/'
class MyPrompt(Prompts):
    def in_prompt_tokens(self, cli=None):
        return [(Token.Prompt, get_prompt(),)]


def try_to(function):
    def wrapped_function(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except:
            return None
    return wrapped_function

@try_to
def created_datetime(file):
    created = os.path.getctime(file)
    created = time.ctime(created)
    return created

@try_to
def modified_datetime(file):
    modified = os.path.getmtime(file)
    modified = time.ctime(modified)
    return modified

def get_type(file):
    if os.path.isfile(file):
        return 'file'
    else:
        return 'directory'

def files(path=None, recursive=False):
    cwd = os.getcwd()
    if path is None:
        path = '**'
    elif path[-1] == SPLITTER:
        path += '**'
    elif path [-1] != '*':
        path += f'{SPLITTER}**'
    file_info = [{
        'name': i,
        'path': f'{cwd}{SPLITTER}{i}',
        'created': created_datetime(i),
        'modified': modified_datetime(i),
        'type': get_type(i),
    } for i in glob.glob(path)]
    return file_info

def goto(path='.'):
    if isinstance(path, dict):
        os.chdir(path['path'])
        return
    os.chdir(path)

def get_prompt():
    cwd = os.getcwd()
    return f" 🐍 {cwd} $ "

ip = get_ipython()
ip.prompts = MyPrompt(ip)

print('𝒔𝒏𝒆𝒌𝒔𝒉𝒆𝒍𝒍')
