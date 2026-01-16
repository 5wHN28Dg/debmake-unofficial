#!/usr/bin/python3
# vim:se tw=0 sts=4 ts=4 et ai:
"""
Copyright © 2014 Osamu Aoki

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
import os
import sys

import debmake.debug


#######################################################################
# cat >file
def cat(file, text, para):
    # para: global variable
    if os.path.isfile(file) and os.stat(file).st_size != 0:
        if para["backup"]:
            file = file + ".bkup"
        else:
            # skip if a file exists and non-zero content
            print(
                "I: skipping : {} (use --backup option to avoid skipping)".format(file),
                file=sys.stderr,
            )
            return
    newtext = ""
    if para["tutorial"]:
        for line in text.split("\n"):
            if line[:3] != "###":
                newtext += line + "\n"
            else:
                newtext += line[2:] + "\n"
    else:
        for line in text.split("\n"):
            if line[:3] != "###":
                newtext += line + "\n"
    newtext = newtext.rstrip() + "\n"
    file_dirpath = os.path.dirname(file)
    if file_dirpath:
        os.makedirs(file_dirpath, exist_ok=True)
    with open(file, mode="w", encoding="utf-8") as f:
        print(newtext, file=f, end="")
        debmake.debug.debug(
            "s",
            para,
            'D: output to "{}" as\n========vvvvvvvv\n{}\n========^^^^^^^^'.format(
                file, newtext
            ),
        )
    return


#######################################################################
# Test script
#######################################################################
if __name__ == "__main__":
    para = {}
    para["tutorial"] = False
    para["backup"] = False
    cat("testfile0.tmp", "fooo\n###barrrr\n####CCCC\nbazzzzz", para)
    para["tutorial"] = True
    cat("testfile1.tmp", "fooo\n###barrrr\n####CCCC\nbazzzzz", para)
