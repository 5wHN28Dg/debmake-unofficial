#!/bin/sh -e
# tar.gz with project-ver/ in tree debmake -x0
LC_ALL=C.UTF-8
export LC_ALL

# non-native source tree with tar.gz on side
PROJECT=foo-3.0
rm -f ${PROJECT}*.tar.?z
rm -rf ${PROJECT}
mkdir ${PROJECT}
echo "DUMMY ${PROJECT}" > ${PROJECT}/dummy-${PROJECT}
tar -cvzf ${PROJECT}.tar.gz ${PROJECT}
cd ${PROJECT} || exit 1
debmake -x0
test -x debian/rules
cd .. || exit 1

