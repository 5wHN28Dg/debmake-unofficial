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


def verdir(para):
    """create a source tree directory with upstream version
    verdir: called from debmake.__main__()

    para["debmake_dir"]  = package-version
    para["source_dir"] = parent directory name (the current directory as started)
    para["yes"]     = 0 (default), Ask [Y/n]
    para["yes"]     = 1 if -y, Force Yes
    para["yes"]     = 2 if -yy, Force No

    para['debmake_dir'] and para['source_dir'] are relative paths from
    specifically abspath para["base_dir"].

    Side-effects:
        * para['debmake_dir'] is created if it doesn't exist.
        * Existing para['debmake_dir'] may be replaced with the current content
          after pausing for [Y/n]
    """
    if os.path.isdir(".pc"):
        print('E: .pc/ directory exists.  Stop "debmake -t ..."', file=sys.stderr)
        print(
            "E: Remove applied patches and remove .pc/ directory, first.",
            file=sys.stderr,
        )
        exit(1)
    if not para["debmake_dir"]:
        print(
            'E: para["debmake_dir"] is NULL string. (verdir)',
            file=sys.stderr,
        )
        exit(1)
    if not para["source_dir"]:
        print(
            'E: para["source_dir"] is NULL string. (verdir)',
            file=sys.stderr,
        )
        exit(1)
    #######################################################################
    # make distribution tarball using tar excluding debian/ directory
    # VCS tree are not copied.
    #######################################################################
    # para["source_dir"] = os.path.dirname(os.path.abspath(os.getcwd()))
    if para["debmake_dir"] == para["source_dir"]:
        print("I: already in the versioned parent directory", file=sys.stderr)
    else:
        print(
            'I: para["source_dir"] = "{}"'.format(para["source_dir"]),
            file=sys.stderr,
        )
        print(
            'I: para["debmake_dir"] = "{}"'.format(para["debmake_dir"]),
            file=sys.stderr,
        )
        print(
            "I: copy dir ...",
            file=sys.stderr,
        )
        if os.path.isdir(para["debmake_dir"]):
            print("I: the versioned directory already exists", file=sys.stderr)
            debmake.yn.yn(
                'remove the versioned directory "{}" for tar'.format(
                    para["debmake_dir"]
                ),
                "rm -rf " + para["debmake_dir"],
                para["yes"],
            )
        # copy from para["source_dir"]/. to para["debmake_dir"] (with debian/* data)
        copy_command = [
            "rsync",
            "-av",
            para["source_dir"] + "/.",
            para["debmake_dir"],
        ]
        print("I: $ {}".format(" ".join(copy_command)), file=sys.stderr)
        if subprocess.call(copy_command) != 0:
            print("E: rsync -av failed.", file=sys.stderr)
            exit(1)
    return


if __name__ == "__main__":
    print("No test program")
