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
import sys

#######################################################################
# Debug output
#######################################################################
key_parameters = [
    "package",
    "version",
    "revision",
    "tarxz",
    "tarball",
    "native",
    "tar",
    "archive",
    "export",
    "override",
]


#######################################################################
def debug(type, para, msg):
    env = os.environ.get("DEBUG", "")
    if type == "s" and "s" in env:
        # simple debug progress report
        print(msg, file=sys.stderr)
    elif type == "p" and "p" in env:
        print(msg, file=sys.stderr)
        for k in key_parameters:
            print('  para[{}] = "{}"'.format(k, para.get(k, "")), file=sys.stderr)
    elif type == "p" and "P" in env:
        print(msg, file=sys.stderr)
        for k, v in para.items():
            print('  para[{}] = "{}"'.format(k, v), file=sys.stderr)
    elif type == "d" and "d" in env:
        print(msg, file=sys.stderr)
        for deb in para["debs"]:
            print("  Binary Package: {}".format(deb["binpackage"]), file=sys.stderr)
            print("    Architecture: {}".format(deb["arch"]), file=sys.stderr)
            print("    Multi-Arch:   {}".format(deb["multiarch"]), file=sys.stderr)
            print(
                "    Depends:      {}".format(", ".join(deb["depends"])),
                file=sys.stderr,
            )
            print(
                "    Pre-Depends:  {}".format(", ".join(deb["pre-depends"])),
                file=sys.stderr,
            )
            print("    Type:         {}".format(deb["type"]), file=sys.stderr)
    else:
        pass
    return


#######################################################################
# Test code
#######################################################################
if __name__ == "__main__":
    para = {}
    debug("d", para, "**** DEBUG ON! ****")
    para["package"] = "package"
    para["version"] = "1.0"
    para["tarxz"] = "tar.xz"
    para["tarball"] = "package-ver.tar.xz"
    para["foo"] = "bar"
    debug("p", para, "=== debug select para ===")
    debug("P", para, "=== debug all para ===")
