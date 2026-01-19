#!/bin/sh
# check if debmake works as expected
LC_ALL=en_US.UTF-8
export LC_ALL

# native
PROJECT=foo-7.0
rm -f ${PROJECT}*.tar.?z
rm -rf ${PROJECT}
mkdir ${PROJECT}
echo "DUMMY ${PROJECT}" > ${PROJECT}/dummy-${PROJECT}
cd ${PROJECT} || exit 1
debmake -n 2>&1
test -x debian/rules
cd .. || exit 1

