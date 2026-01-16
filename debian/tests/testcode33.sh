#!/bin/sh
# check if debmake works as expected
LC_ALL=en_US.UTF-8
export LC_ALL

# non-native source tree with tar.gz on side
PROJECT=foo-3.3
rm -f ${PROJECT}*.tar.?z
rm -rf ${PROJECT}
mkdir ${PROJECT}
echo "DUMMY ${PROJECT}" > ${PROJECT}/dummy-${PROJECT}
tar -cvzf ${PROJECT}.tar.gz ${PROJECT}
cd ${PROJECT} || exit 1
debmake -x3 2>&1
test -x debian/rules
cd .. || exit 1

