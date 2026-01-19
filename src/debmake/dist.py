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
import glob
import os
import os.path
import re
import subprocess
import sys

import debmake.yn


###########################################################################
# dist: called from debmake.main()
#  - This set para["tarball"] value as a part of return value para
###########################################################################
def dist(para):
    distdir = "."
    print('I: make the upstream tarball with "make dist" equivalents', file=sys.stderr)
    #######################################################################
    # make distribution tarball using the Autotools
    #######################################################################
    if os.path.isfile("configure.ac") and os.path.isfile("Makefile.am"):
        command = 'autoreconf -ivf && ./configure --prefix "/usr" && make distcheck'
        print("I: $ {}".format(command), file=sys.stderr)
        if subprocess.call(command, shell=True) != 0:
            print("E: autotools failed.", file=sys.stderr)
            exit(1)
        distdir = "."
    #######################################################################
    # make distribution tarball using setup.py -- disabled
    #######################################################################
    # elif os.path.isfile("setup.py"):
    #     # Python distutils
    #     with open("setup.py", mode="r", encoding="utf-8") as f:
    #         line = f.readline()
    #     if re.search("python3", line):
    #         # http://docs.python.org/3/distutils/
    #         if para["tarxz"] == "tar.xz":
    #             command = (
    #                 "python3 setup.py sdist --owner=root --group=root --formats=xztar"
    #             )
    #         elif para["tarxz"] == "tar.bz2":
    #             command = (
    #                 "python3 setup.py sdist --owner=root --group=root --formats=bztar"
    #             )
    #         else:
    #             command = (
    #                 "python3 setup.py sdist --owner=root --group=root --formats=gztar"
    #             )
    #     else:
    #         # http://docs.python.org/2/distutils/
    #         if para["tarxz"] == "tar.xz":
    #             command = (
    #                 "python setup.py sdist --owner=root --group=root --formats=xztar"
    #             )
    #         elif para["tarxz"] == "tar.bz2":
    #             command = (
    #                 "python setup.py sdist --owner=root --group=root --formats=bztar"
    #             )
    #         else:
    #             command = (
    #                 "python setup.py sdist --owner=root --group=root --formats=gztar"
    #             )
    #     print("I: $ {}".format(command), file=sys.stderr)
    #     if subprocess.call(command, shell=True) != 0:
    #         print("E: setup.py failed.", file=sys.stderr)
    #         exit(1)
    #     distdir = "dist"
    #######################################################################
    # make distribution tarball using Build.PL
    #######################################################################
    elif os.path.isfile("Build.PL"):
        # perl Build.PL
        command = (
            "perl Build.PL && ./Build distcheck && ./Build disttest && ./Build dist"
        )
        print("I: $ {}".format(command), file=sys.stderr)
        if subprocess.call(command, shell=True) != 0:
            print("E: perl Build.PL failed.", file=sys.stderr)
            exit(1)
        distdir = "."
    #######################################################################
    # make distribution tarball using Makefile.PL
    #######################################################################
    elif os.path.isfile("Makefile.PL"):
        # perl Makefile.PL
        command = "perl Makefile.PL && make dist"
        print("I: $ {}".format(command), file=sys.stderr)
        if subprocess.call(command, shell=True) != 0:
            print("E: perl Makefile.PL failed.", file=sys.stderr)
            exit(1)
        distdir = "."
    #######################################################################
    # make distribution tarball for other sources
    #######################################################################
    else:
        if os.path.isfile("CMakeLists.txt"):
            # CMake source tree
            print("E: CMake. Use --tar (-t).", file=sys.stderr)
            exit(1)
        else:
            # Non standard source tree
            print("E: unsupported for --dist (-d). Use --tar (-t).", file=sys.stderr)
            exit(1)
    #######################################################################
    # set version by the tarball name
    #######################################################################
    somepackage1 = distdir + "/*.tar.xz"
    somepackage2 = distdir + "/*.tar.gz"
    somepackage3 = distdir + "/*.tar.bz2"
    globbed_files = (
        glob.glob(somepackage1) + glob.glob(somepackage2) + glob.glob(somepackage3)
    )
    if not globbed_files:
        print(
            "E: tarball unfound after --dist (globbed_files is empty)",
            file=sys.stderr,
        )
        exit(1)
    for file in globbed_files:
        print(
            "I: -> {} created as {} in --dist build tree".format(
                os.path.basename(file), file
            ),
            file=sys.stderr,
        )
    tarball_abspath_by_dist = os.path.abspath(globbed_files[0])
    tarball_by_dist = os.path.basename(tarball_abspath_by_dist)
    print(
        'I: "{}" tarball picked.'.format(tarball_by_dist),
        file=sys.stderr,
    )
    re_match_package_version = re.match(
        r"(?P<package>[^_]*)[-_](?P<version>[^-_]*)\.(?P<tarxz>tar\..{2,3})$",
        tarball_by_dist,
    )
    re_match_package = re.match(
        r"(?P<package>[^_]*)\.(?P<tarxz>tar\..{2,3})$",
        tarball_by_dist,
    )
    tarball_by_dist_package = ""
    tarball_by_dist_version = ""
    tarball_by_dist_tarxz = ""
    if re_match_package_version:
        tarball_by_dist_package = re_match_package_version.group("package")
        tarball_by_dist_version = re_match_package_version.group("version")
        tarball_by_dist_tarxz = re_match_package_version.group("tarxz")
        if para["package"] == "":
            para["package"] = tarball_by_dist_package.lower()
        if para["version"] == "":
            para["version"] = tarball_by_dist_version
        if para["tarxz"] == "":
            para["tarxz"] = tarball_by_dist_tarxz
    elif re_match_package:
        tarball_by_dist_package = re_match_package.group("package")
        tarball_by_dist_tarxz = re_match_package.group("tarxz")
        if para["package"] == "":
            para["package"] = tarball_by_dist_package.lower()
        if para["version"] == "":
            para["version"] = "1"
        if para["tarxz"] == "":
            para["tarxz"] = tarball_by_dist_tarxz
    else:
        print(
            'E: tarball unfound after --dist (globbed_files="{}")'.format(
                globbed_files
            ),
            file=sys.stderr,
        )
        exit(1)
    if para["package"] == "" or para["version"] == "" or para["tarxz"] == "":
        print(
            'E: para["package"] = "{}", para["version"] = "{}", para["tarxz"] = "{} after --dist'.format(
                para["package"], para["version"], para["tarxz"]
            ),
            file=sys.stderr,
        )
        exit(1)
    if (re_match_package_version or re_match_package) and (
        para["package"] != tarball_by_dist_package
        or para["version"] != tarball_by_dist_version
        or para["tarxz"] != tarball_by_dist_tarxz
    ):
        print(
            'W: "{}-{}.{}" tarball expected from -p/-u/-z options or debian/changelog.'.format(
                para["package"], para["version"], para["tarxz"]
            ),
            file=sys.stderr,
        )
        print(
            "W: you may update program name and version in source as needed.",
            file=sys.stderr,
        )
    if (para["package"] + "-" + para["version"]) == os.path.basename(os.getcwd()):
        print(
            'E: "debmake --dist" should not be used for the source tree checked out to versioned {}-{}/" direcory.'.format(
                para["package"], para["version"]
            ),
            file=sys.stderr,
        )
        print(
            'E: Use something like "{}/" direcory for Git checkout.'.format(
                para["package"]
            ),
            file=sys.stderr,
        )
        exit(1)

    #######################################################################
    # create properly named tarball in the parent directory
    #######################################################################
    # para["base_dir"] = os.path.abspath("..") # tar.xz file here
    # para["source_dir"] = os.path.basename(os.getcwd()) # git checkout here
    para["tarball"] = para["package"] + "-" + para["version"] + "." + para["tarxz"]
    if os.path.exists("../" + para["tarball"]):
        msg = 'Overwrite existing "{}"'.format("../" + para["tarball"])
        debmake.yn.yn(msg, "rm -f ../" + para["tarball"], para["yes"])
    # cp -f parent/dist/foo-1.0.tar.gz foo-1.0.tar.gz
    command = "cp -f " + tarball_abspath_by_dist + " ../" + para["tarball"]
    print("I: $ {}".format(command), file=sys.stderr)
    if subprocess.call(command, shell=True) != 0:
        print("E: failed to copy", file=sys.stderr)
        exit(1)
    return


if __name__ == "__main__":
    print("No test program")
