#!/bin/sh -e
# check if debmake works as expected
LC_ALL=en_US.UTF-8
export LC_ALL

# non-native from archive.xz using -a
PROJECT=foo-2.0
rm -f ${PROJECT}*.tar.?z
rm -rf ${PROJECT}
mkdir ${PROJECT}
echo "DUMMY ${PROJECT}" > ${PROJECT}/dummy-${PROJECT}
tar --xz -cvf ${PROJECT}.tar.xz ${PROJECT}
rm -rf ${PROJECT}
debmake -a ${PROJECT}.tar.xz 2>&1
cd ${PROJECT} || exit 1
test -x debian/rules
cd .. || exit 1

