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
import datetime
import glob
import os
import re
import subprocess
import sys

import debmake.debug
import debmake.yn


###########################################################################
# sanity: called from debmake.main()
###########################################################################
def sanity(para):
    #######################################################################
    # Normalize para[] for each exclusive build case (-d -t -a)
    #######################################################################
    if para["archive"]:  # -a
        debmake.debug.debug("p", para, "D: sanity for archive")
        # remote URL fetch of tarball
        re_url = re.match(
            r"(?P<prefix>http://|https://|ftp://)(?P<host>[^:]+)/(?P<tarball>[^/]+)$",
            para["tarball"],
        )
        if re_url:
            url = para["tarball"]
            # re_url.group("prefix"): http:// etc.
            # re_url.group("host"): host URL
            para["tarball"] = re_url.group("tarball")
            if os.path.exists("/usr/bin/wget"):
                command = "/usr/bin/wget " + url
            elif os.path.exists("/usr/bin/curl"):
                command = "/usr/bin/curl -O " + url
            else:
                print("E: please install wget or curl.", file=sys.stderr)
                exit(1)
            print("I: $ {}".format(command), file=sys.stderr)
            if subprocess.call(command, shell=True) != 0:
                print("E: wget/curl failed.", file=sys.stderr)
                exit(1)
            print(
                'I: tarball="{}" from url="{}".'.format(para["tarball"], url),
                file=sys.stderr,
            )
        # src.rpm as tarball: ibus-1.5.5-2.fc19.src.rpm
        re_srcrpm = re.match(
            r"^(?P<srcrpmfile>[^/_-]+)-[0-9]+.*\.(src\.rpm|srpm)$",
            os.path.basename(para["tarball"]),
        )
        if re_srcrpm:
            srcrpm = para["tarball"]
            command = "rpm2cpio " + srcrpm + "|cpio -dium"
            print("I: $ {}".format(command), file=sys.stderr)
            if subprocess.call(command, shell=True) != 0:
                print("E: rpm2cpioc ... | cpio -dium failed.", file=sys.stderr)
                exit(1)
            srcrpm_files = (
                glob.glob(re_srcrpm.group("srcrpmfile") + "*.tar.gz")
                + glob.glob(re_srcrpm.group("srcrpmfile") + "*.tar.bz2")
                + glob.glob(re_srcrpm.group("srcrpmfile") + "*.tar.xz")
            )
            if srcrpm_files:
                para["tarball"] = srcrpm_files[0]
            else:
                print(
                    'E: no tar found in "{}" by unpacking "{}"'.format(
                        para["base_dir"], srcrpm
                    ),
                    file=sys.stderr,
                )
                exit(1)
            print(
                'I: tarball="{}" from unpacked "{}".'.format(para["tarball"], srcrpm),
                file=sys.stderr,
            )
        if not os.path.exists(para["tarball"]):
            print(
                'E: Non-existing tarball "{}" in "{}"'.format(
                    para["tarball"], para["base_dir"]
                ),
                file=sys.stderr,
            )
            exit(1)
        if os.path.abspath(os.path.dirname(para["tarball"])) != os.path.abspath("."):
            command = "cp " + para["tarball"] + " " + os.path.basename(para["tarball"])
            print("I: $ {}".format(command), file=sys.stderr)
            if subprocess.call(command, shell=True) != 0:
                print("E: {} failed.".format(command), file=sys.stderr)
                exit(1)
        para["tarball"] = os.path.basename(para["tarball"])
        if not os.path.exists(para["tarball"]):
            print(
                "E: {} missing in {}.".format(para["tarball"], para["base_dir"]),
                file=sys.stderr,
            )
            exit(1)
        # tarball: package-version.tar.gz or package_version.tar.gz
        re_basetarxz = re.match(
            r"^(?P<package>[^/_]+)[-_](?P<version>[^-/_]+)\.(?P<tarxz>tar\.gz|tar\.bz2|tar\.xz)$",
            para["tarball"],
        )
        # Now para["tarball"] (normalized as filename only) is in the local current directory
        re_origtarxz = re.match(
            r"^(?P<package>[^/_]+)_(?P<version>[^-/_]+)\.orig\.(?P<tarxz>tar\.gz|tar\.bz2|tar\.xz)$",
            para["tarball"],
        )
        re_tarxz = re.match(
            r"^(?P<package>[^/]+)\.(?P<tarxz>tar\.gz|tar\.bz2|tar\.xz)$",
            para["tarball"],
        )
        if re_origtarxz:
            # This needs to e the first to avoid including .orig into version
            if para["package"] == "":
                para["package"] = re_origtarxz.group("package").lower()
            if para["version"] == "":
                para["version"] = re_origtarxz.group("version")
            if para["tarxz"] != re_origtarxz.group("tarxz"):
                print('W: -z "{}" ignored'.format(para["tarxz"]), file=sys.stderr)
                para["tarxz"] = re_origtarxz.group("tarxz")
        elif re_basetarxz:
            if para["package"] == "":
                para["package"] = re_basetarxz.group("package").lower()
            if para["version"] == "":
                para["version"] = re_basetarxz.group("version")
            if para["tarxz"] != re_basetarxz.group("tarxz"):
                print(
                    'W: specified -z "{}" ignored'.format(para["tarxz"]),
                    file=sys.stderr,
                )
                para["tarxz"] = re_basetarxz.group("tarxz")
        elif re_tarxz:
            if para["package"] == "":
                para["package"] = re_tarxz.group("package").lower()
            if para["tarxz"] != re_tarxz.group("tarxz"):
                print('W: -z "{}" ignored'.format(para["tarxz"]), file=sys.stderr)
                para["tarxz"] = re_tarxz.group("tarxz")
        else:
            print(
                "E: Non-parsable local tarball name {}".format(para["tarball"]),
                file=sys.stderr,
            )
        print(
            "I: content of tarball={} is processed as:".format(para["tarball"]),
            file=sys.stderr,
        )
        print(
            'I: $ debmake -p "{}" -u "{}" -z "{}" ...'.format(
                para["package"], para["version"], para["tarxz"]
            ),
            file=sys.stderr,
        )
    #######################################################################
    if not para["archive"]:  # not -a (-t or -d or normal in source tree)
        debmake.debug.debug("p", para, "D: sanity for non-archive")
        if os.path.isfile("debian/changelog"):
            # check changelog for package/version/revision
            with open("debian/changelog", mode="r", encoding="utf-8") as f:
                line = f.readline()
            if para["native"]:
                debmake.debug.debug(
                    "s",
                    para,
                    'D: DEBUG=s @sanity(native): debian/changelog="{}"'.format(line),
                )
                pkgver = re.match(
                    r"^(?P<package>[^ \t]+)[ \t]+\((?P<version>[^()]+)\)", line
                )
                if pkgver:
                    if para["package"] == "":
                        para["package"] = pkgver.group("package").lower()
                    elif para["package"] != pkgver.group("package").lower():
                        print(
                            'W: -p "{}" conflicts with debian/changelog in source tree'.format(
                                para["package"]
                            ),
                            file=sys.stderr,
                        )
                        exit(1)
                    else:
                        para["package"] = pkgver.group("package").lower()
                    if para["version"] == "":
                        para["version"] = pkgver.group("version")
                    elif para["version"] != pkgver.group("version"):
                        print(
                            'W: -u "{}" conflicts with debian/changelog in source tree'.format(
                                para["version"]
                            ),
                            file=sys.stderr,
                        )
                        exit(1)
                    else:
                        para["version"] = pkgver.group("version")
                else:
                    print('E: changelog start with "{}"'.format(line), file=sys.stderr)
                    exit(1)
                debmake.debug.debug(
                    "s", para, "D: DEBUG=s @sanity(native): set by debian/changelog as"
                )
                debmake.debug.debug(
                    "s",
                    para,
                    'D: DEBUG=s $ debmake -n -p "{}" -u "{}" ...'.format(
                        para["package"], para["version"]
                    ),
                )
            else:  # non-native
                debmake.debug.debug(
                    "s",
                    para,
                    'D: DEBUG=s @sanity(non-native): debian/changelog="{}"'.format(
                        line
                    ),
                )
                pkgver = re.match(
                    r"^(?P<package>[^ \t]+)[ \t]+\(?P<version>([^()]+)-(?P<revision>[^-()]+)\)",
                    line,
                )
                if pkgver:
                    if para["package"] == "":
                        para["package"] = pkgver.group("package").lower()
                    elif para["package"] != pkgver.group("package").lower():
                        print(
                            'W: -p "{}" conflicts with debian/changelog in source tree'.format(
                                para["package"]
                            ),
                            file=sys.stderr,
                        )
                        exit(1)
                    else:
                        para["package"] = pkgver.group("package").lower()
                    if para["version"] == "":
                        para["version"] = pkgver.group("version")
                    elif para["version"] != pkgver.group("version"):
                        print(
                            'W: -u "{}" conflicts with debian/changelog in source tree'.format(
                                para["version"]
                            ),
                            file=sys.stderr,
                        )
                        exit(1)
                    else:
                        para["version"] = pkgver.group("version")
                    if para["revision"] == "":
                        para["revision"] = pkgver.group("revision")
                    elif para["revision"] != pkgver.group("revision"):
                        print(
                            'W: -r "{}" conflicts with debian/changelog in source tree'.format(
                                para["revision"]
                            ),
                            file=sys.stderr,
                        )
                        exit(1)
                    else:
                        para["revision"] = pkgver.group("revision")
                else:
                    print(
                        'E: changelog start with "{}" and parsing failed'.format(line),
                        file=sys.stderr,
                    )
                    exit(1)
                debmake.debug.debug(
                    "s",
                    para,
                    "D: DEBUG=s @sanity(non-native): set by debian/changelog as",
                )
                debmake.debug.debug(
                    "s",
                    para,
                    'D: DEBUG=s $ debmake -p "{}" -u "{}" -r "{}" ...'.format(
                        para["package"], para["version"], para["revision"]
                    ),
                )
        # last resort for para["package"] from para["source_dir"]
        if para["package"] == "":
            pkgver = re.match(
                r"^(?P<package>[^-_/].+)-(?P<version>[0-9][^-]*)$",
                os.path.basename(para["source_dir"]),
            )
            if pkgver:
                para["package"] = pkgver.group("package").lower()
                if para["version"] == "":
                    para["version"] = pkgver.group("version")
            else:
                para["package"] = os.path.basename(para["source_dir"].lower())
        if para["version"] == "":
            para["version"] = datetime.datetime.now(datetime.timezone.utc).strftime(
                "0~%y%m%d%H%M"
            )
        if para["native"]:
            debmake.debug.debug("s", para, "D: DEBUG=s @sanity(native): finally set as")
            debmake.debug.debug(
                "s",
                para,
                'D: DEBUG=s $ debmake -n -p "{}" -u "{}" ...'.format(
                    para["package"], para["version"]
                ),
            )
        else:
            if para["revision"] == "":
                para["revision"] = "1"
            debmake.debug.debug(
                "s", para, "D: DEBUG=s @sanity(non-native): finally set as"
            )
            debmake.debug.debug(
                "s",
                para,
                'D: DEBUG=s $ debmake -p "{}" -u "{}" -r "{}" ...'.format(
                    para["package"], para["version"], para["revision"]
                ),
            )
    #######################################################################
    # check tar in parent directory
    if para["archive"]:
        pass
    elif para["dist"]:
        print(
            "I: upstream tarball in the parent is not required: --dist",
            file=sys.stderr,
        )
    elif para["tar"]:
        print(
            "I: upstream tarball in the parent is not required: --tar",
            file=sys.stderr,
        )
    elif para["native"]:
        print(
            "I: upstream tarball in the parent is not required for native package",
            file=sys.stderr,
        )
    else:  # normal non-native case
        # upstream tarball in the parent is required for non-native package
        if os.path.exists("../" + para["package"] + "-" + para["version"] + ".tar.xz"):
            para["tarxz"] = "tar.xz"
            para["tarball"] = (
                para["package"] + "-" + para["version"] + "." + para["tarxz"]
            )
        elif os.path.exists(
            "../" + para["package"] + "-" + para["version"] + ".tar.gz"
        ):
            para["tarxz"] = "tar.gz"
            para["tarball"] = (
                para["package"] + "-" + para["version"] + "." + para["tarxz"]
            )
        elif os.path.exists(
            "../" + para["package"] + "-" + para["version"] + ".tar.bz2"
        ):
            para["tarxz"] = "tar.bz2"
            para["tarball"] = (
                para["package"] + "-" + para["version"] + "." + para["tarxz"]
            )
        elif os.path.exists(
            "../" + para["package"] + "_" + para["version"] + ".orig.tar.xz"
        ):
            para["tarxz"] = "tar.xz"
            para["tarball"] = para["package"] + "_" + para["version"] + ".orig.tar.xz"
        elif os.path.exists(
            "../" + para["package"] + "_" + para["version"] + ".orig.tar.gz"
        ):
            para["tarxz"] = "tar.gz"
            para["tarball"] = para["package"] + "_" + para["version"] + ".orig.tar.gz"
        elif os.path.exists(
            "../" + para["package"] + "_" + para["version"] + ".orig.tar.bz2"
        ):
            para["tarxz"] = "tar.bz2"
            para["tarball"] = para["package"] + "_" + para["version"] + ".orig.tar.bz2"
        else:
            print(
                'W: upstream tarball missing (non-native package): package="{}", version="{}"'.format(
                    para["package"], para["version"]
                ),
                file=sys.stderr,
            )
            debmake.yn.yn(
                'Execute as "debmake --tar ..." to generate the upstream tarball".',
                "",
                para["yes"],
            )
            para["tar"] = True
    #######################################################################
    # set fall back values or exit
    if para["package"] == "":
        print(
            'E: para["package"] is unset after sanity check',
            file=sys.stderr,
        )
        exit(1)
    # set version to 0~YYMMDDHHmm
    if para["version"] == "":
        print(
            'E: para["version"] is unset after sanity check',
            file=sys.stderr,
        )
        exit(1)
    if para["tarxz"] == "":
        para["tarxz"] = "tar.xz"
    if para["revision"] == "":
        para["revision"] = "1"
    if para["tarball"] == "":
        para["tarball"] = para["package"] + "-" + para["version"] + "." + para["tarxz"]
    para["debmake_dir"] = para["package"] + "-" + para["version"]
    #######################################################################
    # Dynamic content with package name etc.
    #######################################################################
    para["section"] = "unknown"
    para["priority"] = "optional"
    para["homepage"] = "<insert the upstream URL, if relevant>"
    para["vcsvcs"] = "https://salsa.debian.org/debian/" + para["package"] + ".git"
    para["vcsbrowser"] = "https://salsa.debian.org/debian/" + para["package"]
    return para
