Never add this debian/local-patch-header file to dgit maintained source tree
since dgit is incompatible.

Even when the git repository records the unmodified upstream source for
outside of debian/ directory, there is no strong reason to add this file for
the current dpkg-source (>1.16).

Thus this is moved to -x4 category for debmake.
===
