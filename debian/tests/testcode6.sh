#!/bin/sh -e
# debmake project-ver/ with different -u verx
LC_ALL=C.UTF-8
export LC_ALL

# non-native without any origtar..\\ (auto -t option)
# version less project and -u version
PROJECT=foo
VERSION=6.5.0~pre
rm -f ${PROJECT}*.tar.?z
rm -rf ${PROJECT}
mkdir ${PROJECT}
echo "DUMMY ${PROJECT}" > ${PROJECT}/dummy-${PROJECT}
cd ${PROJECT} || exit 1
debmake -u "${VERSION}"
cd .. || exit 1
cd "${PROJECT}-${VERSION}" || exit 1
test -x debian/rules
cd .. || exit 1

