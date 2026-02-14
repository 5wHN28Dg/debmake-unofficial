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
import os.path
import sys

import debmake.sh


###########################################################################
# origtar: called from debmake.main()
###########################################################################
def tar_orig(para):
    #######################################################################
    # make package_version.orig.tar.xz (as symlink)
    #######################################################################
    if not os.path.exists(para["tarball"]):
        print(
            'E: missing "{}".'.format(para["tarball"]),
            file=sys.stderr,
        )
        exit(1)
    origtargz = para["package"] + "_" + para["version"] + ".orig." + para["tarz"]
    if para["tarball"] == origtargz:
        print(
            'I: use the existing "{}" as the upstream orig.tar.?z'.format(
                para["tarball"]
            ),
        )
    else:
        command = "ln -sf '" + para["tarball"] + "' '" + origtargz + "'"
        debmake.sh.sh(command)
    return


if __name__ == "__main__":
    para = dict()
    para["tarball"] = sys.argv[1]
    para["package"] = os.path.splitext(os.path.basename(para["tarball"]))[0].lower()
    para["version"] = "1.0"
    para["tarz"] = "tar.xz"
    tar_orig(para)
