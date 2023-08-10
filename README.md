This tool is intended to make it simple to generate minimalist static HTML content from markdown. The goal is not to make a general purpose tool but a specific tool for my own notes.

Use git to store info and back it up. Use git to determine date metadata aand maybe some other stuff.

Use rsync to upload to server.

Ideally don't use templating engines, just code some stuff in python. Use python to do the structuring, not a framework.

# How To Use

```bash
$ python src/generate.py $SRC $DEST
```