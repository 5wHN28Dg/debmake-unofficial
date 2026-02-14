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

import debmake.sh
import debmake.yn


def dir_debmake(para):
    """create a source tree at package-version

    para["debmake_dir"]  = package-version
    para["source_dir"] = path/to/tree
    para["yes"]     = 0 (default), Ask [Y/n]

    Side-effects:
        * para['debmake_dir'] is created if it doesn't exist.
        * Existing para['debmake_dir'] may be replaced with the current content
          after pausing for [Y/n]
    """
    if os.path.abspath(para["debmake_dir"]) == os.path.abspath(para["source_dir"]):
        print(
            'I: already in the package-version form: "{}"'.format(para["debmake_dir"])
        )
    else:
        if os.path.isdir(para["debmake_dir"]):
            debmake.yn.yn(
                'remove the old versioned directory "{}"'.format(para["debmake_dir"]),
                "rm -rf '" + para["debmake_dir"] + "'",
                para["yes"],
            )
        # copy from para["source_dir"]/. to para["debmake_dir"] (with debian/* data)
        if para["verbose"]:
            command = "cp -dRv "
        else:
            command = "cp -dR "
        command += "'" + para["base_dir"] + "/" + para["source_dir"] + "/.' '"
        command += para["debmake_dir"] + "'"
        debmake.sh.sh(command)
    return


if __name__ == "__main__":
    import sys

    para = dict()
    para["source_dir"] = sys.argv[1]
    para["debmake_dir"] = sys.argv[2]
    para["yes"] = 0
    dir_debmake(para)
