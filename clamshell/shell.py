import subprocess
import os
import threading
from collections import defaultdict
from typing import Callable, List, Dict, Type

from pygments.lexers.python import PythonLexer
from rich.table import Table
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit import prompt, PromptSession
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import FileHistory
from rich import print
from prompt_toolkit.output.color_depth import ColorDepth

from . import meta_functions, defaults, shell_utils
from .key_bindings import key_bindings
from .types import FileList


class ClamShell:
    """
    Class handles environment, and running of commands given in shell.
    """

    def __init__(
        self,
        super_commands: list = None,
        aliases: Dict[str, str] = None,
        get_prompt: callable = defaults.get_prompt,
        get_continuation_prompt: callable = defaults.get_continuation_prompt,
        shell_globals: dict = None,
        shell_locals: dict = None,
    ):
        self.super_commands: List[str] = meta_functions.coerce(super_commands, [])
        self.aliases: Dict[str, str] = meta_functions.coerce(aliases, [])
        self.lexer: PygmentsLexer = PygmentsLexer(PythonLexer)
        self.globals: dict = meta_functions.coerce(shell_globals, globals())
        self.locals: list = meta_functions.coerce(shell_locals, locals())
        history_file: str = self.history_file()
        self.session: PromptSession = PromptSession(history=FileHistory(history_file))
        self.key_bindings: KeyBindings = key_bindings
        self.get_prompt: Callable = get_prompt
        self.get_continuation_prompt: Callable = get_continuation_prompt
        self.command: str = None
        self.output: Type = None

    def history_file(self) -> str:
        """
        Infers and returns location of history file
        """
        home: str = shell_utils.home
        splitter: str = shell_utils.splitter
        history_file: str = (
            f"{home}{splitter}.config{splitter}clamshell{splitter}history"
        )
        if not os.path.exists(history_file):
            shell_utils.make_file(history_file)
        return history_file

    def rc_file(self) -> str:
        """
        Infers and returns location of clamrc file
        """
        home: str = shell_utils.home
        splitter: str = shell_utils.splitter
        rc_file: str = f"{home}{splitter}.config{splitter}clamshell{splitter}clamrc.py"
        if not os.path.exists(rc_file):
            shell_utils.make_file(rc_file)
        return rc_file

    def is_uncompleted(self, command: str) -> bool:
        """
        Checks for unclosed brackets, speech marks etc,
        and returns bool based on them being present
        """
        completion_dict = {
            "(": ")",
            "{": "}",
            "[": "]",
            '"': '"',
            "'": "'",
        }
        last: str = None
        for char in command:
            if last is not None:
                if char == completion_dict[last]:
                    last: str = None
            elif char in list(completion_dict.keys()):
                last: str = char
        completed: bool = last is not None
        return completed

    def with_quotes_if_undefined(self, name: str) -> str:
        """
        Checks whether name is defined (if not, adds quotes around it)
        """
        try:
            eval(name, self.globals, self.locals)
            return name
        except:
            return f'"{name}"'

    def flatten_list(self, list_of_lists: List[list]) -> list:
        """
        Takes a list of list of values and returns list of values
        """
        return [item for sublist in list_of_lists for item in sublist]

    def sandwich_split(
        self, string, splitters: List[str] = [" ", '"', "'"]
    ) -> List[str]:
        """
        Splits items from start to end of splitter, without interception
        """
        split: str = splitters[0]
        segments: list = []
        accumulator: str = ""

        for char in string:
            if char == split:
                accumulator += char
                segments.append(accumulator)
                accumulator: str = ""
            elif accumulator == "" and char in splitters:
                accumulator += char
                split = char
            else:
                accumulator += char
        segments.append(accumulator)
        return segments

    def break_into_pieces(self, string: str) -> List[str]:
        """
        Breaks a string into individual pieces based on
        use of sandwich_split function
        """
        pieces: List[str] = self.sandwich_split(string)
        pieces = [i.strip() for i in pieces]
        pieces = [i for i in pieces if i != ""]
        return pieces

    def reform(self, pieces: List[str]) -> str:
        """
        Forms individual pieces into a function call based on
        clam syntax
        """
        remade = f'{pieces[0]}({", ".join(pieces[1:])})'
        return remade

    @meta_functions.capture_and_return_exception
    def python_exec(self, command: str) -> Type:
        """
        Executes as python (attempts evaluation first)
        """
        try:
            return eval(command, self.globals, self.locals)
        except SyntaxError:
            return exec(command, self.globals, self.locals)

    def clam_compile(self, command: str) -> str:
        """
        Converts a string into python executable based on clam syntax
        """
        pieces: List[str] = self.break_into_pieces(command)
        pieces = [pieces[0]] + [self.with_quotes_if_undefined(i) for i in pieces[1:]]
        reformed: str = self.reform(pieces)
        return reformed

    @meta_functions.capture_and_return_exception
    def clam_exec(self, command: str) -> Type:
        """
        Compiles based on clam syntax then executes as python
        """
        reformed: str = self.clam_compile(command)
        return self.python_exec(reformed)

    @meta_functions.capture_and_return_exception
    def shell_exec(self, command: str) -> str:
        for key, value in self.aliases.items():
            if command[: len(key)] == key:
                command = value + command[len(key) :]
                break
        pieces: List[str] = self.break_into_pieces(command)
        output: int = subprocess.call(pieces)
        output = f"\n[italic]output: {output}[/italic]"
        return output

    @meta_functions.capture_and_return_exception
    def super_exec(self, command: str) -> Type:
        """
        Takes command of function name and executes no argument call
        """
        assert len(command.strip().split(" ")) == 1
        command += "()"
        return self.python_exec(command)

    def print_output(self) -> None:
        """
        Custom print of output
        """
        if self.output is None:
            return
        if isinstance(self.output, FileList):
            table = Table()
            for i in self.output[0].keys():
                table.add_column(
                    i,
                    style=defaultdict(
                        lambda: "", {"name": "cyan", "path": "italic", "type": "green"}
                    )[i],
                )
            for i in self.output:
                table.add_row(*list(i.values()))
            print(table)
        else:
            print(self.output)

    def compiles_without_errors(self, command: str) -> bool:
        """
        Returns true if command string can compile to python without
        throwing a SyntaxError, otherwise false
        """
        try:
            compile(command, "<string>", mode="exec")
            return True
        except SyntaxError:
            return False

    @meta_functions.capture_and_return_exception
    def meta_exec(self) -> None:
        """
        Execution order for the self.command string, as follows:
            - If 'super self.command' will run as so
            - Otherwise, will see if it can compile to:
                - Python
                - Then "clam python"
                - (Will run as one of those if it can)
            - Will run as a subprocess if those conditions aren't met
            - (or if python running throws a name error)
        """
        if self.command in self.super_commands:
            result: Type = self.super_exec(self.command)
        elif self.compiles_without_errors(self.command):
            result: Type = self.python_exec(self.command)
        elif self.compiles_without_errors(self.clam_compile(self.command)):
            result: Type = self.clam_exec(self.command)
        else:
            result: Type = self.shell_exec(self.command)
        if isinstance(result, str) and result.startswith("[red bold] ! >> NameError("):
            python_result: Type = result
            result: Type = self.shell_exec(self.command)
            if isinstance(result, str) and result.startswith(
                "[red bold] ! >> FileNotFoundError("
            ):
                result = python_result
        self.output = result

    def repl(self) -> None:
        """
        Central read-evaluate-print loop
        """
        self.prompt()
        self.meta_exec()
        self.print_output()

    def initial_prompt(self) -> None:
        """
        Sets first prompt to self.command value
        """
        self.command = self.session.prompt(
            self.get_prompt(),
            lexer=self.lexer,
            auto_suggest=AutoSuggestFromHistory(),
            key_bindings=self.key_bindings,
            color_depth=ColorDepth.ANSI_COLORS_ONLY,
        )

    def continuation_prompt(self) -> None:
        """
        Uses continuation prompt to append to self.command
        """
        new_line: str = None
        while new_line != "":
            new_line = self.session.prompt(
                self.get_continuation_prompt(),
                lexer=self.lexer,
                auto_suggest=AutoSuggestFromHistory(),
                key_bindings=self.key_bindings,
                color_depth=ColorDepth.ANSI_COLORS_ONLY,
            )
            self.command += f"\n{new_line}"

    def prompt(self) -> None:
        """
        Runs inital_prompt and continuation_prompt in own thread
        (so that async of prompt doesn't affect anything ran)
        """
        th: threading.Thread = threading.Thread(target=self.initial_prompt)
        th.start()
        th.join()
        if self.command != "" and (
            self.command[-1] == ":" or self.is_uncompleted(self.command)
        ):
            th: threading.Thread = threading.Thread(target=self.continuation_prompt)
            th.start()
            th.join()
