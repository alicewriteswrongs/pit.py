import sys
import os
import hashlib
import time
import json

def main():
    if (len(sys.argv) == 1 or sys.argv[1] == "--help"):
        print("usage:  version.py --init\t\tstart a new repo")
        print("\tversion.py --add\t\tstage a file")
        print("\tversion.py --commit author message\twrite a commit with staged files")
        print("\tversion.py --status\t\tget information about staged files")
        print("\tversion.py --help to display this message")
        return 0
    elif (sys.argv[1] == "--init"):
        init()
    elif (sys.argv[1] == "--add"):
        if (os.path.isfile("./" + sys.argv[2])):
            addFile(sys.argv[2])
        else:
            print("error: not a file", file=sys.stderr)
    elif (sys.argv[1] == "--status"): # this will basically just print stage
        status()
    elif (sys.argv[1] == "commit"):
        writeCommit(sys.argv[2], sys.argv[3])
    else:
        print("sorry, I didn't understand that", file=sys.stderr)

def status():
    with open("./.versionpy/stage") as stage:
        text = stage.readlines()

    if (text == []):
        print("Nothing staged. Use python version.py --add myfile")
    else:
        print("Files currently staged for commit:")
        for line in text:
            print('\t' + line.split('\t')[0])


def init():
    """
    this just checks for an existing repo, and if there isn't one it
    will make a fresh one
    """
    if (os.path.isdir("./.versionpy")):
        print("error: repository exists", file = sys.stderr)
        return -1
    else:
        os.mkdir("./.versionpy")
        os.mkdir("./.versionpy/objects")
        os.mkdir("./.versionpy/commits")
        open("./.versionpy/stage","w")
        open("./.versionpy/head","w")
        print("created empty repository in .versionpy, enjoy!")
        return 0


def stageFile(filename, filedir, hashname):
    """
    this is called within addFile, and it will add the appropriate info
    to the stage file
    """
    with open("./.versionpy/stage") as myfile:
        lines = myfile.readlines()

    filepath = "./.versionpy/objects/" + filedir.hexdigest() + "/" + hashname.hexdigest()

    if (lines == []):
        with open("./.versionpy/stage", "a") as myfile:
            myfile.writelines(filename + '\t' + filepath + "\n")
    else:
        for line in lines:
            if (line.split('\t')[1] == filepath):
                print("error: object already staged but not in object directory", file=sys.stderr)
                return -1

        with open("./.versionpy/stage", "a") as myfile:
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
    with open("./.versionpy/head", "r") as myfile:
        commit['parent'] = myfile.read()

    #read in staged files
    with open("./.versionpy/stage", "r") as myfile:
        files = myfile.readlines()

    committed = {}
    filecounter = 0
    for item in files:
        linesplit = item.split('\t')
        committed[linesplit[0]] = linesplit[1]
        filecounter += 1
    commit['committed_files'] = committed

    #reset stage file
    with open("./.versionpy/stage", "w") as myfile:
        myfile.write("")

    #write the commit file
    filename = hashlib.sha1()
    filename.update(message.encode('utf-8') + author.encode('utf-8') + time.ctime().encode('utf-8'))
    with open("./.versionpy/commits/" + filename.hexdigest(), "w") as myfile:
        json.dump(commit, myfile)

    #update head file (filename of latest commit)
    with open("./.versionpy/head","w") as myfile:
        myfile.write(filename.hexdigest())

    print("Commited " + str(filecounter) + " file(s) to " + filename.hexdigest())

def commitInfo(commitname):
    """
    get info about a commit!
    """
    with open("./.versionpy/commits/" + commitname) as myfile:
        commit = json.parse(myfile)



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
    if not (os.path.isdir("./.versionpy/objects/" + filedir.hexdigest())):
        os.mkdir("./.versionpy/objects/" + filedir.hexdigest())

    hashname = hashlib.sha1()
    moddate = time.ctime(os.path.getmtime(filename)).encode('utf-8')
    hashname.update(filename.encode('utf-8') + moddate)
    if not (os.path.isfile("./.versionpy/objects/" + filedir.hexdigest() 
                    + "/" + hashname.hexdigest())):
        # we open a file in the added files object directory,
        # with the name of the filename + last date modified
        writefile = open("./.versionpy/objects/" + filedir.hexdigest()
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
