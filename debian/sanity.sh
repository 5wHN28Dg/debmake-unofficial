#!/usr/bin/sh -e
# Sanity check of source tree
for f in src/debmake/*.py ;
  do
    echo " ... testing $f for python syntax"
    python3 -m py_compile $f || exit 1
  done
# Checking hardcoded versions
# debian/changelog
DEBIAN_VERSION="$(dpkg-parsechangelog -S "Version")"
# src/debmake/__init__.py
PYCODE_VERSION="$(sed -n -e '/^__version__/s/^__version__ = "\([^"][^"]*\)".*$/\1/p' src/debmake/__init__.py)"
if [ "$DEBIAN_VERSION" = "$PYCODE_VERSION" ]; then
  echo "All version OK: $DEBIAN_VERSION"
else
  echo "XXX version mismatch XXX"
  echo "DEBIAN_VERSION = $DEBIAN_VERSION @ debian/changelog"
  echo "PYCODE_VERSION = $PYCODE_VERSION @ src/debmake/__init__.py"
  exit 1
fi

