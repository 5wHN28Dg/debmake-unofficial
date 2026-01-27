#!/bin/sh -e
# check if installed as executable
LC_ALL=C.UTF-8
export LC_ALL
debmake --version | grep -q -e 'Copyright © [-0-9 ]* Osamu Aoki <osamu@debian.org>'

