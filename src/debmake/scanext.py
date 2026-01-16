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
import collections
import itertools
import os
import re
import sys

###################################################################
# Define constants
###################################################################
ext_to_type = {
    "pl": "perl",
    "PL": "perl",
    "pm": "perl",
    "py": "python3",
    "pyc": "python3",
    "rb": "ruby",
    "javac": "java",
    "js": "javascript",
    "ml": "ocml",
    "vala": "vala",
    "h": "c",
    "cpp": "c",
    "CPP": "c",
    "cc": "c",
    "C": "c",
    "cxx": "c",
    "CXX": "c",
    "c++": "c",
    "hh": "c",
    "H": "c",
    "hxx": "c",
    "Hxx": "c",
    "HXX": "c",
    "hpp": "c",
    "h++": "c",
    "asm": "c",
    "s": "c",
    "S": "c",
    "TXT": "text",
    "txt": "text",
    "doc": "text",
    "html": "text",
    "htm": "text",
    "xml": "text",
    "dbk": "text",
    "dtd": "text",
    "odt": "text",
    "sda": "text",
    "sdb": "text",
    "sdc": "text",
    "sdd": "text",
    "sds": "text",
    "sdw": "text",
    "a": "binary",
    "class": "binary",
    "jar": "binary",
    "exe": "binary",
    "com": "binary",
    "dll": "binary",
    "obj": "binary",
    "zip": "archive",
    "tar": "archive",
    "cpio": "archive",
    "afio": "archive",
    "jpeg": "media",
    "jpg": "media",
    "m4a": "media",
    "png": "media",
    "gif": "media",
    "GIF": "media",
    "svg": "media",
    "ico": "media",
    "mp3": "media",
    "ogg": "media",
    "ttf": "media",
    "TTF": "media",
    "otf": "media",
    "OTF": "media",
    "wav": "media",
}
###################################################################
# re.search file name extension (ignoring compression)

re_ext = re.compile(r"\.(?P<ext>[^.]+)(?:\.in|\.gz|\.bz2|\.xz|\.Z\|\.z|~)*$")


###################################################################
# Scan source to count all program related extensions
###################################################################
def scanext():
    # exclude some non program source extensions
    excluded_ext_type = ["text", "binary", "archive", "media"]
    ext_type_list = []
    # ext_type_list : representative code type
    # binary means possible non-DFSG component
    for dir, subdirs, files in os.walk("."):
        for file in files:
            # dir iterates over ./ ./foo ./foo/bar/ ./foo/bar/baz ...
            filepath = os.path.join(dir[2:], file)
            if os.path.islink(filepath):
                pass  # skip symlink (both for file and dir)
            else:
                re_ext_match = re_ext.search(file)
                if re_ext_match:
                    ext = re_ext_match.group("ext")
                    if ext in ext_to_type.keys():
                        ext_type = ext_to_type[ext]
                    else:
                        ext_type = ext
                    # extrep is normalized extension
                    if ext_type not in excluded_ext_type:
                        ext_type_list.append(ext_type)
        # do not descend to VCS dirs and debian/ directory
        for vcs in ["CVS", ".svn", ".pc", ".git", ".hg", ".bzr", "debian"]:
            if vcs in subdirs:
                subdirs.remove(vcs)  # skip VCS
    # Assume Python 3.7 or newer to preserve item order for dict
    ext_type_counter = dict(
        reversed(
            sorted(collections.Counter(ext_type_list).items(), key=lambda item: item[1])
        )
    )
    n_max_files = 3
    for ext_type in itertools.islice(ext_type_counter.keys(), 0, n_max_files):
        print(
            "I: ext_type = {0:<16} {1:>8} files".format(
                ext_type, ext_type_counter[ext_type]
            ),
            file=sys.stderr,
        )
    return ext_type_counter


#######################################################################
# Test script
#######################################################################
if __name__ == "__main__":
    ext_type_counter = scanext()
    print("I: ext_type ====================== file count", file=sys.stderr)
    for ext_type, count in ext_type_counter.items():
        print("   ext_type = {0:<16} {1:>8} files".format(ext_type, count))
