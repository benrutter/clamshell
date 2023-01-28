# clamshell 🦪

Experimental shell for utopians!


### What is this?

clamshell is a repl shell for using python as an interactive shell (like bash, fish, zsh etc)

I love working in the terminal, and use Bash all the time, but there's a bunch of stuff I feel like I wish it has:

- Autocompletion, syntax highlighting etc
- Actual types that got used (like arrays, numbers, ints)
- Easier syntax (does anyone actually know how to define a function, loop through something, add two numbers without having to look it up every time?)
- Less terse (This is the most subjective, but built in functions like 'cd', 'ls' are designed to be quick to type, but we have autocompletion for that- I'd rather things were more obvious to beginners)

I built clamshell as an experiment to think about what an ideal shell utopia might look like.

It's an experiment, and you can run it on windows, mac or linux.

### That sounds like xonsh

Yes it does! Xonsh is actually a much better idea if you're looking for something to use since it is production ready, has less dependencies and a safer execution pattern (check it out!)[]

But, xonsh is based on the idea of using python *with* another existing shell language like bash, I wanted to experiment with what it would be like to actually have a *fully python shell* - where your standard shell commands had types, and where python functions could get ran just like command line arguments/

### Like command line arguments you say?

Yeah! Let's taken an example.

Python has a function to change directory already, so why not just load up a default python repl and do stuff like this:

```python
os.chdir('Music/great-tunes/')
```

It should work fine, but it seems like a lot more typing than just:

```bash
cd Music/great-tunes
```

So clamshell adds an extra layer of interpretation whereby this:

```clam
os.chdir Music/great-tunes
```

gets ran as if it has the first command.

This works for anything you define as well, so say we type up this new function:

```python
def say_hello(name='stranger'):
  print(f'Hello {name}!')
```

We can run this as usual with:
```python
say_hello('Joe')
>> "Hello Joe!"
```

But you also have the option of running it with clam syntax:
```clam
say_hello Joe
>> "Hello Joe!"
```

There's also a concept of "super_commands" (sorry for the terrible name), where a function explicitly set as one, will run when typed in with no arguments (rather than just spitting back the type, as is normal python repl behaviour):

```clam
say_hello
>> "Hello stranger!"
```
Pretty handy right?!
If something isn't runnable as python, but is a runnable command, then that'll work too:

```clam
docker run
>> "doing docker stuff"
```

You can import .py files and modules as you would in a normal repo too:

```clam
import pandas as pd
```

And then use that in your interactive shell.

Bear in mind, this is all experimental, and you probably shouldn't use it in production - again, see the awesome Xonsh if you want to use python in the shell in a more robust setting.


## A quick tour of built in functions

### goto: move directories

Initial use is basically just like 'cd' in bash:

```clam
~/me $_ goto Documents/some_folder
~/me/Documents/some_folder $_
```

We move to working in another directory. So far so good!

Aside from 'goto' being a more beginner friendly name that 'cd', this is pretty much identical behaviour.

But. .  .

As a nice tweak, clamshell maps out your directories on start up, so if a folder isn't hidden, and is within a certain depth from your home directory, you don't have to type the full path:

```clam
~/me $_ goto cool_album
~/me/Music/cool_album $_ goto important_docs
~/me/Documents/important_docs $_
```

Nice! That's a lot less time we can spend remembering where we saved a folder.

### files: get a list of files

This is the equivalent of 'ls', although it returns a special "file list" which is basically just a list that clamshell will print as a nice table.

```clam
~/me $_ files

<a nice table of files appears>
```

We can pass arguments to see another folder, include hidden files, and recur down to see subfolders too

```clam
~/me $_ files Documents/another_folder True 3

<a nice table of files appears>
```

That above command calls the equivalent of this:
```python
files(path='Documents/another_folder', hidden=True, recursive=3)
```
which means it'll include hidden files and folders, and recur into folders up to a depth of 3.

Because the return is a list, we can do things like loop through it's return (although note that for setting variables, we no longer get to use our fun clam syntax 🥲):

```clam
~/me $_ x = files('Music')
~/me $_ for item in x:
      >     if 'Rick Astley' not in x['name']:
      >         delete(x['path'])
```

Phew! That deleted every file and folder in Music that didn't have Rick Astley in the name (more on delete later)


### copy and move

Not much to save about these, they copy or move a file/folder from one place to another:

```clam
~/me $_ move some_file.txt a_folder/somewhere_else.txt
```

Although, combined with the files() return, we can do some cool stuff to move things from one location to another:

```clam
~/me/Downloads/new_album $_ to_move = files()
~/me/Downlaods/new_album $_ goto Music
~/me/Music $_ [copy(i['path'], i['name']) for i in to_move]
```


### delete

Works *a bit* like rm, except that it'll put things into the recycle bin thanks to the beautiful send2trash module.

So we can do this in a burst of desire to destroy everything:
```clam
~/me $_ delete Documents
```

but unlike running:
```bash
~/me $_ rm -rf Documents
```

We can recover our stuff later.


### pipe and run

Sadly, if we're in some python logic, we can't just run shell commands. This function (which uses my 'mpy3' command line runnable) won't work:

```clam
~/me/Music $_ for i in files():
            >     if i['name'].endswith('.mp3'):
            >         mpy3 i['name']
```

If something isn't native python, once we're in a loop for function, we have to use "run" (which is basically just pythons subprocessing module's run.

It returns an object with .stdout and .stderr methods that can be handy, so you can set variables, or process standard output and input pretty easy.

```clam
~/me/Music $_ for i in files():
            >     if i['name'].endswith('.mp3'):
            >         run(f'mpy3 {i['name']}')
```

There's also a handy "pipe" function, that'll do basically what you think (pipe the results from the first argument into the second, and the second into the third, etc).

```clam
~/me/Music $_ pipe(
            >     files()[0],
            >     lambda x: run(f'mpy3 {x}')
            > )
```

or something like:

```clam
~/me/Music $_ pipe(
            >     run('ls')
            >     lambda x: print(f'output of ls is {x.stdout}')
            > )
```

### Other functions

There are a bunch of other functions to, which are a bit more self explanatory, and have less to say on:
    - read(name_of_file) -> prints out a nicely formatted version of a file
    - search(string, path, recursive=0) -> will seach for a string occurence within files and give use the lines
    - make_file, make_directory -> make a file or directory with the name of the argument given

## clamrc.py

on first running, clamshell with make a file in your home under '.config/clamshell/clamrc.py'. This'll get ran and brought into global variables every time you start up clamshell.

At first it'll just be blank.

It's just a normal python file, so if we add something like this to it:

```python
interesting_opinion = """
I’d just like to interject for a moment. What you’re refering to as Linux, is in fact, GNU/Linux, or as I’ve recently taken to calling it, GNU plus Linux. Linux is not an operating system unto itself, but rather another free component of a fully functioning GNU system made useful by the GNU corelibs, shell utilities and vital system components comprising a full OS as defined by POSIX.
"""
def be_interesting():
  print(interesting_optinion)
```

We can call that function anytime in our repl:
```clam
~/me $_ be_interesting()

I’d just like to interject for a moment. What you’re refering to as Linux, is in fact, GNU/Linux, or as I’ve recently taken to calling it, GNU plus Linux. Linux is not an operating system unto itself, but rather another free component of a fully functioning GNU system made useful by the GNU corelibs, shell utilities and vital system components comprising a full OS as defined by POSIX.
```

There's a couple of special tweaks that are worth menthioning. . .

### super_commands

Again, sorry for the name, but if we define a list with it of **strings of the names of functions** (kinda wierd, sorry!). Then those functions become 'super_commands', and are ran whenever they're typed without having to use python's () function sytanx.

So if we add this to the end of our clamrc.py:

```python
super_commands = ['be_interesting']
```
Now we can be interesting with even less keystrokes:

```clam
~/me $_ be_interesting

I’d just like to interject for a moment. What you’re refering to as Linux, is in fact, GNU/Linux, or as I’ve recently taken to calling it, GNU plus Linux. Linux is not an operating system unto itself, but rather another free component of a fully functioning GNU system made useful by the GNU corelibs, shell utilities and vital system components comprising a full OS as defined by POSIX.
```

### aliases

Just like with bash, we can alias things by adding them in our clamrc.py.

We just add a dictionary called "aliases":

```python
aliases = {'python2': 'python3'}
```

Now every time someone tries to run python2, python3 will run instead. Phew, how  helpful!

### get_prompt & get_continuation_prompt

We can define a custom prompt by making a function that returns a string:

```python
import os

def get_prompt():
    return 'cooooooooooooool ' + os.getcwd() + ' >'

def continuation_prompt():
    return 'keep it up>>'
```

Now our shell looks like this:

```clam
coooooooool ~/me > def something():
keep it up>>     print('stuff')
```

Aside from that, the whole file is just normal python that'll get interpretted as normal python.

That makes it pretty easy to write quick utilities for ourselves, or take use of python's capabilities to do something crazy, like:

- Print out an inspirational quote every time we start the shell
- Delete every file we own if it's 14:34
- Get the price of bitcoin from an api and print it out in the command prompt


## How do I get this wonderful beast!?

Though pip:

```
pip install clamshell
```

and then either:
```
clamshell
```
or
```
python -m clamshell
```



