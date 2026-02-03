#!/usr/bin/python3
# vim:se tw=0 sts=4 ts=4 et ai:
"""
Copyright © 2026 Osamu Aoki

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

import argparse
import os
import pwd
import re
import sys

import debmake.debug
import debmake.yn

re_url = re.compile(
    r"""
    ^
    (?P<pre>http://|https://|ftp://|git://|)     # https:// ... or ''
    (?P<user>[A-Za-z][A-Za-z0-9+._-]*@|)         # username@ or ''
    (?P<host>[A-Za-z][A-Za-z0-9+._-]*[:/]|)      # hostname/ or hostname: or ''
    (?P<path>[A-Za-z0-9+._-][A-Za-z0-9+._/-]*/|) # path/to/ or ''
    (?P<pkg>[^/]+?)                              # package non-greedy
    (?P<ver>[_-][0-9]+[A-Za-z0-9~+.-]*?|)        # -version non-greedy or ''
    (?P<ext>\.orig\.tar\.xz|\.tar\.xz|\.txz|
            \.orig\.tar\.gz|\.tar\.gz|\.tgz|
            \.orig\.tar\.bz2|\.tar\.bz2|\.tbz|\.tb2|\.tbz2|
            \.git
            |)                                   # .ext or ''
    (?P<tail>/|)                                 # / or ''
    $
    """,
    re.VERBOSE,
)

# No $ ` ! # \ | for invoke
re_safe = re.compile(
    r"""
    ^
    [A-Za-z][A-Za-z0-9+.;"'=_ -]*
    $
    """,
    re.VERBOSE,
)


#######################################################################
# Initialize parameters
#######################################################################
def para(para):
    """
    Set para[...] from the command line and environment variables.
    """
    #######################################################################
    # process command line
    #######################################################################
    p = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""\
{0}: make Debian source package    Version: {1}
{2}

{0} helps to build the Debian package from the upstream source.

Normally, this is done as follows:
 * The upstream source is obtained as a tarball from a remote web site
   or a cloned work tree using "git clone".
   * For a tarball, it is expanded to many files in the source directory.
   * For a cloned work tree, it is used as the source directory.
 * {0} is typically invoked in the source directory without any
   argument.
   * The source directory is copied to ../package-version/ directory.
   * If ../package_version.orig.tar.xz is missing, it is generated.
   * The current directory is moved to ../package-version/.
   * Template files are generated in the ../package-version/debian/
     directory
 * Files in the ../package-version/debian/ directory should be manually
   adjusted.
 * dpkg-buildpackage (usually from its wrapper debuild, sbuild, ...) is
   invoked in the ../package-version/ directory to make Debian source
   and binary packages.

Also, {0} can be invoked with an argument.  This argument can be URL
for a tarball hosted on a remote web site or for a source code accessed
by "git clone"; or local PATH to the tarball or the source code.

Arguments to -b, -f, and -w options need to be quoted to protect them from the shell.
""".format(
            para["program_name"], para["program_version"], para["program_copyright"]
        ),
        epilog="See debmake(1) manpage for more.",
    )
    p.add_argument(
        "-n",
        "--native",
        action="store_true",
        default=False,
        help="make a native source package without .orig.tar.gz",
    )
    p.add_argument(
        "-p",
        "--package",
        action="store",
        default="",
        help="set the Debian package name",
        metavar="package",
    )
    p.add_argument(
        "-u",
        "--upstreamversion",
        action="store",
        default="",
        help="set the upstream package version",
        metavar="version",
    )
    p.add_argument(
        "-r",
        "--revision",
        action="store",
        default="",
        help="set the Debian package revision",
        metavar="revision",
    )
    p.add_argument(
        "-z",
        "--tarz",
        action="store",
        default="",
        help="set the tarball compression type, extension=(tar.xz|tar.gz|tar.bz2)",
        metavar="extension",
    )
    p.add_argument(
        "-b",
        "--binaryspec",
        action="store",
        default="",
        help='set binary package specs as comma separated list of "binarypackage":"type" pairs, e.g., in full form "foo:bin,foo-doc:doc,libfoo1:lib,libfoo-dev:dev" or in short form ",-doc,libfoo1, libfoo-dev".  Here, "binarypackage" is the binary package name; and optional "type" is chosen from "bin", "data", "dev", "doc", "lib", "perl", "python3", "ruby", and "script". If "type" is not specified but obvious, it is set by "binarypackage".  Otherwise it is set to "bin" for the compiled ELF binary.',
        metavar='"binarypackage[:type], ..."',
    )
    p.add_argument(
        "-e",
        "--email",
        action="store",
        default="",
        help="set e-mail address",
        metavar="foo@example.org",
    )
    p.add_argument(
        "-f",
        "--fullname",
        action="store",
        default="",
        help="set the fullname",
        metavar='"firstname lastname"',
    )
    #    p.add_argument(
    #            '-g',
    #            '--gui',
    #            action = 'store_true',
    #            default = False,
    #            help = 'run GUI configuration')
    #
    #   -h : used by argparse for --help
    p.add_argument(
        "-i",
        "--invoke",
        default="",
        action="store",
        help="invoke package build tool",
        metavar="[debuild|sbuild|dgit sbuild|gbp buildpackage|dpkg-buildpackage| ...]",
    )
    p.add_argument(
        "-m",
        "--monoarch",
        action="store_true",
        default=False,
        help="force packages to be non-multiarch",
    )
    p.add_argument(
        "-q",
        "--quitearly",
        action="store_true",
        default=False,
        help="quit early before creating files in the debian directory",
    )
    p.add_argument(
        "-v",
        "--version",
        action="store_true",
        default=False,
        help="show version information",
    )
    p.add_argument(
        "-V",
        "--verbose",
        action="store_true",
        default=False,
        help="use --verbose for shell commands if available",
    )
    p.add_argument(
        "-w",
        "--with",
        action="store",
        default="",
        dest="withargs",
        help='set additional "dh --with" option arguments in debian/rules',
        metavar='"addon ..."',
    )
    p.add_argument(
        "-x",
        "--extra",
        default="",
        action="store",
        help="generate extra configuration files as templates (default: 2)",
        metavar="[01234]",
    )
    p.add_argument(
        "-y",
        "--yes",
        action="count",
        default=0,
        help='use once to "force yes" for all prompts, twice to "force no"',
    )
    # This is removed option (now NOP)
    p.add_argument(
        "-B",
        "--backup",
        action="store_true",
        default=False,
        help="keep the user editted ones without .ex suffix and create template files with .ex suffix",
    )
    p.add_argument(
        "URL",
        nargs="?",
        default="",
        help="aquire the source tree from the tarball, the git repository or the source tree at this URL (or PATH) (if missing, the source tree uses the current directory)",
    )
    # old options for transition
    p.add_argument(
        "-a",
        "--archive",
        action="store",
        default="",
        help=argparse.SUPPRESS,
    )
    p.add_argument("-c", "--copyright", action="store_true", help=argparse.SUPPRESS)
    p.add_argument("-d", "--dist", action="store_true", help=argparse.SUPPRESS)
    p.add_argument("-j", "--judge", action="store", help=argparse.SUPPRESS)
    p.add_argument("-k", "--kludge", action="store_true", help=argparse.SUPPRESS)
    p.add_argument(
        "-l",
        "--license",
        default="",
        action="store",
        help=argparse.SUPPRESS,
    )
    p.add_argument(
        "-o",
        "--option",
        default="",
        action="store",
        help=argparse.SUPPRESS,
    )
    p.add_argument("-P", "--pedantic", action="store_true", help=argparse.SUPPRESS)
    p.add_argument("-s", "--spec", action="store_true", help=argparse.SUPPRESS)
    p.add_argument(
        "-t",
        "--tar",
        action="store_true",
        default=False,
        help=argparse.SUPPRESS,
    )
    p.add_argument("-T", "--tutorial", action="store_true", help=argparse.SUPPRESS)
    args = p.parse_args()
    #######################################################################
    # Debug
    #######################################################################
    # print('DEBUG "{}"'.format(args.invoke))
    #######################################################################
    # print version and copyright notice
    #######################################################################
    if args.version:  # -v
        print(
            para["program_license"],
        )
        exit(0)
    #######################################################################
    # CLI compatibility
    #######################################################################
    if args.archive:
        print("-a, --archive is not needed")
    if args.copyright:
        print("-c, --copyright is ignored")
    if args.dist:
        print("-d, --dist is ignored")
    if args.judge:
        print("-j, --judge is ignored")
    if args.kludge:
        print("-k, --kludge is ignored")
    if args.license:
        print("-l, --license is ignored")
    if args.option:
        print("-o, --option is ignored")
    if args.pedantic:
        print("-P, --pedantic is ignored")
    if args.spec:
        print("-s, --spec is ignored")
    if args.tutorial:
        print("-T, --tutorial is ignored")
    #######################################################################
    # Set para[...] variables
    #######################################################################
    para["debmake_dir"] = ""
    para["base_dir"] = os.path.abspath(".")
    # normalize URL
    para["url"] = args.URL
    if para["url"] == "" and args.archive:
        # compatibility
        para["url"] = args.archive  # -a
    if para["url"][:7] == "file://":
        # drop file:// for simplicity
        para["url"] = para["url"][7:]
    if para["url"] == "":
        para["url"] = os.path.basename(os.getcwd())
        print("I: [{}] $ cd ..".format(os.path.basename(os.getcwd())))
        os.chdir("..")
        para["base_dir"] = os.path.abspath(".")
    para["binaryspec"] = args.binaryspec  # -b
    para["email"] = args.email  # -e
    if para["email"]:
        pass
    elif os.environ.get("DEBEMAIL"):
        para["email"] = os.environ.get("DEBEMAIL")
    else:
        # para["email"] = os.getlogin() + '@localhost'
        #   os.getlogin may not work well: #769392
        #   https://bugs.python.org/issue584566
        para["email"] = pwd.getpwuid(os.getuid())[0] + "@localhost"
    para["fullname"] = args.fullname  # -f
    if para["fullname"]:
        pass
    elif os.environ.get("DEBFULLNAME"):
        para["fullname"] = os.environ.get("DEBFULLNAME")
    else:
        # os.getlogin may not work well: #769392
        # debfullname = pwd.getpwnam(os.getlogin())[4].split(',')[0]
        para["fullname"] = pwd.getpwuid(os.getuid())[4].split(",")[0]
    #   para['gui']             = args.gui          # -g
    #   para['invoke'] # -i
    m = re_safe.match(args.invoke)
    para["invoke"] = args.invoke  # -i
    if para["invoke"] == "":
        pass
    elif m:
        para["invoke"] = args.invoke  # -i
    else:
        para["invoke"] = 'echo "ignore invalid -i/--invoke argument"'  # -i
    para["monoarch"] = args.monoarch  # -m
    para["native"] = args.native  # -n
    para["package"] = args.package.lower()  # -p
    para["quitearly"] = args.quitearly  # -q
    para["revision"] = args.revision  # -r
    para["tar"] = args.tar  # -t
    para["version"] = args.upstreamversion  # -u
    para["verbose"] = args.verbose  # -V
    ############################################# -w
    # --with: args.withargs -> para['dh_with'] as set
    if args.withargs == "":
        para["dh_with"] = set()  # default is empty set
    else:
        para["dh_with"] = set(args.withargs.split(","))
    #############################################
    para["extra"] = args.extra  # -x
    para["yes"] = min(args.yes, 2)  # -y
    # 0: ask, 1: yes, 2: no
    #############################################
    # short alias values for -z option
    para["tarz"] = args.tarz  # -z
    if para["tarz"] == "":
        pass
    elif para["tarz"][0] == "g":
        para["tarz"] = "tar.gz"
    elif para["tarz"][0] == "b":
        para["tarz"] = "tar.bz2"
    elif para["tarz"][0] == "x":
        para["tarz"] = "tar.xz"
    else:
        para["tarz"] = "tar.xz"
    #############################################
    para["backup"] = args.backup  # -B
    #######################################################################
    # analyze positional parameter for access and expand option
    #  para["method"] == "" --> Stop debmake
    #######################################################################
    para["method"] = ""
    m = re_url.match(para["url"])
    if m is not None:
        para["url_flag"] = True
        para["url_pre"] = m.group("pre")
        para["url_user"] = m.group("user")
        para["url_host"] = m.group("host")
        para["url_path"] = m.group("path")
        para["url_pkg"] = m.group("pkg")
        para["url_ver"] = m.group("ver")
        para["url_ext"] = m.group("ext")
        para["url_tail"] = m.group("tail")
    else:
        para["url_flag"] = False
        para["url_pre"] = ""
        para["url_user"] = ""
        para["url_host"] = ""
        para["url_path"] = ""
        para["url_pkg"] = ""
        para["url_ver"] = ""
        para["url_ext"] = ""
        para["url_tail"] = ""
    if not para["url_flag"]:
        para["method"] = ""
    elif para["url_pre"] in ["http://", "https://", "ftp://"]:
        # remote URL (non- git://)
        if para["url_ext"] == ".git" or para["url_user"] == "git@":
            para["method"] = "dir_git"
        else:
            para["method"] = "tar_wget"
    elif para["url_pre"] == "git://":
        para["method"] = "dir_git"
    else:
        if para["url_ext"] == "":
            para["method"] = "dir_debmake"
        elif para["url_tail"] != "":
            para["method"] = ""
        elif para["url_ext"] in [".orig.tar.xz", ".tar.xz", ".txz"]:
            para["method"] = "tar_copy"
            para["tarz"] = para["url_ext"][1:]
        elif para["url_ext"] in [".orig.tar.gz", ".tar.gz", ".tgz"]:
            para["method"] = "tar_copy"
            para["tarz"] = para["url_ext"][1:]
        elif para["url_ext"] in [".orig.tar.bz2", ".tar.bz2", ".tbz", ".tb2", ".tbz2"]:
            para["method"] = "tar_copy"
            para["tarz"] = para["url_ext"][1:]
        else:
            para["method"] = ""
    # extra sanity check for package_version.orig.tar.*
    if para["url_ext"] in [".orig.tar.xz", ".orig.tar.gz", ".orig.tar.bz2"]:
        if para["url_ver"][:1] == "_":
            # package_version.orig.tar.xz
            pass
        else:
            para["method"] = ""
    else:
        pass
    #######################################################################
    if para["method"] == "":
        print(
            'E: invalid URL/PATH used for debmake: "{}" (very restrictive)'.format(
                para["url"]
            ),
            file=sys.stderr,
        )
        print("I: consider executing debmake in the manually generated source tree.")
        debmake.debug.debug(" >>> mid-para ERROR for URL", type="p", para=para)
        exit(1)
    #######################################################################
    # set legal fall back values
    #######################################################################
    if para["package"] == "":
        if para["url_pkg"]:
            para["package"] = para["url_pkg"].lower()
        else:
            para["package"] = "packagename"
    #
    if para["version"] == "":
        if para["url_ver"][1:]:
            para["version"] = para["url_ver"][1:].lower()
        else:
            para["version"] = "1.0"
    #
    if para["revision"] == "":
        para["revision"] = "1"
    # fall back for para["method"] == "dir_*" w/o explicit -z
    if para["tarz"] == "":
        para["tarz"] = "tar.xz"
    # set option fmatching for file extension
    if para["tarz"] in ["orig.tar.xz", "tar.xz", "txz"]:
        para["option_z"] = "--xz"
    elif para["tarz"] in ["orig.tar.gz", "tar.gz", "tgz"]:
        para["option_z"] = "--gzip"
    elif para["tarz"] in ["orig.tar.bz2", "tar.bz2", "tbz", "tb2", "tbz2"]:
        para["option_z"] = "--bzip2"
    else:
        print(
            'E: invalid -z option set for debmake: -z "{}"'.format(para["url"]),
            file=sys.stderr,
        )
        debmake.debug.debug(" >>> mid-para ERROR for -z option", type="p", para=para)
        exit(1)

    #######################################################################
    para["section"] = "unknown"
    para["priority"] = "optional"
    para["homepage"] = "<insert the upstream URL, if relevant>"
    para["vcsvcs"] = "https://salsa.debian.org/debian/" + para["package"] + ".git"
    para["vcsbrowser"] = "https://salsa.debian.org/debian/" + para["package"]
    #######################################################################
    # Finalizing para[...] and sanity checks
    #######################################################################
    para["debmake_dir"] = para["package"] + "-" + para["version"]
    if para["method"] == "tar_copy":
        para["tarball"] = para["url_pkg"] + para["url_ver"] + para["url_ext"]
        para["source_dir"] = para["debmake_dir"] + ".temp_dir"
        if not os.path.exists(para["tarball"]):
            print(
                'E: tarball missing: "{}" for "{}"'.format(
                    para["tarball"], para["method"]
                ),
                file=sys.stderr,
            )
            debmake.debug.debug(" >>> late-para (tar_copy)", type="p", para=para)
            exit(1)
    elif para["method"] == "tar_wget":
        para["tarball"] = para["url_pkg"] + para["url_ver"] + para["url_ext"]
        para["source_dir"] = para["debmake_dir"] + ".temp_dir"
        if os.path.exists(para["tarball"]):
            command = "mv -f " + para["tarball"] + " " + para["tarball"] + ".backup"
            debmake.yn.yn(
                'backup existing "{}" for "{}"'.format(para["tarball"], para["method"]),
                command,
                para["yes"],
                exit_no=False,
            )
    elif para["method"] == "dir_debmake":
        para["tarball"] = para["package"] + "-" + para["version"] + "." + para["tarz"]
        # switch CWD to the parent directory
        if para["url"] == "":
            print(
                'E: invalid URL = "" for method "{}" (never here)'.format(
                    para["method"]
                )
            )
            debmake.debug.debug(
                " >>> late-para (dir_debmake url==" ")", type="p", para=para
            )
            exit(1)
        elif para["url"][0] == "/":  # abspath
            # when invoked without optional positional argument as abspath,
            # para["url"] = no change
            para["source_dir"] = para["url"]
        else:  # relpath
            # para["url"] = no change
            para["source_dir"] = para["url"]
        if not os.path.exists(para["source_dir"]):
            print(
                'E: source_dir missing: "{}" for "{}"'.format(
                    os.path.relpath(
                        para["base_dir"] + "/" + para["source_dir"], para["start_dir"]
                    ),
                    para["method"],
                ),
                file=sys.stderr,
            )
            debmake.debug.debug(
                " >>> late-para (dir_debmake missing source_dir)", type="p", para=para
            )
            exit(1)
    elif para["method"] == "dir_git":
        para["tarball"] = para["package"] + "-" + para["version"] + "." + para["tarz"]
        para["source_dir"] = para["url_pkg"] + para["url_ver"]
        if os.path.exists(para["source_dir"]):
            debmake.yn.yn(
                'backup existing "{}/" for "{}"'.format(
                    para["source_dir"], para["method"]
                ),
                "mv -f " + para["source_dir"] + " " + para["source_dir"] + ".backup",
                para["yes"],
                exit_no=False,
            )
    else:
        print('E: invalid method "{}"'.format(para["method"]))
        debmake.debug.debug(" >>> late-para (else)", type="p", para=para)
        exit(1)
    return


#######################################################################
# Test code
#######################################################################
if __name__ == "__main__":
    parax = dict()
    parax["program_name"] = "foo"
    parax["program_version"] = "9.9.9"
    parax["program_copyright"] = "John Doh"
    parax["source_dir"] = sys.argv[1]
    parax["start_dir"] = os.getcwd()
    print("X: ===================================")
    para(parax)
    for p, v in parax.items():
        print("X: para['{}'] = \"{}\"".format(p, v))
