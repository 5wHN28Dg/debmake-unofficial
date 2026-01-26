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

import glob
import itertools
import os.path
import sys

import debmake.grep
import debmake.scanext
import debmake.yn


###########################################################################
# check_popular_ext_type: warn binary dependency (popular extension match)
###########################################################################
def check_popular_ext_type(ext_type, msg, para):
    n_max_files = 3
    if ext_type in itertools.islice(para["ext_type_counter"].keys(), 0, n_max_files):
        ext_type_found = False
        for deb in para["debs"]:
            type = deb["type"]  # -b (python3 also reports python)
            if type == ext_type:
                ext_type_found = True
                break
            if ext_type == "python3" and type == "python3":
                ext_type_found = True
                break
            if ext_type == "javascript" and type == "nodejs":
                ext_type_found = True
                break
        if not ext_type_found:
            print(
                'W: many ext = "{}" type extension programs without matching -b set.'.format(
                    ext_type
                ),
            )
            debmake.yn.yn(msg, "", para["yes"])
    return


###########################################################################
# analyze: called from debmake.main()
###########################################################################
def analyze(para):
    ###################################################################
    # package list by types (first pass)
    ###################################################################
    para["bin"] = []
    para["lib"] = []
    para["dev"] = []
    para["data"] = []
    para["doc"] = []
    para["scripts"] = []
    for i, deb in enumerate(para["debs"]):
        if deb["type"] == "bin":
            para["bin"].append(deb["binpackage"])
        elif deb["type"] == "lib":
            para["lib"].append(deb["binpackage"])
        elif deb["type"] == "dev":
            para["dev"].append(deb["binpackage"])
        elif deb["type"] == "doc":
            para["doc"].append(deb["binpackage"])
        elif deb["type"] == "data":
            para["data"].append(deb["binpackage"])
        else:
            para["scripts"].append(deb["binpackage"])
    if len(para["debs"]) != 1 and len(para["dev"]) != len(para["lib"]):
        print(
            'E: # of "dev":{} != # of "lib": {}.'.format(
                len(para["dev"]), len(para["lib"])
            ),
            file=sys.stderr,
        )
        exit(1)
    if para["lib"] != []:
        setmultiarch = True
    elif para["bin"] != [] and len(para["debs"]) == 1:
        setmultiarch = True
    else:
        setmultiarch = False  # for override
    if para["monoarch"]:
        setmultiarch = False
    ###################################################################
    # package list by types (second pass)
    ###################################################################
    for i, deb in enumerate(para["debs"]):
        if deb["type"] == "bin":
            para["export"].update({"compiler"})
            for libpkg in para["lib"]:
                para["debs"][i]["depends"].update({libpkg + " (= ${binary:Version})"})
        elif deb["type"] == "lib":
            para["export"].update({"compiler"})
        elif deb["type"] == "dev":
            if deb["binpackage"][-4:] == "-dev":
                pkg = deb["binpackage"][:-4]
            else:
                print(
                    'E: Type=dev package "{}" should end with "-dev"'.format(
                        deb["binpackage"]
                    ),
                    file=sys.stderr,
                )
                exit(1)
            match = False
            for libpkg in para["lib"]:
                if libpkg[: len(pkg)] == pkg:
                    para["debs"][i]["depends"].update(
                        {libpkg + " (= ${binary:Version})"}
                    )
                    match = True
                    break
            if not match:
                print(
                    'E: {} does not have matching library in "{}".'.format(
                        deb["binpackage"], ", ".join(para["lib"])
                    ),
                    file=sys.stderr,
                )
                exit(1)
        elif deb["type"] == "perl":
            for libpkg in para["lib"]:
                para["debs"][i]["depends"].update(
                    {
                        libpkg
                        + " (>= ${source:Version}), "
                        + libpkg
                        + " (<< ${source:Upstream-Version}.0~)"
                    }
                )
        elif deb["type"] == "python3":
            para["dh_with"].update({"python3"})
            para["build_depends"].update({"python3-all", "dh-python"})
            for libpkg in para["lib"]:
                para["debs"][i]["depends"].update(
                    {
                        libpkg
                        + " (>= ${source:Version}), "
                        + libpkg
                        + " (<< ${source:Upstream-Version}.0~)"
                    }
                )
        elif deb["type"] == "ruby":
            para["dh_with"].update({"ruby"})  # may not be needed
            para["build_depends"].update({"ruby"})
            for libpkg in para["lib"]:
                para["debs"][i]["depends"].update(
                    {
                        libpkg
                        + " (>= ${source:Version}), "
                        + libpkg
                        + " (<< ${source:Upstream-Version}.0~)"
                    }
                )
        elif deb["type"] == "nodejs":
            para["dh_with"].update({"nodejs"})
            para["build_depends"].update({"pkg-js-tools"})
            for libpkg in para["lib"]:
                para["debs"][i]["depends"].update(
                    {
                        libpkg
                        + " (>= ${source:Version}), "
                        + libpkg
                        + " (<< ${source:Upstream-Version}.0~)"
                    }
                )
        elif deb["type"] == "script":
            for libpkg in para["lib"]:
                para["debs"][i]["depends"].update(
                    {
                        libpkg
                        + " (>= ${source:Version}), "
                        + libpkg
                        + " (<< ${source:Upstream-Version}.0~)"
                    }
                )
        else:
            pass
    #######################################################################
    # auto-set build system by files in the base directory
    #   update para["dh_with"] -- debian build component dh_*
    #   para["build_type"] -- upstrean build type
    #   para["build_depends"] -- build dependency packages
    #   para["export"] -- exported build environment variable type
    #   para["override"] -- set override_dh_* setting type
    #######################################################################
    para["build_type"] = ""  # reset value
    para["dh_buildsystem"] = ""  # normally not needed
    # check if '*.pro' for Qmake project exist in advance.
    pro = glob.glob("*.pro")
    if pro:
        pro = pro[0]
    else:
        pro = ""
    # check if '*.spec.in' for RPM
    # GNU coding standard with autotools = autoconf+automake
    if (
        os.path.isfile("configure.ac")
        and os.path.isfile("Makefile.am")
        and ("autotools-dev" not in para["dh_with"])
    ):
        para["dh_with"].update({"autoreconf"})
        para["build_type"] = "Autotools with autoreconf"
        para["build_depends"].update({"dh-autoreconf"})
        para["export"].update({"autotools"})
        if os.path.isfile("autogen.sh"):
            para["override"].update({"autogen"})
        else:
            para["override"].update({"autoreconf"})
    elif (
        os.path.isfile("configure.in")
        and os.path.isfile("Makefile.am")
        and ("autotools-dev" not in para["dh_with"])
    ):
        para["dh_with"].update({"autoreconf"})
        para["build_type"] = "Autotools with autoreconf (old)"
        para["build_depends"].update({"dh-autoreconf"})
        para["export"].update({"autotools"})
        if os.path.isfile("autogen.sh"):
            para["override"].update({"autogen"})
        else:
            para["override"].update({"autoreconf"})
        print("W: Use of configure.in has been deprecated since 2001.")
    elif (
        os.path.isfile("configure.ac")
        and os.path.isfile("Makefile.am")
        and os.path.isfile("configure")
    ):
        para["dh_with"].update({"autotools-dev"})
        para["build_type"] = "Autotools"
        para["build_depends"].update({"autotools-dev"})
        para["export"].update({"autotools"})
    elif (
        os.path.isfile("configure.in")
        and os.path.isfile("Makefile.am")
        and os.path.isfile("configure")
    ):
        para["dh_with"].update({"autotools-dev"})
        para["build_type"] = "Autotools (old)"
        para["build_depends"].update({"autotools-dev"})
        para["export"].update({"autotools"})
        print("W: Use of configure.in has been deprecated since 2001.")
    elif "autoreconf" in para["dh_with"]:
        print(
            'E: missing configure.ac or Makefile.am required for "dh $@ --with autoreconf".',
            file=sys.stderr,
        )
        exit(1)
    elif "autotools-dev" in para["dh_with"]:
        print(
            'E: missing configure.ac or Makefile.am or configure required for "dh $@ --with autotools-dev".',
            file=sys.stderr,
        )
        exit(1)
    # GNU coding standard with configure
    elif os.path.isfile("configure"):
        para["build_type"] = "configure"
        if setmultiarch:
            para["override"].update({"multiarch"})
    # GNU coding standard with Cmake
    elif os.path.isfile("CMakeLists.txt"):
        para["build_type"] = "Cmake"
        para["build_depends"].update({"cmake"})
        para["override"].update({"cmake"})
        if setmultiarch:
            para["override"].update({"multiarch"})
    # GNU coding standard with make
    elif os.path.isfile("Makefile"):
        para["build_type"] = "make"
        para["override"].update({"makefile"})
        if setmultiarch:
            para["override"].update({"multiarch"})
    # Python setuptools
    elif os.path.isfile("setup.py"):
        para["dh_with"].update({"python3"})
        para["build_type"] = "Python setuptools (setup.py)"
        para["dh_buildsystem"] = "pybuild"
        # dh-python and python3-build are pulled in by pybuild-plugin-pyproject"
        para["build_depends"].update({"python3-all", "pybuild-plugin-pyproject"})
        if debmake.grep.grep("setup.py", "python3", 0, 1) or debmake.grep.grep(
            "setup.py", "python", 0, 1
        ):
            # http://docs.python.org/3/distutils/
            if debmake.grep.grep(
                "setup.py", r"from\s+setuptools\s+import\s+setup", 0, -1
            ):
                # TODO: this needs verification
                para["build_depends"].update({"python3-setuptools"})
            else:
                # non-setuptools (pure distutil?) may not be supported
                print(
                    "W: no setuptools. (distutils?)  check setup.py.",
                )
        else:
            print("W: unknown python system.  check setup.py.")
    elif os.path.isfile("setup.cnf"):
        para["dh_with"].update({"python3"})
        para["build_type"] = "Python setuptools (setup.cnf)"
        para["dh_buildsystem"] = "pybuild"
        # dh-python and python3-build are pulled in by pybuild-plugin-pyproject"
        para["build_depends"].update({"python3-all", "pybuild-plugin-pyproject"})
        # TODO: check if this is good idea
        para["build_depends"].update({"python3-setuptools"})
    elif os.path.isfile("pyproject.toml"):
        para["dh_with"].update({"python3"})
        para["build_type"] = "Python (pyproject.toml: PEP-518, PEP-621, PEP-660)"
        para["dh_buildsystem"] = "pybuild"
        # dh-python and python3-build are pulled in by pybuild-plugin-pyproject"
        para["build_depends"].update({"python3-all", "pybuild-plugin-pyproject"})
        if debmake.grep.grep("pyproject.toml", r"setuptools", 0, -1):
            # TODO: check if this is good idea
            para["build_depends"].update({"python3-setuptools"})
            # para["build_depends"].update({"python3-setuptools-whl"})
            print("W: setuptools build system.")
        elif debmake.grep.grep("pyproject.toml", r"hatchling", 0, -1):
            # TODO: check if this is good idea
            para["build_depends"].update({"python3-hatchling"})
            print("W: Hatchling build system.")
        elif debmake.grep.grep("pyproject.toml", r"flit_core", 0, -1):
            # TODO: check if this is good idea
            para["build_depends"].update({"flit"})
            print("W: Flit build system.")
        elif debmake.grep.grep("pyproject.toml", r"pdm-backend", 0, -1):
            # TODO: check if this is good idea
            para["build_depends"].update({"python3-pdm"})
            # para["build_depends"].update({"python3-pdm-pep517"})
            print("W: PDM build system.")
        else:
            # TODO: check if this is good idea
            print("W: unknown python build system.")
    # Perl
    elif os.path.isfile("Build.PL"):
        # Preferred over Makefile.PL after debhelper v8
        para["build_type"] = "Perl Module::Build"
        para["build_depends"].update({"perl"})
    elif os.path.isfile("Makefile.PL"):
        para["build_type"] = "Perl ExtUtils::MakeMaker"
        para["build_depends"].update({"perl"})
    # Ruby
    elif os.path.isfile("setup.rb"):
        print(
            "W: dh-make-ruby(1) (gem2deb package) may provide better packaging results.",
        )
        para["build_type"] = "Ruby setup.rb"
        para["build_depends"].update({"ruby", "gem2deb"})
    # Javascript nodejs
    elif os.path.isfile("package.json"):
        para["build_type"] = "nodejs"
        para["dh_with"].update({"nodejs"})
        para["build_depends"].update({"dh-nodejs"})
    # Java
    elif os.path.isfile("build.xml"):
        para["build_type"] = "Java ant"
        para["dh_with"].update({"javahelper"})
        # XXX FIXME XXX which compiler to use?
        para["build_depends"].update({"javahelper", "gcj"})
        para["export"].update({"java", "compiler"})
        para["override"].update({"java"})
        if setmultiarch:
            para["override"].update({"multiarch"})
    # Qmake
    elif os.path.isfile(pro):
        # XXX FIXME XXX Is this right?
        para["build_type"] = "QMake"
        para["build_depends"].update({"qt4-qmake"})
        if setmultiarch:
            para["override"].update({"multiarch"})
    else:
        para["build_type"] = "Unknown"
        if setmultiarch:
            para["override"].update({"multiarch"})
    print("I: build_type = {}".format(para["build_type"]))
    #######################################################################
    # analyze file extensions
    #######################################################################
    para["ext_type_counter"] = debmake.scanext.scanext()
    #######################################################################
    # compiler: set build dependency etc. if they are used
    if "c" in para["ext_type_counter"].keys():
        para["export"].update({"compiler"})
        if setmultiarch and para["build_type"][0:9] != "Autotools":
            para["override"].update({"multiarch"})
    if "java" in para["ext_type_counter"].keys():
        if para["build_type"][0:4] != "Java":
            # Non-ant build system
            if para["build_type"]:
                para["build_type"] = "Java + " + para["build_type"]
            else:
                para["build_type"] = "Java"
            para["dh_with"].update({"javahelper"})
            para["build_depends"].update({"javahelper", "gcj"})
            para["export"].update({"java", "compiler"})
            para["override"].update({"java"})
            if setmultiarch and para["build_type"][0:9] != "Autotools":
                para["override"].update({"multiarch"})
    if para["build_type"][0:4] == "Java":
        print(
            "W: Java support is not perfect. (/usr/share/doc/javahelper/tutorials.html)",
        )
    if "vala" in para["ext_type_counter"].keys():
        para["build_type"] = "Vala"
        para["build_depends"].update({"valac"})
        para["export"].update({"vala", "compiler"})
        if setmultiarch and para["build_type"][0:9] != "Autotools":
            para["override"].update({"multiarch"})
    #######################################################################
    # set build dependency and override if --with python3
    #######################################################################
    if "python3" in para["dh_with"]:
        para["build_depends"].update({"python3-all", "dh-python"})
        para["override"].update({"pythons"})
    #######################################################################
    # interpreter: warn binary dependency etc. if they are top 3 popular files
    #######################################################################
    check_popular_ext_type("perl", '-b":perl, ..." missing. Continue?', para)
    check_popular_ext_type("python3", '-b":python3" is missing. Continue?', para)
    check_popular_ext_type("ruby", '-b":ruby, ..." missing. Continue?', para)
    check_popular_ext_type("javascript", '-b":nodejs, ..." missing. Continue?', para)
    #######################################################################
    return


if __name__ == "__main__":
    print("no test")
