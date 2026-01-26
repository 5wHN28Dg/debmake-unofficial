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
import os.path
import sys

#######################################################################
# Debug output
#######################################################################
key_parameters = [
    "url",
    "package",
    "version",
    "revision",
    "tarz",
    "pre",
    "pkg",
    "ver",
    "ext",
    "tarball",
    "source_dir",
    "debmake_dir",
    "option_z",
    "export",
    "override",
    "native",
]


#######################################################################
# All Debug outputs to STDERR
#######################################################################
def debug(msg, type="s", para=dict()):
    env = os.environ.get("DEBUG", "")
    if type == "s" and "s" in env:
        # simple debug progress report
        print(
            "D: ======== "
            + msg
            + " @ {} ========".format(os.path.basename(os.getcwd())),
            file=sys.stderr,
        )
    if type == "p" and "p" in env:
        print(
            "D: ======== "
            + msg
            + " @ {} ========".format(os.path.basename(os.getcwd())),
            file=sys.stderr,
        )
        for k in key_parameters:
            print('D:   para[{}] = "{}"'.format(k, para.get(k, "")), file=sys.stderr)
    if type == "p" and "P" in env:
        print(
            "D: ======== "
            + msg
            + " @ {} ========".format(os.path.basename(os.getcwd())),
            file=sys.stderr,
        )
        for k, v in para.items():
            print('D:   para[{}] = "{}"'.format(k, v), file=sys.stderr)
    if type == "d" and "d" in env:
        print(
            "D: ======== "
            + msg
            + " @ {} ========".format(os.path.basename(os.getcwd())),
            file=sys.stderr,
        )
        for deb in para["debs"]:
            print("D:   Binary Package: {}".format(deb["binpackage"]), file=sys.stderr)
            print("D:   Architecture:   {}".format(deb["arch"]), file=sys.stderr)
            print("D:   Multi-Arch:     {}".format(deb["multiarch"]), file=sys.stderr)
            print(
                "D:   Depends:        {}".format(", ".join(deb["depends"])),
                file=sys.stderr,
            )
            print(
                "D:   Pre-Depends:    {}".format(", ".join(deb["pre-depends"])),
                file=sys.stderr,
            )
            print("D:   Type:           {}".format(deb["type"]), file=sys.stderr)
    else:
        pass
    return


#######################################################################
# Test code
#######################################################################
if __name__ == "__main__":
    para = {}
    debug("**** DEBUG ON! ****", type="d", para=para)
    para["package"] = "package"
    para["version"] = "1.0"
    para["tarz"] = "tar.xz"
    para["tarball"] = "package-ver.tar.xz"
    para["foo"] = "bar"
    debug("=== debug select para ===", type="p", para=para)
    debug("=== debug all para ===", type="P", para=para)
