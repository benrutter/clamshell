import subprocess
import os
import pandas as pd
import glob
import sys
import time
import traceback
from pygments.lexers.python import PythonLexer
from rich import print
from prompt_toolkit import prompt, print_formatted_text, PromptSession
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from rich.console import Console
from prompt_toolkit.output.color_depth import ColorDepth

from .utils import *
from .key_bindings import key_bindings

def capture_and_return_exception(function):
    def new_function(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as exception:
            return f'[red bold] ! >> {str(repr(exception))}[/red bold]'
    return new_function

class ClamShell:
    def __init__(self, super_commands: list = None, aliases: dict = None, get_prompt = get_prompt, get_continuation_prompt=get_continuation_prompt):
        self.console = Console(color_system='auto')
        self.super_commands = coerce(super_commands, [])
        self.aliases = coerce(aliases, [])
        self.lexer = PygmentsLexer(PythonLexer)
        self.globals = globals()
        self.locals = locals()
        self.session = PromptSession()
        self.key_bindings = key_bindings
        self.run_repl = True
        self.get_prompt = get_prompt
        self.get_continuation_prompt = get_continuation_prompt


    def is_uncompleted(self, string):
        completion_dict = {
            '(': ')',
            '{': '}',
            '[': ']',
            '"': '"',
            "'": "'",
        }
        last = None
        for char in string:
            if last is not None:
                if char == completion_dict[last]:
                    last = None
            elif char in list(completion_dict.keys()):
                last = char
        return last is not None

    def with_quotes_if_undefined(self, string):
        try:
            eval(string, self.globals, self.locals)
            return string
        except:
            return f'"{string}"'

    def flatten_list(self, list_of_lists):
        return [item for sublist in list_of_lists for item in sublist]

    def sandwich_split(self, string, splitters=[' ', '"', "'"]):
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

    def break_into_pieces(self, string):
        pieces = self.sandwich_split(string)
        pieces = [i.strip() for i in pieces]
        pieces = [i for i in pieces if i != '']
        return pieces

    def reform(self, pieces):
        remade = f'{pieces[0]}({", ".join(pieces[1:])})'
        return remade

    @capture_and_return_exception
    def python_exec(self, command: str):
        try:
            return eval(command, self.globals, self.locals)
        except SyntaxError:
            return exec(command, self.globals, self.locals)

    def clam_compile(self, command:str):
        pieces = self.break_into_pieces(command)
        pieces = [pieces[0]] + [self.with_quotes_if_undefined(i) for i in pieces[1:]]
        reformed = self.reform(pieces)
        return reformed

    @capture_and_return_exception
    def clam_exec(self, command: str):
        reformed = self.clam_compile(command)
        try:
            return self.python_exec(reformed)
        except Exceptions as e:
            return str(repr(e))

    @capture_and_return_exception
    def shell_exec(self, command: str):
        for key, value in self.aliases.items():
            if command[:len(key)] == key:
                command = value + command[len(value)-1:]
                break
        pieces = self.break_into_pieces(command)
        output = subprocess.call(pieces)
        output = f'\n[italic]output: {output}[/italic]'

    @capture_and_return_exception
    def super_exec(self, command: str):
        assert len(command.strip().split(' ')) == 1
        command += '()'
        return self.python_exec(command)

    def print_output(self, output):
        if isinstance(output, list) and isinstance(output[0], dict) and output[0].get('path') is not None:
            try:
                df = pd.DataFrame(output)
                self.console.print(df)
                return
            except:
                pass
        self.console.print(output)

    def compiles_without_errors(self, command):
        try:
            compile(command, '<string>', mode='exec')
            return True
        except SyntaxError:
            return False

    def meta_exec(self, command):
        # rule is, will it compile as python or clam?
        # if it works as one, run
        # if that throws a name error, then
        # execute as subprocess
        if command in self.super_commands:
            return self.super_exec(command)
        elif self.compiles_without_errors(command):
            result = self.python_exec(command)
        elif self.compiles_without_errors(self.clam_compile(command)):
            result = self.clam_exec(command)
        else:
            result = self.shell_exec(command)
        if isinstance(result, str) and result.startswith('[red bold] ! >> NameError('):
            python_result = result
            result = self.shell_exec(command)
            if isinstance(result, str) and result.startswith('[red bold] ! >> FileNotFoundError('):
                result = python_result
        return result

    @capture_and_return_exception
    def repl(self):
        command = self.prompt()
        result = self.meta_exec(command)
        if result is not None:
            self.print_output(result)

    def prompt(self):
        command = self.session.prompt(
            self.get_prompt(),
            lexer=self.lexer,
            auto_suggest=AutoSuggestFromHistory(),
            key_bindings=self.key_bindings,
            color_depth=ColorDepth.ANSI_COLORS_ONLY
        )
        if command != '' and (command[-1] == ':' or self.is_uncompleted(command)):
            new_line = None
            while new_line != '':
                new_line = self.session.prompt(
                    self.get_continuation_prompt(),
                    lexer=self.lexer,
                    auto_suggest=AutoSuggestFromHistory(),
                    key_bindings=self.key_bindings,
                    color_depth=ColorDepth.ANSI_COLORS_ONLY
                )
                command += f'\n{new_line}'
        return command

    def exit(self):
        self.run_repl = False


