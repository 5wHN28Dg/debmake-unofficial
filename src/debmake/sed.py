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

import glob
import sys

import debmake.cat


#######################################################################
def sed(confmask, destdir, substlist, package, para):
    ###################################################################
    # confmask:   configuration file path glob mask with *
    # destdir:   destination directory with / at the end
    # substlist: substitution dictionary
    # package:   binary package name
    # para:      global variable
    ###################################################################
    len_data_path = len(para["data_path"])
    for file in glob.glob(para["data_path"] + confmask):
        destname = file[len_data_path + file[len_data_path:].find("_") + 1 :]
        if destname[: len("package")] == "package":
            newfile = destdir + package + destname[len("package") :]
        else:
            newfile = destdir + destname
        print(
            "I: creating {} from {}".format(newfile, file[len_data_path:]),
            file=sys.stderr,
        )
        with open(file, mode="r", encoding="utf-8") as f:
            text = f.read()
        for k in substlist.keys():
            text = text.replace(k, substlist[k])
        debmake.cat.cat(newfile, text, para)
    return


#######################################################################
# Test script
#######################################################################
if __name__ == "__main__":
    para = {}
    substlist = {
        "@BINPACKAGE@": "binpackage",
        "@PACKAGE@": "package",
        "@UCPACKAGE@": "package".upper(),
        "@YEAR@": "2014",
        "@FULLNAME@": "fullname",
        "@EMAIL@": "email@example.org",
        "@SHORTDATE@": "11 Jan. 2013",
    }
    sed("data/extra2_", "debian/", substlist, "package", para)
    sed("data/extra3_", "debian/", substlist, "package", para)
