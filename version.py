import sys
import os

def main():
    if (len(sys.argv) == 1 or sys.argv[1] == "--help"):
        print("usage:  version.py --init\t\tstart a new repo")
        print("\tversion.py --add\t\tstage a file")
        print("\tversion.py --commit 'commit message'\twrite a commit with staged files")
        print("\tversion.py --help to display this message")
        return 0
    elif (sys.argv[1]) == "--init":
        if (os.path.isdir("./.versionpy")):
            print("error: repository exists", file = sys.stderr)
            return -1
        else:
            os.mkdir("./.versionpy")
            print("created empty repository in .versionpy, enjoy!")
            return 0
    else:
        print("oops")
            

        


main()
