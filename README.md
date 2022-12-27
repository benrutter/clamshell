# clam shell 🦪

Experimental and modern python based shell

Idea:

Reimagining the shell with:
- common sense function names
- easy hackability
- modern programming convenience

xonsh does a lot like this and better,
But the idea is to reimagine the shell completely
(I.e no bash)

Special repl loop to allow:
   - first run as python
   - then run as reformatted clam python
   - then execute as command

## convenient function

- files (ls equivalent) returns list
- goto (cd equivalent) moves, including searching for location if not in directoru
- see (cat equivalent) shows formatted file output
- move, copy, delete do as expected

## Clam python
Basically, allow python commands to be ran like cli
I.e
```
print 'hello world'
# runs print('hello world')
```
Or
```
goto 'Documents/cool-folder'
# runs goto('Documents/cool-folder')
```
This already works, but still to do is auto-stringify:

```
goto Documents/cool-folder
# runs goto('Documents/cool-folder')
```

Also, to do is allow variable setting
```
tunes = files '~/Music'
```

## Run

Already done is execute program like:
```
python3 -m pytest
```

To do is capture stdout as variable:
```
results = python3 -m pytest
```


## Other still to do
(lots, although prompt toolkit covers a lot of this)

- Formatted input
- autocompletion
- history
- configurable init file


