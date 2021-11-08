# pit.py

It's a gitlike VCS in Python! Wow! It's called pit because it's not great.
Pit is written in Python 3, and it expects it to be at /usr/bin/python3. If
your python 3 is in a different place you can probably either edit pit.py or
make a symlink.

It makes it a bit easier to use if you do:

    sudo ln -s /path/to/pit.py /usr/bin/pit

So you can do:

    pit init

To create a new repo (in `.pit`).

    pit add myfile

to stage `myfile`.

    pit commit author 'commit message'

to write a commit object, and 

    pit status

To see the currently staged files.

    pit info commit

where commit is the hash of a commit your interested in, to get information
about who committed it and which files were included.

    pit branch

To see info about the branches, and 
    
    pit branch branchname author

To create a new branch `branchname` with author `author`. Then you can do:

    pit checkout object

to check out either a branch or a commit (there isn't a whole lot of difference
between these, except that branches have human-readable names).

I also added an alias feature:

    pit alias name commit

This just lets you make a human readable name for a commit, which you can
use to checkout that commit later.

That's about it!

###TODO:

- stash
- history/git log
- diff
