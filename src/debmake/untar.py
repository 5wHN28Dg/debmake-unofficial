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
import subprocess
import sys

import debmake.yn


###########################################################################
def untar(para):
    """untar source tarball
    untar: called for --archive or --dist only

    para["tarball"] =  'package-version.tar.*z' or ''
                    or 'package_version.orig.tar.*z'
    para["tarxz"]     = one of 'tar.gz', 'tar.bz2' or 'tar.xz'
    para["debmake_dir"]  = package-version
    para["tar"]     = True if -t, False if -a or -d
    para["dist"]    = True if -d, False if -a or -t
    para["yes"]     = 0 (default), Ask [Y/n]
    para["yes"]     = 1 if -y, Force Yes
    para["yes"]     = 2 if -yy, Force No

    para["tarball"] is untared to para['debmake_dir'].

    Side-effects:
        * para['debmake_dir'] is created if it doesn't exist.
        * Existing para['debmake_dir'] may be replaced with the current content
          after pausing for [Y/n]
    """

    if not para["tarball"]:
        print(
            'E: para["tarball"] is NULL string. (untar)',
            file=sys.stderr,
        )
        exit(1)
    if not para["debmake_dir"]:
        print(
            'E: para["debmake_dir"] is NULL string. (untar)',
            file=sys.stderr,
        )
        exit(1)
    if not os.path.exists(para["tarball"]):
        print(
            'E: missing the "{}" file in "{}" directory. (untar)'.format(
                para["tarball"], os.getcwd()
            ),
            file=sys.stderr,
        )
        print(
            'E: "debmake" should have automatically tured on "--tar" option. (untar)',
            file=sys.stderr,
        )
        exit(1)
    print('I: untar the upstream tarball "{}"'.format(para["tarball"]), file=sys.stderr)
    if os.path.isdir(para["debmake_dir"] + "_tmp"):
        debmake.yn.yn(
            'remove old "{}" directory in untar'.format(para["debmake_dir"] + "_tmp"),
            "rm -rf " + para["debmake_dir"] + "+tmp",
            para["yes"],
        )
    if os.path.isdir(para["debmake_dir"]):
        debmake.yn.yn(
            'remove old "{}" directory in untar'.format(para["debmake_dir"]),
            "rm -rf " + para["debmake_dir"],
            para["yes"],
        )
    # setup command line
    if para["tarxz"] == "tar.bz2":
        command = "tar --bzip2 -vf "
    elif para["tarxz"] == "tar.xz":
        command = "tar --xz -vf "
    elif para["tarxz"] == "tar.gz":
        command = "tar -vzf "
    else:
        print(
            'E: the extension "{}" not supported.'.format(para["tarxz"]),
            file=sys.stderr,
        )
        exit(1)
    new_source_tree_path = para["debmake_dir"] + "_tmp"
    os.makedirs(new_source_tree_path, exist_ok=True)
    command += para["tarball"] + " -C " + new_source_tree_path + " -x"
    print("I: $ {}".format(command), file=sys.stderr)
    if subprocess.call(command, shell=True) != 0:
        print("E: failed to untar. (untar)", file=sys.stderr)
        exit(1)
    print("I: untared {}.".format(para["tarball"]), file=sys.stderr)
    untar_tmp_dir = para["debmake_dir"] + "_tmp/"
    untar_list = glob.glob(untar_tmp_dir + "/*")
    untar_dir_list = glob.glob(untar_tmp_dir + "/*/")
    if len(untar_list) == 1 and len(untar_dir_list) == 1:
        # only one directory found (very likely package-version/
        # move para["debmake_dir"] + "_tmp/" + untar_dir_list[0] to para["debmake_dir"]
        command = "mv -f " + untar_dir_list[0] + " " + para["debmake_dir"] + " ; "
        command += "rm -rf " + untar_tmp_dir
        print("I: $ {}".format(command), file=sys.stderr)
        if subprocess.call(command, shell=True) != 0:
            print("E: failed to move directory. (untar)", file=sys.stderr)
            exit(1)
    else:
        # move para["debmake_dir"] + "_tmp/" to para["debmake_dir"]
        command = "mv -f " + untar_tmp_dir + para["debmake_dir"]
        print("I: $ {}".format(command), file=sys.stderr)
        if subprocess.call(command, shell=True) != 0:
            print("E: failed to move directory. (untar)", file=sys.stderr)
            exit(1)
    return


if __name__ == "__main__":
    print("No test program")
