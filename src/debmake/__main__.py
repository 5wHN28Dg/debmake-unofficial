#!/usr/bin/python3
# vim:se tw=0 sts=4 ts=4 et ai:
"""
Copyright © 2014-2026 Osamu Aoki

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
import sys
import time

import debmake
import debmake.analyze
import debmake.debian
import debmake.debs
import debmake.debug
import debmake.dir_debmake
import debmake.dir_git
import debmake.dir_tar
import debmake.para
import debmake.sh
import debmake.tar_copy
import debmake.tar_expand
import debmake.tar_orig
import debmake.tar_wget


#######################################################################
# main program
#######################################################################
def main():
    #######################################################################
    # set parameters from commandline etc.
    #######################################################################
    para = {}  # effective global variable storage
    debmake.debug.debug("PYTHONPATH = {} ".format(":".join(sys.path)))
    debmake.debug.debug(
        "DEBMAKE_PATH = {}".format(importlib.resources.files("debmake"))
    )
    para["program_name"] = debmake.__programname__
    para["program_version"] = debmake.__version__
    para["program_copyright"] = debmake.__copyright__
    para["program_license"] = debmake.__license__
    print(
        "I: {} (version: {})".format(para["program_name"], para["program_version"]),
    )
    print(
        "I: {}".format(para["program_copyright"]),
    )
    para["start_dir"] = os.getcwd()
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
    para["tarz"] = ""
    para["debs"] = []
    #######################################################################
    # parse command argument
    #######################################################################
    debmake.debug.debug("initial values")
    debmake.para.para(para)
    debmake.debug.debug("values set by CLI", type="p", para=para)
    #######################################################################
    # print basic package info
    #######################################################################
    if para["native"]:
        print(
            'I: Native Debian package pkg="{}", ver="{}" method="{}"'.format(
                para["package"], para["version"], para["method"]
            ),
        )
    else:
        print(
            'I: Non-native Debian package pkg="{}", ver="{}", rev="{}" method="{}"'.format(
                para["package"], para["version"], para["revision"], para["method"]
            ),
        )
    #######################################################################
    # get working tree to local base directory
    #######################################################################
    if para["method"] == "tar_wget":
        # obtain tarball from URL and expand to package-version/
        debmake.tar_wget.tar_wget(para)
        debmake.tar_orig.tar_orig(para)
        debmake.tar_expand.tar_expand(para)
    elif para["method"] == "tar_copy":
        # obtain tarball from PATH and expand to package-version/
        debmake.tar_copy.tar_copy(para)
        debmake.tar_orig.tar_orig(para)
        debmake.tar_expand.tar_expand(para)
    elif para["method"] == "dir_git":
        # work tree at package-version copied from
        # clone work tree at package/
        debmake.dir_git.dir_git(para)
        debmake.dir_debmake.dir_debmake(para)
        if not para["native"]:
            debmake.dir_tar.dir_tar(para)
            debmake.tar_orig.tar_orig(para)
    elif para["method"] == "dir_debmake":
        # work tree at package-version copied from PATH
        debmake.dir_debmake.dir_debmake(para)
        if not para["native"]:
            debmake.dir_tar.dir_tar(para)
            debmake.tar_orig.tar_orig(para)
    else:
        print(
            'E: bug in para.py? method="{}"'.format(para["method"]),
            file=sys.stderr,
        )
        debmake.debug.debug('values causing "bug in para.py"', type="p", para=para)
        exit(1)
    #######################################################################
    # -q: quit here before generating template debian/* package files
    #######################################################################
    if para["quitearly"]:
        print("I: quit early after making the upstream tarball.")
        debmake.debug.debug('values at "quit early"', type="p", para=para)
        exit(0)
    #######################################################################
    # Prep to create debian/* package files in debmake_dir
    #######################################################################
    print("I: [{}] $ cd {}".format(os.path.basename(os.getcwd()), para["debmake_dir"]))
    os.chdir(para["debmake_dir"])
    # on para["debmake_dir"]=package-version path
    debmake.debs.debs(para)
    debmake.debug.debug(
        'values after "-b" option parsing to debs[...]', type="d", para=para
    )
    debmake.analyze.analyze(para)
    debmake.debug.debug("values after analyzing the source", type="d", para=para)
    # debmake.gui()          # GUI setting
    # debmake.debug.debug(after gui", type="P", para=para)
    #######################################################################
    # Make debian/* package files
    #######################################################################
    debmake.debian.debian(para)
    #######################################################################
    # Make Debian package(s)
    #######################################################################
    if para["invoke"]:
        # This is safe string
        print("I: invoke dbuild/sbuild equivalents")
        debmake.sh.sh(para["invoke"])
    #######################################################################
    # Make Debian package(s)
    #######################################################################
    current_dir = os.getcwd()
    if current_dir != para["start_dir"]:
        # abspath comparison
        print(
            'I: "cd {}" to the directory where debian/* are generated'.format(
                os.path.relpath(current_dir, para["start_dir"])
            )
        )
    return


#######################################################################
# Test code
#######################################################################
if __name__ == "__main__":
    main()
