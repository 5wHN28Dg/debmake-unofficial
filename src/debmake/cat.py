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


#######################################################################
# cat >file
def cat(file, text, para):
    if file[-3:] != ".ex":
        file_noex = file
    else:
        file_noex = file[:-3]
    file_ex = file_noex + ".ex"
    if os.path.exists(file_noex) and os.stat(file_noex).st_size != 0:
        if para["backup"]:
            file_write = file_ex
        else:
            file_write = ""
    else:
        file_write = file
    if file_write == "":
        # skip if a file exists and non-zero content
        print("I: skip writing: {})".format(file))
    else:
        newtext = ""
        for line in text.split("\n"):
            newtext += line + "\n"
        newtext = newtext.rstrip() + "\n"
        file_dirpath = os.path.dirname(file)
        if file_dirpath:
            os.makedirs(file_dirpath, exist_ok=True)
        with open(file_write, mode="w", encoding="utf-8") as f:
            print(newtext, file=f, end="")
    return


#######################################################################
# Test script
#######################################################################
if __name__ == "__main__":
    para = {}
    para["backup"] = True
    file1 = "00_testfile0"
    file2 = "00_testfile0"
    print('{} -> {} with para["backup"] = {}'.format(file1, file2, para["backup"]))
    cat(file1, "0fooo\n###barrrr\n####CCCC\nbazzzzz", para)
    cat(file2, "1fooo\n###barrrr\n####CCCC\nbazzzzz", para)
    file1 = "00_testfile1"
    file2 = "00_testfile1.ex"
    print('{} -> {} with para["backup"] = {}'.format(file1, file2, para["backup"]))
    cat(file1, "0fooo\n###barrrr\n####CCCC\nbazzzzz", para)
    cat(file2, "1fooo\n###barrrr\n####CCCC\nbazzzzz", para)
    file1 = "00_testfile2.ex"
    file2 = "00_testfile2.ex"
    print('{} -> {} with para["backup"] = {}'.format(file1, file2, para["backup"]))
    cat(file1, "0fooo\n###barrrr\n####CCCC\nbazzzzz", para)
    cat(file2, "1fooo\n###barrrr\n####CCCC\nbazzzzz", para)
    para["backup"] = False
    file1 = "00_testfile3"
    file2 = "00_testfile3"
    print('{} -> {} with para["backup"] = {}'.format(file1, file2, para["backup"]))
    cat(file1, "0fooo\n###barrrr\n####CCCC\nbazzzzz", para)
    cat(file2, "1fooo\n###barrrr\n####CCCC\nbazzzzz", para)
    file1 = "00_testfile4"
    file2 = "00_testfile4.ex"
    print('{} -> {} with para["backup"] = {}'.format(file1, file2, para["backup"]))
    cat(file1, "0fooo\n###barrrr\n####CCCC\nbazzzzz", para)
    cat(file2, "1fooo\n###barrrr\n####CCCC\nbazzzzz", para)
    file1 = "00_testfile5.ex"
    file2 = "00_testfile4.ex"
    print('{} -> {} with para["backup"] = {}'.format(file1, file2, para["backup"]))
    cat(file1, "0fooo\n###barrrr\n####CCCC\nbazzzzz", para)
    cat(file2, "1fooo\n###barrrr\n####CCCC\nbazzzzz", para)
