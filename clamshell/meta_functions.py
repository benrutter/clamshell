from typing import Callable, Type


def try_else_none(function: Callable) -> Callable:
    """
    Wraps the given function in a try/except
    Returning None on failure
    """

    def wrapped_function(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except:
            return None

    return wrapped_function


def try_else_empty_list(function: Callable) -> Callable:
    """
    Wraps the given function in a try/except
    Returning empty list ([]) on failure
    """

    def wrapped_function(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except:
            return []

    return wrapped_function


def coerce(value: Type, default: Type) -> Type:
    """
    Returns the first argument, unless None,
    in which case the second argument is returned
    """
    if value:
        return value
    return default


def capture_and_return_exception(function: Type) -> Type:
    """
    Wraps the given function to return exception as string
    on failure
    """
    def new_function(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as exception:
            return f"[red bold] ! >> {str(repr(exception))}[/red bold]"
    return new_function
