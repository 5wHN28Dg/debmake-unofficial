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

import os
import os.path
import shutil

import debmake.cat
import debmake.control
import debmake.read
import debmake.sed
import debmake.sh


#######################################################################
def debian(para):
    ###################################################################
    ###################################################################
    # bin_type="bin" list for executable deb["type"]
    ###################################################################
    exec_deb_type_list = {"bin", "perl", "python3", "ruby", "script"}
    ###################################################################
    # set output detail level: para["extra"]
    ###################################################################
    conf_required = ["changelog", "control", "copyright", "rules", "source/format"]
    if para["extra"] == "":  # -x, --extra default
        para["extra"] = "2"
        for conf in conf_required:
            if os.path.isfile("debian/" + conf):
                print('I: found "debian/' + conf + '"')
                para["extra"] = "0"
    try:
        extra = int(para["extra"])
    except ValueError:
        extra = 2  # set to normal one
    # extra = 0 default: minimum configuration files already exist
    # extra = 2 default: none of minimum configuration files already exist
    print('I: creating debian/* files with "-x {}" option'.format(extra))
    ###################################################################
    # common variables
    ###################################################################
    substlist = {
        "@PACKAGE@": para["package"],
        "@UCPACKAGE@": para["package"].upper(),
        "@YEAR@": para["year"],
        "@FULLNAME@": para["fullname"],
        "@EMAIL@": para["email"],
        "@SHORTDATE@": para["shortdate"],
        "@DATE@": para["date"],
        "@DEBMAKEVER@": para["program_version"],
        "@BINPACKAGE@": para["debs"][0]["binpackage"],
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
    # generate/verify minimum configuration files (extra=0-4).
    #  debian/copyright
    #  debian/control
    #  debian/changelog
    #  debian/rules
    #  debian/source/format
    ###################################################################
    # ensure debian/ directory to exist
    os.makedirs("debian", exist_ok=True)
    # debian/copyright (generate or verify)
    if not os.path.exists("debian/copyright"):
        # generate debian/copyright
        command = "licensecheck --recursive --copyright --deb-machine "
        if para["verbose"]:
            command = "--verbose "
        command += " . > " + "debian/copyright"
        debmake.sh.sh(command)
        print("I: creating debian/copyright by licensecheck.")
    elif shutil.which("lrc"):
        # verify existing debian/copyright
        command = "lrc"
        debmake.sh.sh(command)
        print("I: verifying debian/copyright by lrc (licenserecon package).")
    else:
        command = "licensecheck --recursive --copyright --deb-machine "
        if para["verbose"]:
            command = "--verbose "
        command += " . > " + "debian/copyright.ex"
        debmake.sh.sh(command)
        print("I: creating debian/copyright.ex by licensecheck.")
    # debian/control
    print(
        "I: creating {} from control.py".format("debian/control"),
    )
    debmake.cat.cat("debian/control", debmake.control.control(para), para)
    # debian/changelog, debian/rules
    debmake.sed.sed("extra0_*", "debian/", substlist, "", para)
    os.chmod("debian/rules", 0o755)
    # debian/source/format
    debmake.sed.sed(
        "extra0source_*",
        "debian/source/",
        substlist,
        "",
        para,
    )
    ###################################################################
    # generate desirable configuration files, if missing (extra=1-4).
    # some templates are produced only for the first binary package.
    ###################################################################
    if extra >= 1:
        # debian/clean
        # debian/dirs
        # debian/docs
        # debian/examples
        # debian/gbp.conf
        # debian/links
        # debian/manpages
        # debian/README.Debian
        # debian/README.source
        # debian/salsa-ci.yml
        debmake.sed.sed(
            "extra1_*",
            "debian/",
            substlist,
            "",
            para,
        )
        if not para["native"]:
            # debian/watch
            debmake.sed.sed(
                "extra1nn_*",
                "debian/",
                substlist,
                "",
                para,
            )
        # tests/control
        debmake.sed.sed(
            "extra1tests_*",
            "debian/tests/",
            substlist,
            "",
            para,
        )
        # upstream/metadata
        debmake.sed.sed(
            "extra1upstream_*",
            "debian/upstream/",
            substlist,
            "",
            para,
        )
        if not para["native"]:
            # patches/series
            debmake.sed.sed(
                "extra1patches_*",
                "debian/patches/",
                substlist,
                "",
                para,
            )
    ###################################################################
    # generate basic .ex configuration files, if missing (extra=2-4).
    ###################################################################
    if extra >= 2:
        # bug-control.ex
        # bug-presubj.ex
        # bug-script.ex
        # maintscript.ex
        # manpage.1.ex
        # doc-base.ex
        # info.ex
        # lintian-overrides.ex
        debmake.sed.sed(
            "extra2_*",
            "debian/",
            substlist,
            "",
            para,
        )
        debmake.sed.sed("extra2source_*", "debian/source/", substlist, "", para)
        if not para["native"]:
            # source/local-options.ex
            # source/local-patch-header.ex
            # source/options.ex
            # source/patch-header.ex
            # source/lintian-overrides.ex
            debmake.sed.sed(
                "extra2source.nn_*",
                "debian/source/",
                substlist,
                "",
                para,
            )
    ###################################################################
    # generate typical optional .ex configuration files, if missing (extra=3, 4).
    ###################################################################
    # create templates only for the first binary package
    if extra >= 3:
        debmake.sed.sed("extra3_*", "debian/", substlist, "", para)
    ###################################################################
    # generate all optional .ex configuration files, if missing (extra=4).
    ###################################################################
    # create templates only for the first binary package
    if extra >= 4:
        debmake.sed.sed(
            "extra4_*",
            "debian/",
            substlist,
            "",
            para,
        )
    ###################################################################
    # generate desirable configuration files, if missing (extra=1-4).
    #  - loop over binary packages
    ###################################################################
    if extra >= 1:
        # package-install, package.docs for multi-binary debs
        for deb in para["debs"]:
            substlist["@BINPACKAGE@"] = deb["binpackage"]
            if len(para["debs"]) == 1:
                binpackagedot = ""
            else:
                binpackagedot = substlist["@BINPACKAGE@"] + "."
            deb_type = deb["type"]
            if deb_type in exec_deb_type_list:
                deb_type = "bin"

            # deb_type is reduced to {bin, data, dev, doc, lib}
            debmake.sed.sed(
                "extra1" + deb_type + "_*",
                "debian/",
                substlist,
                binpackagedot,
                para,
            )
    ###################################################################
    # wrap-and-sort -vast
    # comments may be reordered to be placed after an empty line
    ###################################################################
    if para["verbose"]:
        command = "wrap-and-sort -vast"
    else:
        command = "wrap-and-sort -ast"
    debmake.sh.sh(command)
    print("I: debian/* may have a blank line at the top.")
    return


#######################################################################
# Test script
#######################################################################
if __name__ == "__main__":
    print("no test")
