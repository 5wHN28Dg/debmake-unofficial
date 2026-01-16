#!/usr/bin/python3
# vim:se tw=0 sts=4 ts=4 et ai:
"""
Copyright © 2014-2018 Osamu Aoki

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
import importlib.resources
import os
import subprocess
import sys
import time

import debmake
import debmake.analyze
import debmake.debian
import debmake.debs
import debmake.debug
import debmake.dist
import debmake.judge
import debmake.origtar
import debmake.para
import debmake.sanity
import debmake.tar
import debmake.untar
import debmake.verdir


#######################################################################
# main program
#######################################################################
def main():
    #######################################################################
    # set parameters from commandline etc.
    #######################################################################
    para = {}  # effective global variable storage
    debmake.debug.debug("s", para, "D: PYTHONPATH = {} ".format(":".join(sys.path)))
    debmake.debug.debug(
        "s", para, "D: DEBMAKE_PATH = {}".format(importlib.resources.files("debmake"))
    )
    para["program_name"] = debmake.__programname__
    para["program_version"] = debmake.__version__
    para["program_copyright"] = debmake.__copyright__
    para["program_license"] = debmake.__license__
    print(
        "I: {} (version: {})".format(para["program_name"], para["program_version"]),
        file=sys.stderr,
    )
    print(
        "I: {}".format(para["program_copyright"]),
        file=sys.stderr,
    )
    para["start_dir"] = os.path.abspath(".")
    para["home_dir"] = os.path.expanduser("~")  # this is constant
    debmake.debug.debug(
        "s",
        para,
        "D: the starting directory @ ~/{}".format(
            os.path.relpath(".", para["home_dir"])
        ),
    )
    debmake.debug.debug(
        "s", para, "D: PATHs below are relative to the starting directory"
    )
    para["base_dir"] = os.path.relpath("..", para["home_dir"])  # tar.xz file here
    para["source_dir"] = os.path.relpath(".", para["home_dir"])  # untared source here
    para["debmake_dir"] = ""  # debian/* generated here
    para["date"] = time.strftime("%a, %d %b %Y %H:%M:%S %z")
    para["shortdate"] = time.strftime("%d %b %Y")
    para["year"] = time.strftime("%Y")
    para["standard_version"] = debmake.__debian_policy__  # Debian policy_
    para["compat"] = debmake.__debian_compat__  # debhelper
    para["build_depends"] = {"debhelper-compat (= " + para["compat"] + ")"}
    para["desc"] = ""
    para["desc_long"] = ""
    para["export"] = set()
    para["override"] = set()
    para["data_path"] = "{}/data/".format(importlib.resources.files("debmake"))
    para["tarball"] = ""
    para["package"] = ""
    para["version"] = ""
    para["revision"] = ""
    para["tarxz"] = ""
    para["debs"] = []
    #######################################################################
    # parse command argument
    #######################################################################
    debmake.debug.debug(
        "s", para, "D: @pre-para @ {}".format(os.path.relpath(".", para["start_dir"]))
    )
    debmake.para.para(para)
    debmake.debug.debug("p", para, "D: @post-para")
    #######################################################################
    # -v: print version and copyright notice
    #######################################################################
    if para["print_version"]:
        print(
            para["program_license"],
            file=sys.stderr,
        )
        return
    #######################################################################
    # sanity check parameters without digging deep into source tree
    #######################################################################
    debmake.debug.debug(
        "s", para, "D: @pre-sanity @ {}".format(os.path.relpath(".", para["start_dir"]))
    )
    debmake.sanity.sanity(para)
    debmake.debug.debug("p", para, "D: @post-sanity")
    # para["debmake_dir"] is set according to updated para[...]
    para["debmake_dir"] = para["package"] + "-" + para["version"]
    #######################################################################
    # -d: make dist (with upstream buildsystem dist/sdist target)
    #######################################################################
    if para["dist"]:
        debmake.debug.debug(
            "s",
            para,
            "D: @pre-dist @ {}".format(os.path.relpath(".", para["start_dir"])),
        )
        debmake.dist.dist(para)
        debmake.debug.debug("p", para, "D: @post-dist")
        print("I: $ cd ..", file=sys.stderr)
        os.chdir("..")
        # tarball directory
    #######################################################################
    # -a, -d: extract archive from tarball (tar -xvzf)
    #######################################################################
    if para["archive"] or para["dist"]:
        # tarball directory
        debmake.debug.debug(
            "s",
            para,
            "D: @pre-untar @ {}".format(os.path.relpath(".", para["start_dir"])),
        )
        debmake.untar.untar(para)
        print("I: $ cd {}".format(para["debmake_dir"]), file=sys.stderr)
        os.chdir(para["debmake_dir"])
        # on para["debmake_dir"]=package-version path
    #######################################################################
    # debmake source tree in package-version/
    #######################################################################
    if (not para["native"]) and (
        para["debmake_dir"] != os.path.basename(os.path.abspath("."))
    ):
        # normal non-native packaging not on para["debmake_dir"]=package-version path
        print("I: $ cd ..", file=sys.stderr)
        os.chdir("..")
        debmake.debug.debug(
            "s",
            para,
            "D: @pre-verdir @ {}".format(os.path.relpath(".", para["start_dir"])),
        )
        debmake.verdir.verdir(para)
        print("I: $ cd {}".format(para["debmake_dir"]), file=sys.stderr)
        os.chdir(para["debmake_dir"])
        # on para["debmake_dir"]=package-version path
    #######################################################################
    # -t: make tar (with "tar --exclude=debian" command)
    #######################################################################
    if para["tar"]:
        # on para["source_dir"]=any directory made on tarball directory
        print(
            'I: make the upstream tarball with "tar --exclude=debian"', file=sys.stderr
        )
        print("I: $ cd ..", file=sys.stderr)
        os.chdir("..")
        debmake.debug.debug(
            "s",
            para,
            "D: @pre-tar @ {}".format(os.path.relpath(".", para["start_dir"])),
        )
        debmake.tar.tar(para)
        debmake.debug.debug("p", para, "D: @post-tar")
        print("I: $ cd {}".format(para["debmake_dir"]), file=sys.stderr)
        os.chdir(para["debmake_dir"])
        # on para["debmake_dir"]=package-version path
    #######################################################################
    # always: generate orig tarball if missing and non-native package
    #######################################################################
    # on para["debmake_dir"]=package-version path
    if para["native"]:
        print(
            'I: Native Debian package pkg="{}", ver="{}"'.format(
                para["package"], para["version"]
            ),
            file=sys.stderr,
        )
    else:
        print(
            'I: Non-native Debian package pkg="{}", ver="{}", rev="{}"'.format(
                para["package"], para["version"], para["revision"]
            ),
            file=sys.stderr,
        )
        print("I: $ cd ..", file=sys.stderr)
        os.chdir("..")
        # ln -sf Foo-1.0.tar.gz foo_1.0.orig.tar.gz
        debmake.debug.debug(
            "s",
            para,
            "D: @pre-origtar (non-native all) @ {}".format(
                os.path.relpath(".", para["start_dir"])
            ),
        )
        debmake.origtar.origtar(para)
        print("I: $ cd {}".format(para["debmake_dir"]), file=sys.stderr)
        os.chdir(para["debmake_dir"])
        # on para["debmake_dir"]=package-version path
    #######################################################################
    # -q: quit here before generating template debian/* package files
    #######################################################################
    if para["quitearly"]:
        print("I: quit early after making the upstream tarball.", file=sys.stderr)
        exit(0)
    #######################################################################
    # Prep to create debian/* package files
    #######################################################################
    # on para["debmake_dir"]=package-version path
    debmake.debug.debug(
        "s", para, "D: @pre-debs @ {}".format(os.path.relpath(".", para["start_dir"]))
    )
    debmake.debs.debs(para)
    debmake.debug.debug("d", para, "D: @post-debs")
    debmake.debug.debug(
        "s",
        para,
        "D: @pre-analyze @ {}".format(os.path.relpath(".", para["start_dir"])),
    )
    debmake.analyze.analyze(para)
    debmake.debug.debug("p", para, "D: @post-analyze")
    debmake.debug.debug("d", para, "D: @post-analyze")
    # debmake.gui()          # GUI setting
    # debmake.debug.debug("P", para, "D: after gui")
    #######################################################################
    # Make debian/* package files
    #######################################################################
    print("I: make debian/* template files", file=sys.stderr)
    debmake.debian.debian(para)
    #######################################################################
    # Make Debian package(s)
    #######################################################################
    if para["judge"]:
        debmake.debug.debug(
            "s",
            para,
            "D: @pre-judge @ {}".format(os.path.relpath(".", para["start_dir"])),
        )
        debmake.judge.judge(para)
    elif para["invoke"]:
        debmake.debug.debug(
            "s",
            para,
            "D: @pre-invoke @ {}".format(os.path.relpath(".", para["start_dir"])),
        )
        print("I: $ {}".format(para["invoke"]), file=sys.stderr)
        if subprocess.call(para["invoke"], shell=True) != 0:
            print("E: failed to build Debian package(s).", file=sys.stderr)
            exit(1)
    current_dir = os.path.abspath(".")
    if current_dir != para["start_dir"]:
        print(
            "I: debmake operated in the ~/{} directory".format(current_dir),
            file=sys.stderr,
        )
        print(
            "I: upon exit of debmake, you will be back to the ~/{} directory".format(
                para["start_dir"]
            ),
            file=sys.stderr,
        )
        print(
            'I: please execute "cd {}" before building the binary package'.format(
                os.path.relpath(para["start_dir"], current_dir)
            ),
            file=sys.stderr,
        )
        print(
            "I: with dpkg-buildpackage (or debuild, pdebuild, sbuild, ...).",
            file=sys.stderr,
        )
    return


#######################################################################
# Test code
#######################################################################
if __name__ == "__main__":
    main()
