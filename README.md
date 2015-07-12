#pit.py

It's a gitlike VCS in Python! Wow! It's called pit because it's not great. It
makes it a bit easier to use if you do:

    ln -s /path/to/pit.py /usr/bin/pit

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

to check out either a branch or a commit (there isn't a whole lot different
between these, except that branches have human-readable names).

That's about it!

###TODO:

- stash
- history/git log
- user defined aliases for commits


