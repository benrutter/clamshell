from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys

key_bindings = KeyBindings()

@key_bindings.add(Keys.Tab)
def _(event):
    before_cursor = event.app.current_buffer.document.current_line_before_cursor
    event.app.current_buffer.insert_text(' '*(4 - len(before_cursor)%4))

# overriding cntrl-c
@key_bindings.add('c-c')
def _(event):
    pass
