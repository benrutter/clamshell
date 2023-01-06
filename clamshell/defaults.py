import os


def get_prompt():
    cwd = os.getcwd()
    return f" 🐚 {cwd} $ "


def get_continuation_prompt():
    return " ... "
