#!/bin/sh -e
# check if debmake works as expected
# debmake project-ver/ for native
LC_ALL=C.UTF-8
export LC_ALL

# native
PROJECT=foo-7.0
rm -f ${PROJECT}*.tar.?z
rm -rf ${PROJECT}
mkdir ${PROJECT}
echo "DUMMY ${PROJECT}" > ${PROJECT}/dummy-${PROJECT}
cd ${PROJECT} || exit 1
debmake -n -x0
test -x debian/rules
cd .. || exit 1

