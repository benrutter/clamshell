import subprocess

from prompt_toolkit import prompt, print_formatted_text
from rich.console import Console

run = True
console = Console(color_system='auto')

print('This is basically just a wrapper for your existing shell')

while run:
    text = prompt('Give me some input: ')
    output = subprocess.call(text)
    console.print(output)
    if text == 'exit':
        run = False
