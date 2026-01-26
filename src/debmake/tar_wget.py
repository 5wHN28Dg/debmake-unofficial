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
# upstream: called from debmake.__main__()
###########################################################################
# get upstream source to the current directory
def tar_wget(para):
    if shutil.which("wget"):
        command = "wget "
    elif shutil.which("curl"):
        command = "curl -O "
    else:
        print("E: please install wget or curl.", file=sys.stderr)
        exit(1)
    if para["verbose"]:
        command += "--verbose " + para["url"]
    else:
        command += para["url"]
    debmake.sh.sh(command)
    return


if __name__ == "__main__":
    para = dict()
    para["url"] = sys.argv[1]
    para["tarball"] = os.path.basename(para["url"])
    tar_wget(para)
