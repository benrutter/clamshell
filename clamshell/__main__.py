from os import environ

from .shell import ClamShell
from .utils import files, delete, search, copy, move, goto, read, make_file, make_directory, get_prompt, get_continuation_prompt, run

# making callable function
clamshell = ClamShell(
    super_commands=['files', 'exit'],
    aliases={'_': '_'},
    get_prompt=get_prompt,
    get_continuation_prompt=get_continuation_prompt,
)


def run_clam():
    while clamshell.run_repl:
        try:
            clamshell.repl()
        except KeyboardInterrupt:
            clamshell.print_output('')

if __name__ == '__main__':
    run_clam()
