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

from utils import *
from key_bindings import key_bindings


class ClamShell:
    def __init__(self, super_commands: list = None, aliases: dict = None):
        self.console = Console(color_system='auto')
        self.super_commands = coerce(super_commands, [])
        self.aliases = coerce(aliases, [])
        self.lexer = PygmentsLexer(PythonLexer)
        self.globals = globals()
        self.locals = locals()
        self.session = PromptSession()
        self.key_bindings = key_bindings


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

    def sandwich_split(self, string, splitters):
        split = None
        segments = []
        accumulator = ''
        for char in string:
            if char == split:
                segments.append(accumulator)
                accumulator = ''
            elif char in splitters:
                segments.append(accumulator)
                split = char
                accumulator = ''
            else:
                accumulator += char
        segments.append(accumulator)
        return segments

    def break_into_pieces(self, string):
        pieces = self.sandwich_split(string, ['"', "'", ' '])
        pieces = [i.strip() for i in pieces]
        pieces = [i for i in pieces if i != '']
        return pieces

    def reform(self, pieces):
        remade = f'{pieces[0]}({", ".join(pieces[1:])})'
        return remade

    def python_exec(self, command: str):
        try:
            output = eval(command, self.globals, self.locals)
            return output
        except:
            return exec(command, self.globals, self.locals)

    def clam_exec(self, command: str):
        pieces = self.break_into_pieces(command)
        pieces = [self.with_quotes_if_undefined(i) for i in pieces]
        reformed = self.reform(pieces)
        assert reformed[0] not in ['"', "'"]
        return self.python_exec(reformed)

    def shell_exec(self, command: str):
        for key, value in self.aliases.items():
            if command[:len(key)] == key:
                command = value + command[len(value)-1:]
                break
        pieces = self.break_into_pieces(command)
        output = subprocess.call(pieces)
        output = f'\n[italic]output: {output}[/italic]'
        return output

    def super_exec(self, command: str):
        assert len(command.strip().split(' ')) == 1
        command += '()'
        return self.python_exec(command)

    def try_except_chain(self, try_list: list, first_exception=None):
        """
        try except for everything in list,
        list must be series of no_argument functions
        capture and return first exception if no pass
        """
        if len(try_list) == 0:
            return first_exception
        to_try = try_list[0]
        try:
            return to_try()
        except Exception as e:
            if first_exception is None:
                first_exception = '[red bold] ! >> [/red bold]' + str(repr(e))
            return self.try_except_chain(try_list[1:], first_exception)

    def print_output(self, output):
        if isinstance(output, list) and isinstance(output[0], dict) and output[0].get('path') is not None:
            try:
                df = pd.DataFrame(output)
                self.console.print(df)
                return
            except:
                pass
        self.console.print(output)

    def repl_loop(self):

        from prompt_toolkit.output.color_depth import ColorDepth
        command = self.session.prompt(
            get_prompt(),
            lexer=self.lexer,
            auto_suggest=AutoSuggestFromHistory(),
            key_bindings=self.key_bindings,
            color_depth=ColorDepth.ANSI_COLORS_ONLY
        )
        if command != '' and (command[-1] == ':' or self.is_uncompleted(command)):
            new_line = None
            while new_line != '':
                new_line = self.session.prompt(
                    get_continuation_prompt(),
                    lexer=self.lexer,
                    auto_suggest=AutoSuggestFromHistory(),
                    key_bindings=self.key_bindings,
                    color_depth=ColorDepth.ANSI_COLORS_ONLY
                )
                command += f'\n{new_line}'

        if command in self.super_commands:
            result = self.super_exec(command)
        else:
            result = self.try_except_chain([
                lambda: self.python_exec(command),
                lambda: self.clam_exec(command),
                lambda: self.shell_exec(command),
            ])
        if result is not None:
            self.print_output(result)

# making callable function
app = ClamShell(['files', 'exit'], {'python': 'python3'})

while True:
    app.repl_loop()
