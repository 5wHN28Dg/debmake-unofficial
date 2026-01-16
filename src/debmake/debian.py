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
import subprocess
import sys

import debmake.cat
import debmake.control
import debmake.read
import debmake.sed
import debmake.yn


#######################################################################
def debian(para):
    ###################################################################
    # bin_type="bin" list for executable deb["type"]
    ###################################################################
    exec_deb_type_list = {"bin", "perl", "python3", "ruby", "script"}
    ###################################################################
    # set output detail level: para["extra"]
    ###################################################################
    if para["extra"] == "":  # -x, --extra default
        if os.path.isfile("debian/changelog"):
            print('I: found "debian/changelog"', file=sys.stderr)
            para["extra"] = "0"
        elif os.path.isfile("debian/control"):
            print('I: found "debian/control"', file=sys.stderr)
            para["extra"] = "0"
        elif os.path.isfile("debian/copyright"):
            print('I: found "debian/copyright"', file=sys.stderr)
            para["extra"] = "0"
        elif os.path.isfile("debian/rules"):
            print('I: found "debian/rules"', file=sys.stderr)
            para["extra"] = "0"
        else:
            print(
                "I: new debianization",
                file=sys.stderr,
            )
            para["extra"] = "2"
    try:
        extra = int(para["extra"])
    except ValueError:
        extra = 2  # set to normal one
    # extra = 0 default: when any of minimum configuration files already exist
    # extra = 2 default: when none of minimum configuration files already exist
    print('I: $ debmake ... -x "{}" ...'.format(extra), file=sys.stderr)
    ###################################################################
    # common variables
    ###################################################################
    deb_package0 = para["debs"][0]["package"]  # the first binary package name
    deb_type0 = para["debs"][0]["type"]  # the first binary package type
    substlist = {
        "@PACKAGE@": para["package"],
        "@UCPACKAGE@": para["package"].upper(),
        "@YEAR@": para["year"],
        "@FULLNAME@": para["fullname"],
        "@EMAIL@": para["email"],
        "@SHORTDATE@": para["shortdate"],
        "@DATE@": para["date"],
        "@DEBMAKEVER@": para["program_version"],
        "@BINPACKAGE@": deb_package0,  # place holder
        "@COMPAT@": para["compat"],
    }
    if para["native"]:
        substlist["@PKGFORMAT@"] = "3.0 (native)"
        substlist["@VERREV@"] = para["version"]
    else:
        substlist["@PKGFORMAT@"] = "3.0 (quilt)"
        substlist["@VERREV@"] = para["version"] + "-" + para["revision"]
    ###################################################################
    # set substitution string for the 4 place holder strings:
    #   @EXPORT@ @OVERRIDE@ @DHWITH@ @DHBUILDSYSTEM@
    ###################################################################
    export_path_stem = para["data_path"] + "extra0export_"
    substlist["@EXPORT@"] = ""
    if "compiler" in para["export"]:
        substlist["@EXPORT@"] += (
            debmake.read.read(export_path_stem + "compiler").rstrip() + "\n"
        )
        if "java" in para["export"]:
            substlist["@EXPORT@"] += (
                debmake.read.read(export_path_stem + "java").rstrip() + "\n"
            )
        if "vala" in para["export"]:
            substlist["@EXPORT@"] += (
                debmake.read.read(export_path_stem + "vala").rstrip() + "\n"
            )
    substlist["@EXPORT@"] += (
        debmake.read.read(export_path_stem + "misc").rstrip() + "\n\n"
    )

    override_path_stem = para["data_path"] + "extra0override_"
    substlist["@OVERRIDE@"] = ""
    if "autogen" in para["override"]:
        substlist["@OVERRIDE@"] += (
            debmake.read.read(override_path_stem + "autogen").rstrip() + "\n\n"
        )
    if "autoreconf" in para["override"]:
        substlist["@OVERRIDE@"] += (
            debmake.read.read(override_path_stem + "autoreconf").rstrip() + "\n\n"
        )
    if "cmake" in para["override"]:
        substlist["@OVERRIDE@"] += (
            debmake.read.read(override_path_stem + "cmake").rstrip() + "\n\n"
        )
    if "java" in para["override"]:
        substlist["@OVERRIDE@"] += (
            debmake.read.read(override_path_stem + "java").rstrip() + "\n\n"
        )
    if "judge" in para["override"]:
        substlist["@OVERRIDE@"] += (
            debmake.read.read(override_path_stem + "judge").rstrip() + "\n\n"
        )
    if "makefile" in para["override"]:
        substlist["@OVERRIDE@"] += (
            debmake.read.read(override_path_stem + "makefile").rstrip() + "\n\n"
        )
    if "multiarch" in para["override"]:
        substlist["@OVERRIDE@"] += (
            debmake.read.read(override_path_stem + "multiarch").rstrip() + "\n\n"
        )
    if "pythons" in para["override"]:
        substlist["@OVERRIDE@"] += (
            debmake.read.read(override_path_stem + "pythons").rstrip() + "\n\n"
        )

    if para["dh_with"] == set():  # no dh_with
        substlist["@DHWITH@"] = ""
    else:
        substlist["@DHWITH@"] = " --with {}".format(",".join(para["dh_with"]))

    if para["dh_buildsystem"] == "":  # no --buildsystem
        substlist["@DHBUILDSYSTEM@"] = ""
    else:
        substlist["@DHBUILDSYSTEM@"] = " --buildsystem={}".format(
            para["dh_buildsystem"]
        )

    ###################################################################
    # generate/verify minimum 5 configuration files (extra=0-4).
    ###################################################################
    # ensure debian/ directory to exist
    os.makedirs("debian", exist_ok=True)
    # debian/copyright (generate or verify)
    if not os.path.isfile("debian/copyright"):
        # generate debian/copyright
        command = (
            "licensecheck --recursive --copyright --deb-machine . > debian/copyright"
        )
        print("I: $ {}".format(command), file=sys.stderr)
        if subprocess.call(command, shell=True) != 0:
            print("E: failed to run this command", file=sys.stderr)
            exit(1)
        print(
            "I: debian/copyright generated.",
            file=sys.stderr,
        )
    else:
        # verify existing debian/copyright
        command = "lrc"
        print("I: $ {}".format(command), file=sys.stderr)
        if subprocess.call(command, shell=True) != 0:
            print("E: failed to run lrc command", file=sys.stderr)
            debmake.yn.yn("Continue", "", para["yes"])
        print(
            "I: debian/copyright verified.",
            file=sys.stderr,
        )
    # debian/control
    debmake.cat.cat("debian/control", debmake.control.control(para), para)
    # debian/changelog, debian/rules
    debmake.sed.sed("extra0_*", "debian/", substlist, deb_package0, para)
    os.chmod("debian/rules", 0o755)
    # debian/source/format
    debmake.sed.sed(
        "extra0source_*",
        "debian/source/",
        substlist,
        deb_package0,
        para,
    )
    ###################################################################
    # generate desirable configuration files, if missing (extra=1-4).
    ###################################################################
    if extra >= 1:
        # README.Debian, README.source, clean, gbp.conf, salsa-ci.yml, watch
        debmake.sed.sed(
            "extra1_*",
            "debian/",
            substlist,
            deb_package0,
            para,
        )
        # test/control
        debmake.sed.sed(
            "extra1tests_*",
            "debian/tests/",
            substlist,
            deb_package0,
            para,
        )
        # upstream/metadata
        debmake.sed.sed(
            "extra1upstream_*",
            "debian/upstream/",
            substlist,
            deb_package0,
            para,
        )
        if not para["native"]:
            # non-native and extra=1-3
            # patches/series
            debmake.sed.sed(
                "extra1patches_*",
                "debian/patches/",
                substlist,
                deb_package0,
                para,
            )
        if len(para["debs"]) == 1:
            # install, links, dirs, docs, examples for single binary deb
            debmake.sed.sed(
                "extra1single_*",
                "debian/",
                substlist,
                deb_package0,
                para,
            )
            if deb_type0 == "doc":
                # info, doc-base, manpages  for single doc binary deb
                debmake.sed.sed(
                    "extra1single.doc_*",
                    "debian/",
                    substlist,
                    deb_package0,
                    para,
                )
        else:
            # package.links, package.dirs for multi-binary debs
            #  * don't repeat over binary packages for simplicity
            #
            # package.install package.docs, ... will be generated at
            # the last with repeat over binary packages
            debmake.sed.sed(
                "extra1multi_*",
                "debian/",
                substlist,
                deb_package0,
                para,
            )
    ###################################################################
    # generate basic .ex configuration files, if missing (extra=2-4).
    ###################################################################
    if extra >= 2:
        debmake.sed.sed(
            "extra2_*",
            "debian/",
            substlist,
            deb_package0,
            para,
        )
        if not para["native"]:
            # source/local-options.ex source/local-patch-header.ex
            debmake.sed.sed(
                "extra2source.nn_*",
                "debian/source/",
                substlist,
                deb_package0,
                para,
            )
        if len(para["debs"]) == 1:
            # single binary .ex templates
            debmake.sed.sed("extra2single_*", "debian/", substlist, deb_package0, para)
        else:
            # multi-binary .ex templates only for the first binary package
            debmake.sed.sed("extra2multi_*", "debian/", substlist, deb_package0, para)
    ###################################################################
    # generate typical optional .ex configuration files, if missing (extra=3, 4).
    ###################################################################
    # create templates only for the first binary package
    if extra >= 3:
        debmake.sed.sed("extra3_*", "debian/", substlist, deb_package0, para)
        debmake.sed.sed(
            "extra3source_*", "debian/source/", substlist, deb_package0, para
        )
    ###################################################################
    # generate all optional .ex configuration files, if missing (extra=4).
    ###################################################################
    # create templates only for the first binary package
    if extra >= 4:
        debmake.sed.sed(
            "extra4_*",
            "debian/",
            substlist,
            deb_package0,
            para,
        )
        if not para["native"]:
            # non-native and extra=4
            debmake.sed.sed(
                "extra4source.nn_*",
                "debian/source/",
                substlist,
                deb_package0,
                para,
            )
    ###################################################################
    # generate desirable configuration files, if missing (extra=1-4).
    #  - loop over binary packages by setting substlist["@BINPACKAGE@"]
    ###################################################################
    if extra >= 1:
        if len(para["debs"]) > 1:
            # package-install, package.docs for multi-binary debs
            for deb in para["debs"]:
                substlist["@BINPACKAGE@"] = deb["package"]
                deb_type = deb["type"]
                if deb_type in exec_deb_type_list:
                    deb_type = "bin"
                # deb_type is reduced to {bin, data, dev, doc, lib}
                debmake.sed.sed(
                    "extra1multi." + deb_type + "_*",
                    "debian/",
                    substlist,
                    deb["package"],  # use binpackage name
                    para,
                )
    ###################################################################
    # wrap-and-sort -vast
    # comments may be reordered to be placed after an empty line
    ###################################################################
    command = "wrap-and-sort -vast"
    print("I: $ {}".format(command), file=sys.stderr)
    if subprocess.call(command, shell=True) != 0:
        print('E: failed to run "wrap-and-sort -vast".', file=sys.stderr)
        exit(1)
    print(
        "I: debian/* may have a blank line at the top.",
        file=sys.stderr,
    )
    return


#######################################################################
# Test script
#######################################################################
if __name__ == "__main__":
    print("no test")
