import sys
from os import environ

from rich import print

from .shell import ClamShell
from .shell_utils import (
    files,
    delete,
    search,
    copy,
    move,
    goto,
    read,
    make_file,
    make_directory,
    run,
    clear,
    pipe,
    splitter,
)


clamshell = ClamShell(
    super_commands=["files", "exit", "clear"],
    aliases={"_": "_"},
    shell_globals=globals(),
    shell_locals=locals(),
)

try:
    rc_path, rc_file = clamshell.rc_file().rsplit(splitter, 1)
    sys.path.append(rc_path)
    from clamrc import *

    if "super_commands" in locals():
        clamshell.super_commands += super_commands
        del super_commands
    if "aliases" in locals():
        clamshell.aliases.update(aliases)
        del aliases
    if "get_prompt" in locals():
        clamshell.get_prompt = get_prompt
        del get_prompt
    if "get_continuation_prompt" in locals():
        clamshell.get_continuation_prompt = get_continuation_prompt
        del get_continuation_prompt
    del splitter
    del sys
    del rc_path
    del rc_file
except:
    print(
        "[red]Error loading/running clamrc!\n"
        "(likely error in .config/clamrc.py script)[/red]"
    )

def run_clam():
    while True:
        try:
            clamshell.repl()
        except KeyboardInterrupt:
            clamshell.print_output("")

if __name__ == '__main__':
    run_clam()
