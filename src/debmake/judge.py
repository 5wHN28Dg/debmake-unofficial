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
import subprocess
import sys


#######################################################################
def judge(para):
    command = "fakeroot dpkg-depcheck -m -C -o ../{0}.depcheck.log -f -catch-alternatives debian/rules install >../{0}.build.log 2>&1".format(
        para["package"]
    )
    print("I: $ {}".format(command), file=sys.stderr)
    if subprocess.call(command, shell=True) != 0:
        print("E: failed to run dpkg-depcheck.", file=sys.stderr)
        exit(1)
    command = r'LANG=C ; sed -e "1d" < ../{0}.depcheck.log | sort >../{0}.build-dep.log'.format(
        para["package"]
    )
    print("I: $ {}".format(command), file=sys.stderr)
    if subprocess.call(command, shell=True) != 0:
        print("E: failed to run sort on build-dep.", file=sys.stderr)
        exit(1)
    if len(para["debs"]) == 1:
        bpackage = para["debs"][0]["package"]
        command = (
            r"LANG=C; find debian/"
            + bpackage
            + r' -type f 2>&1 | sed -e "s/^debian\/'
            + bpackage
            + r'\///" | sort >../{0}.install.log'.format(para["package"])
        )
        print("I: $ {}".format(command), file=sys.stderr)
        if subprocess.call(command, shell=True) != 0:
            print("E: failed to run find debian/{}.".format(bpackage), file=sys.stderr)
            exit(1)
    elif len(para["debs"]) > 1:
        command = r'LANG=C; find debian/tmp -type f 2>&1 | sed -e "s/^debian\/tmp\///" | sort >../{0}.install.log'.format(
            para["package"]
        )
        print("I: $ {}".format(command), file=sys.stderr)
        if subprocess.call(command, shell=True) != 0:
            print("E: failed to run find debian/tmp.", file=sys.stderr)
            exit(1)
    else:
        print("E: No binary package was generated.", file=sys.stderr)
        exit(1)
    return


#######################################################################
# Test script
#######################################################################
if __name__ == "__main__":
    print("no test")
