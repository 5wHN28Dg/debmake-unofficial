#!/bin/sh -e
# project-ver/ in tree debmake
LC_ALL=C.UTF-8
export LC_ALL

# non-native without any origtar..\\ (auto -t option)
PROJECT=foo-4.0
rm -f ${PROJECT}*.tar.?z
rm -rf ${PROJECT}
mkdir ${PROJECT}
echo "DUMMY ${PROJECT}" > ${PROJECT}/dummy-${PROJECT}
cd ${PROJECT} || exit 1
debmake
test -x debian/rules
cd .. || exit 1

