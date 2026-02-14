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
import sys

import debmake.sh


def dir_tar(para):
    """create a source tarball excluding the debian/ directory

    para["debmake_dir"]  = package-version
    para["tarball"]      = 'package-version.tar.*z'
    para["tar"]          = True to make tar
    para["option_z"]     = --xz --gzip --bz2 ''
    """
    #######################################################################
    # make distribution tarball using tar excluding debian/ directory
    # VCS tree are not copied.
    #######################################################################
    if not os.path.isdir(para["debmake_dir"]):
        print(
            'E: missing debmake_dir: "{}"'.format(para["debmake_dir"]),
            file=sys.stderr,
        )
        exit(1)
    if not os.path.exists(para["tarball"]):
        # missing tar while excluding VCS and debian directories
        if para["verbose"]:
            command = "tar --verbose "
        else:
            command = "tar "
        command += (
            "--exclude '"
            + para["debmake_dir"]
            + "/debian' "
            + "--anchored --exclude-vcs "
            + para["option_z"]
        )
        command += " -cvf '" + para["tarball"] + "' '" + para["debmake_dir"] + "'"
        debmake.sh.sh(command)
    return


if __name__ == "__main__":
    print("No test program")
