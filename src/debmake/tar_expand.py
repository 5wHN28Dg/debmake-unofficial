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
import os
import sys

import debmake.sh
import debmake.yn


###########################################################################
def tar_expand(para):
    """expand tarball to package-version

    para["tarball"]   =  'package-version.tar.*z' or ''
                      or 'package_version.orig.tar.*z'
    para["url"]       =   ....
    para["option_z"]     = --xz --gzip --bz2 ''
    para["source_dir"]  = package-version_tmp
    para["debmake_dir"]  = package-version

    Side-effects:
        * para['debmake_dir'] + "_tmp" is temp directory (overwritten)
        * para['debmake_dir'] directory is created if it doesn't exist.
        * Existing para['debmake_dir'] contents may be replaced with
          the current content after pausing for [Y/n]
    """

    print('I: expand the upstream tarball "{}"'.format(para["tarball"]))
    if not os.path.exists(para["tarball"]):
        print(
            "E: tarball missing in {}".format(
                os.path.relpath(os.getcwd(), para["start_dir"])
            ),
            file=sys.stderr,
        )
        exit(1)
    if os.path.isdir(para["source_dir"]):
        command = "rm -rf " + para["source_dir"]
        debmake.sh.sh(command)
    if os.path.isdir(para["debmake_dir"]):
        debmake.yn.yn(
            'remove old "{}" directory'.format(para["debmake_dir"]),
            "rm -rf " + para["debmake_dir"],
            para["yes"],
        )
    command = "mkdir -p " + para["source_dir"]
    debmake.sh.sh(command)
    if para["verbose"]:
        command = "tar --verbose"
    else:
        command = "tar "
    command += para["option_z"] + " -f " + para["tarball"]
    command += " -C " + para["source_dir"] + " -x"
    debmake.sh.sh(command)
    print("I: expanded {}.".format(para["tarball"]))
    expand_list = glob.glob(para["source_dir"] + "/*")
    expand_dir_list = glob.glob(para["source_dir"] + "/*/")
    if len(expand_list) == 1 and len(expand_dir_list) == 1:
        # only one directory found (likely package-version/)
        # move expand_dir_list[0] to para["debmake_dir"]
        command = "mv -f " + expand_dir_list[0] + " " + para["debmake_dir"]
        debmake.sh.sh(command)
        command = "rm -rf " + para["source_dir"]
        debmake.sh.sh(command)
    else:
        # root of archive have many files
        # move para["source_dir"] to para["debmake_dir"]
        command = "mv -f " + para["source_dir"] + para["debmake_dir"]
        debmake.sh.sh(command)
    return


if __name__ == "__main__":
    print("No test program")
