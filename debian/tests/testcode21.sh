#!/bin/sh -e
# tar.xz with project-ver/
LC_ALL=C.UTF-8
export LC_ALL

# non-native from archive.xz using -a
PROJECT=foo-2.1
rm -f ${PROJECT}*.tar.?z
rm -rf ${PROJECT}
mkdir ${PROJECT}
echo "DUMMY ${PROJECT}" > ${PROJECT}/dummy-${PROJECT}
tar --xz -cvf ${PROJECT}.tar.xz ${PROJECT}
#rm -rf ${PROJECT}
# now you need -y
debmake -x0 -y ${PROJECT}.tar.xz
cd ${PROJECT} || exit 1
test -x debian/rules
cd .. || exit 1

