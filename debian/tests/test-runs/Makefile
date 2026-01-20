#
# This is used for manual testing
#
DEBUG = spd
export DEBUG

all:
	mkdir foo10 ; cd foo10 ; echo "FOO" >FOO ; debmake -p debhello -u 1.0 -n -x0
	mkdir foo11 ; cd foo11 ; echo "FOO" >FOO ; debmake -p debhello -u 1.1 -n -x1
	mkdir foo12 ; cd foo12 ; echo "FOO" >FOO ; debmake -p debhello -u 1.2 -n -x2
	mkdir foo13 ; cd foo13 ; echo "FOO" >FOO ; debmake -p debhello -u 1.3 -n -x3
	mkdir foo14 ; cd foo14 ; echo "FOO" >FOO ; debmake -p debhello -u 1.4 -n -x4
	mkdir foo20 ; cd foo20 ; echo "FOO" >FOO ; debmake -p debhello -y -u 2.0 -r 1 -t -x0
	mkdir foo21 ; cd foo21 ; echo "FOO" >FOO ; debmake -p debhello -y -u 2.1 -r 1 -t -x1
	mkdir foo22 ; cd foo22 ; echo "FOO" >FOO ; debmake -p debhello -y -u 2.2 -r 1 -t -x2
	mkdir foo23 ; cd foo23 ; echo "FOO" >FOO ; debmake -p debhello -y -u 2.3 -r 1 -t -x3
	mkdir foo24 ; cd foo24 ; echo "FOO" >FOO ; debmake -p debhello -y -u 2.4 -r 1 -t -x4
	mkdir foo32 ; cd foo32 ; echo "FOO" >FOO ; debmake -p debhello -y -u 3.2 -r 1 -t -x2 -b"-,-doc,libdebhello1,libdebhello1-dev"

clean:
	rm -rf foo*
	rm -rf debhello*
