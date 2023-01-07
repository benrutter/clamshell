import os


def get_prompt() -> str:
    """
    Returns text to display in front of initial prompt
    """
    cwd = os.getcwd()
    return f" 🐚 {cwd} $ "


def get_continuation_prompt() -> str:
    """
    Returns text to display on continuation lines after initial prompt
    """
    return " ... "
