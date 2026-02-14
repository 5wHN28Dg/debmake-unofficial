#!/usr/bin/python3
# vim:se tw=0 sts=4 ts=4 et ai:
"""
Copyright © 2026 Osamu Aoki

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import os.path
import shutil
import sys

import debmake.sh


###########################################################################
# get upstream source to the current directory
def dir_git(para):
    """create a cloned source tree at para["source_dir"]

    para["source_dir"] = git_checkout/

    Side-effects:
        * para['source_dir'] is created if it doesn't exist.
        * Existing para['source_dir'] may be updated
    """
    if not shutil.which("git"):
        print("E: please install git.", file=sys.stderr)
        exit(1)
    if not os.path.exists(para["source_dir"]):
        print('I: checked out to "{}"'.format(para["source_dir"]), file=sys.stderr)
        command = "git clone '" + para["url"] + "'"
        debmake.sh.sh(command)
    elif os.path.exists(para["source_dir"] + "/.git/config"):
        print(
            'I: update the local work tree at "{}"'.format(para["source_dir"]),
            file=sys.stderr,
        )
        command = "cd '" + para["source_dir"] + "' ; git pull ; cd -"
        debmake.sh.sh(command)
    else:
        print(
            'E: "{}" exists but isn\'t the valid git repository'.format(
                para["source_dir"]
            ),
            file=sys.stderr,
        )
        exit(1)
    return


if __name__ == "__main__":
    para = dict()
    para["url"] = sys.argv[1]
    para["source_dir"] = os.path.basename(para["url"])
    para["yes"] = 0
    dir_git(para)
