from os import environ

from rich import print

from .shell import ClamShell
from .utils import files, delete, search, copy, move, goto, read, make_file, make_directory, get_prompt, get_continuation_prompt, run, clear

# making callable function
clamshell = ClamShell(
    super_commands=['files', 'exit', 'clear'],
    aliases={'_': '_'},
    get_prompt=get_prompt,
    get_continuation_prompt=get_continuation_prompt,
    shell_globals=globals(),
    shell_locals=locals(),
)

try:
    # currently ugly code to load rc
    from .utils import get_splitter
    import sys
    rc_path, rc_file = clamshell.rc_file().rsplit(get_splitter(), 1)
    sys.path.append(rc_path)
    from clamrc import *
    if 'super_commands' in locals():
        clamshell.super_commands += super_commands
        del super_commands
    if 'aliases' in locals():
        clamshell.aliases.update(aliases)
        del aliases
    if 'get_prompt' in locals():
        clamshell.get_prompt = get_prompt
        del get_prompt
    if 'get_continuation_prompt' in locals():
        clamshell.get_continuation_prompt = get_continuation_prompt
        del get_continuation_prompt
    del get_splitter
    del sys
    del rc_path
    del rc_file
except:
    print("Error loading/running clamrc")

def run_clam():
    while clamshell.run_repl:
        try:
            clamshell.repl()
        except KeyboardInterrupt:
            clamshell.print_output('')

if __name__ == '__main__':
    run_clam()
