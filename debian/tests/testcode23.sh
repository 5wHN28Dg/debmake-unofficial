#!/bin/sh -e
# project-ver/ w/o tar.xz (non-native) in-tree
LC_ALL=C.UTF-8
export LC_ALL

# non-native from archive.xz using -a
PROJECT=foo-2.2
rm -f ${PROJECT}*.tar.?z
rm -rf ${PROJECT}
mkdir ${PROJECT}
echo "DUMMY ${PROJECT}" > ${PROJECT}/dummy-${PROJECT}
#tar --xz -cvf ${PROJECT}.tar.xz ${PROJECT}
#rm -rf ${PROJECT}
cd ${PROJECT} || exit 1
debmake -x0
test -x debian/rules
cd .. || exit 1

