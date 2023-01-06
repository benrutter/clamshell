def try_else_none(function):
    def wrapped_function(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except:
            return None

    return wrapped_function


def try_else_empty_list(function):
    def wrapped_function(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except:
            return []

    return wrapped_function


def coerce(value, default):
    if value:
        return value
    return default
