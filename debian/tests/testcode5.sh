#!/bin/sh -e
# project_ver.orig.tar.xz w/o project-ver/
LC_ALL=C.UTF-8
export LC_ALL

# non-native from archive.orig.tar.xz using -a
PROJECT=foo-5.0
PROJECTX=foo_5.0
rm -f ${PROJECTX}*.tar.?z
rm -rf ${PROJECT}
mkdir ${PROJECT}
echo "DUMMY ${PROJECT}" > ${PROJECT}/dummy-${PROJECT}
tar --xz -cvf ${PROJECTX}.orig.tar.xz ${PROJECT}
rm -rf ${PROJECT}
debmake ${PROJECTX}.orig.tar.xz
cd ${PROJECT} || exit 1
test -x debian/rules
cd .. || exit 1

