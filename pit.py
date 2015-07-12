#!/usr/bin/python

import sys
import os
import shutil
import hashlib
import time
import json

def main():
    if (len(sys.argv) == 1 or sys.argv[1] == "--help"):
        print("usage:  pit.py --init\t\tstart a new repo")
        print("\tpit.py --add\t\tstage a file")
        print("\tpit.py --commit author message\twrite a commit with staged files")
        print("\tpit.py --status\t\tget information about staged files")
        print("\tpit.py --branch branchName author\tto create a new branch")
        print("\tpit.py --checkout arg\t to checkout a branch or commit")
        print("\tpit.py --info\t\tget information about a commit")
        print("\tpit.py --help to display this message")
        return 0
    elif (sys.argv[1].strip('-') == "init"):
        init()
    elif (sys.argv[1].strip('-') == "add"):
        if (os.path.isfile("./" + sys.argv[2])):
            addFile(sys.argv[2])
        else:
            print("error: not a file", file=sys.stderr)
    elif (sys.argv[1].strip('-') == "status"): # this will basically just print stage
        status()
    elif (sys.argv[1].strip('-') == "commit"):
        writeCommit(sys.argv[2], sys.argv[3]) #author and message
    elif (sys.argv[1].strip('-') == "info"):
        commitInfo(sys.argv[2])
    elif (sys.argv[1].strip('-') == "branch"):
        if (len(sys.argv) == 2):
            branchInfo()
        else:
            branchCommit(sys.argv[2], sys.argv[3]) #branch name and author
    elif (sys.argv[1].strip('-') == "checkout"):
        checkout(sys.argv[2])
    else:
        print("sorry, I didn't understand that", file=sys.stderr)


def status():
    with open("./.pit/stage") as stage:
        text = stage.readlines()

    if (text == []):
        print("Nothing staged. Use python pit.py --add myfile")
    else:
        print("Files currently staged for commit:")
        for line in text:
            print('\t' + line.split('\t')[0])


def init():
    """
    this just checks for an existing repo, and if there isn't one it
    will make a fresh one
    """
    if (os.path.isdir("./.pit")):
        print("error: repository exists", file = sys.stderr)
        return -1
    else:
        os.mkdir("./.pit")
        os.mkdir("./.pit/objects")
        os.mkdir("./.pit/commits")
        open("./.pit/stage","w")
        open("./.pit/head","w")
        open("./.pit/branches", "w")
        print("created empty repository in .pit, enjoy!")
        return 0


def stageFile(filename, filedir, hashname):
    """
    this is called within addFile, and it will add the appropriate info
    to the stage file
    """
    with open("./.pit/stage") as myfile:
        lines = myfile.readlines()

    filepath = "./.pit/objects/" + filedir.hexdigest() + "/" + hashname.hexdigest()

    if (lines == []):
        with open("./.pit/stage", "a") as myfile:
            myfile.writelines(filename + '\t' + filepath + "\n")
    else:
        for line in lines:
            if (line.split('\t')[1] == filepath):
                print("error: object already staged but not in object directory", file=sys.stderr)
                return -1

        with open("./.pit/stage", "a") as myfile:
            myfile.writelines(filename + '\t' + filepath + "\n")


def writeCommit(author, message):
    """
    this will write a commit, clear the staging file, and reset the HEAD file
    the commit is just a JSON object, where the filename is derived from the
    author, commit message, and current time
    """
    commit = {}
    commit['message'] = message
    commit['author'] = author

    #get parent
    with open("./.pit/head", "r") as myfile:
        commit['parent'] = myfile.read()

    #read in staged files
    with open("./.pit/stage", "r") as myfile:
        files = myfile.readlines()

    committed = {}
    filecounter = 0
    for item in files:
        linesplit = item.split('\t')
        committed[linesplit[0]] = linesplit[1]
        filecounter += 1
    commit['committed_files'] = committed

    #deal with previously committed files (this way every commit
    #has a complete description of the stage of the working 
    #directory)
    previous = {}
    if commit['parent'] == "":
        commit['previous'] = previous
    else:
        with open("./.pit/commits/" + commit['parent']) as myfile:
            parent = json.load(myfile)

        for key in parent['committed_files'].keys():
            if key not in commit['committed_files']:
                previous[key] = parent['committed_files'][key]

        for key in parent['previous'].keys():
            if key not in commit['committed_files']:
                previous[key] = parent['previous'][key]
        commit['previous'] = previous

    #reset stage file
    with open("./.pit/stage", "w") as myfile:
        myfile.write("")

    #write the commit file
    filename = hashlib.sha1()
    filename.update(message.encode('utf-8') + author.encode('utf-8') + time.ctime().encode('utf-8'))

    #deal with branch related stuff
    if commit['parent'] == "":
        commit['branch'] = 'master'
        branches = {'master': filename.hexdigest()}
        with open("./.pit/branches", "w") as myfile:
            json.dump(branches, myfile)
    else:
        commit['branch'] = parent['branch']
        with open("./.pit/branches", "r") as myfile:
            branches = json.load(myfile)
        branches[commit['branch']] = filename.hexdigest()
        with open("./.pit/branches", "w") as myfile:
            json.dump(branches, myfile)

    with open("./.pit/commits/" + filename.hexdigest(), "w") as myfile:
        json.dump(commit, myfile)

    #update head file (filename of latest commit)
    with open("./.pit/head","w") as myfile:
        myfile.write(filename.hexdigest())

    print("Commited " + str(filecounter) + " file(s) to " + filename.hexdigest())


def branchCommit(branch, author):
    """
    this will write a commit, and create a new branch. a branch commit does
    not commit working directory files, it just creates a branch and writes a
    commit to that branch
    """
    commit = {}
    commit['branch'] = branch
    commit['author'] = author

    #get parent
    with open("./.pit/head", "r") as myfile:
        commit['parent'] = myfile.read()

    #this is blank, because we're doing a branch commit
    committed = {}
    commit['committed_files'] = committed

    #we need a 'previously' object in every commit
    previously = {}
    with open("./.pit/commits/" + commit['parent']) as myfile:
        parent = json.load(myfile)
    for key in parent['committed_files'].keys():
        if key not in previously:
            previously[key] = parent['committed_files'][key]
    for key in parent['previous'].keys():
        if key not in previously:
            previously[key] = parent['previous'][key]
    commit['previous'] = previously

    #write the commit file
    filename = hashlib.sha1()
    filename.update(branch.encode('utf-8') + author.encode('utf-8') + time.ctime().encode('utf-8'))
    with open("./.pit/commits/" + filename.hexdigest(), "w") as myfile:
        json.dump(commit, myfile)

    #deal with branch related stuff
    with open("./.pit/branches", "r") as myfile:
        branches = json.load(myfile)

    branches[branch] = filename.hexdigest()

    with open("./.pit/branches","w") as myfile:
        json.dump(branches, myfile)

    #update head file (filename of latest commit)
    with open("./.pit/head","w") as myfile:
        myfile.write(filename.hexdigest())

    print("New branch '" + branch + "' committed to " + filename.hexdigest())


def branchInfo():
    """
    get info about the current branches!
    """
    with open("./.pit/head", "r") as myfile:
        commit = myfile.read()

    with open("./.pit/branches", "r") as myfile:
        branches = json.load(myfile)

    print("Branches! Nice.")
    for key in branches.keys():
        if branches[key] == commit:
            print("    ~*~ " + key + " ~*~")
        else:
            print('\t' + key)
    return 0

def checkout(argument): #could be commit hash or branch name
    """
    takes a branch name or a commit hash, and changes the contents of the
    working directory to match the state at that commit
    """
    with open("./.pit/stage") as myfile:
        stage = myfile.read()

    if stage != '':
        print("error: staged, uncommitted files in working directory.", file=sys.stderr)
        return 1

    with open("./.pit/branches") as myfile:
        branches = json.load(myfile)

    if argument in branches:
        commitname = branches[argument]
    else:
        if (os.path.isfile("./.pit/commits/" + argument)):
            commitname = argument
        else:
            print("error: " + argument + " is not a branch or a commit", file=sys.stderr)
            return 1

    with open("./.pit/commits/" + commitname) as myfile:
        commit = json.load(myfile) 

    for key in commit['previous'].keys():
        shutil.copy(commit['previous'][key], "./" + key)
 
    for key in commit['committed_files'].keys():
        shutil.copy(commit['committed_files'][key].strip('\n'), "./" + key)

    #update head
    with open("./.pit/head", "w") as myfile:
        myfile.write(commitname)

    #update branch?
    #I think we want to do this in case we're stepping back in a branch?
    return 0


def commitInfo(commitname):
    """
    get info about a commit!
    """
    with open("./.pit/commits/" + commitname) as myfile:
        commit = json.load(myfile)

    print("Commited by " + commit['author'] + ". Message: " + commit['message'])
    print("Files commited:")

    for item in commit['committed_files'].keys():
        print("\t" + item)
    return 0

def addFile(filename):
    """
    checks to see if a file is already in the object directory,
    if it is it then checks current version against this one,
    and decides if it will add a new version or not.

    if the file is not in the directory at all, then it adds a
    new object folder, and add the first version of the file to it
    """
    filedir = hashlib.sha1()
    filedir.update(filename.encode('utf-8'))
    # no object dir? make it
    if not (os.path.isdir("./.pit/objects/" + filedir.hexdigest())):
        os.mkdir("./.pit/objects/" + filedir.hexdigest())

    hashname = hashlib.sha1()
    moddate = time.ctime(os.path.getmtime(filename)).encode('utf-8')
    hashname.update(filename.encode('utf-8') + moddate)
    if not (os.path.isfile("./.pit/objects/" + filedir.hexdigest() 
                    + "/" + hashname.hexdigest())):
        # we open a file in the added files object directory,
        # with the name of the filename + last date modified
        writefile = open("./.pit/objects/" + filedir.hexdigest()
            + "/" + hashname.hexdigest(),"w")
        with open(sys.argv[2]) as myfile:
            text = myfile.read()

        writefile.write(text)
        writefile.close()

        stageFile(filename, filedir, hashname)
        print("Staged " + filename)

    else: #this means the file with that name and date modified already exists
        print("error: that version is already in database", file=sys.stderr)


main()
