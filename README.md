#pit.py
It's a gitlike VCS in Python! Wow! It's called pit because it's not great.

So you can do:

    python pit.py --init

To create a new repo (in `.pit`).

    python pit.py --add myfile

to stage `myfile`.

    python pit.py --commit author 'commit message'

to write a commit object, and 

    python pit.py --status

To see the currently staged files.

    python pit.py --info commit

where commit is the hash of a commit your interested in, to get information
about who committed it and which files were included.

That's about it!

###TODO:

- branches
- checkout
- stash
- history/git log


