#!/bin/sh
# check if debmake works as expected
LC_ALL=en_US.UTF-8
export LC_ALL

# non-native from archiveorig.tar.xz using -a
PROJECT=foo-5.0
PROJECTX=foo_5.0
rm -f ${PROJECTX}*.tar.?z
rm -rf ${PROJECT}
mkdir ${PROJECT}
echo "DUMMY ${PROJECT}" > ${PROJECT}/dummy-${PROJECT}
tar --xz -cvf ${PROJECTX}.orig.tar.xz ${PROJECT}
rm -rf ${PROJECT}
debmake -a ${PROJECTX}.orig.tar.xz 2>&1
cd ${PROJECT} || exit 1
test -x debian/rules
cd .. || exit 1

