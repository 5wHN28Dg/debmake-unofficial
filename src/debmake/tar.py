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
import os
import subprocess
import sys

import debmake.yn


def tar(para):
    """create a source tarball excluding the debian/ directory
    tar: called from debmake.__main__()

    para["tarball"]   = 'package-version.tar.*z'
    para["tarxz"]   = one of 'tar.gz', 'tar.bz2' or 'tar.xz'
    para["debmake_dir"]  = package-version
    para["yes"]     = 0 (default), Ask [Y/n]
    para["yes"]     = 1 if -y, Force Yes
    para["yes"]     = 2 if -yy, Force No

    para['debmake_dir'] is a relative path from
    specifically abspath para["base_dir"].
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
    #######################################################################
    # make distribution tarball using tar excluding debian/ directory
    # VCS tree are not copied.
    #######################################################################
    if os.path.isdir(para["debmake_dir"]):
        print(
            "I: the parent directory is properly named with version.", file=sys.stderr
        )
    # tar while excluding VCS and debian directories
    tar_command = [
        "tar",
        "--exclude",
        para["debmake_dir"] + "/debian",
        "--anchored",
        "--exclude-vcs",
    ]
    if para["tarxz"] == "tar.gz":
        tar_command.append("--gzip")
    elif para["tarxz"] == "tar.bz2":
        tar_command.append("--bzip2")
    elif para["tarxz"] == "tar.xz":
        tar_command.append("--xz")
    else:
        print('E: Wrong file format "{}".'.format(para["tarxz"]), file=sys.stderr)
        exit(1)
    tar_command.append("-cvf")
    tar_command.append(para["tarball"])
    tar_command.append(para["debmake_dir"])
    if os.path.exists(para["tarball"]):
        debmake.yn.yn(
            'Overwite existing "{}"'.format(para["tarball"]),
            "rm -rf " + para["tarball"],
            para["yes"],
        )
    print("I: $ {}".format(" ".join(tar_command)), file=sys.stderr)
    if subprocess.call(tar_command) != 0:
        print("E: tar failed {}.".format(para["tarball"]), file=sys.stderr)
        exit(1)
    print("I: {} tarball made".format(para["tarball"]), file=sys.stderr)
    return


if __name__ == "__main__":
    print("No test program")
