# Uncomment to active options. See dpkg-source(1)
#
# Never add debian/local-options to dgit maintained source.
#
# This file contains a list of long options that should be automatically
# prepended to the set of command line options of a dpkg-source --build call.

# Remove this file if you use dgit-maint-merge(7) workflow and the git
# repository records the modified source for outside of debian/ directory.

# When the git repository records the unmodified upstream source for outside of
# debian/ directory, uncomment the following:
#abort-on-upstream-changes
#unapply-patches

# Setting these here instead of debian/options makes dpkg-source long options
# applied only for the team builds based on the VCS repository.
# NMU builds based on the Debian source package are not affected.

# For patch-unapplied workflows, see:
#   * Workflow using diff -u
#       https://www.debian.org/doc/manuals/debmake-doc/ch04.en.html#diff-u
#   * Workflow using dquilt
#       https://www.debian.org/doc/manuals/debmake-doc/ch04.en.html#dquilt
#   * Workflow using dpkg-source commit (commit only patch to VCS after dpkg-source commit)
#       https://www.debian.org/doc/manuals/debmake-doc/ch04.en.html#dpkg-source-commit
#   * Workflow to use gbp-buildpackage(1) with pristine-tar
#   * Workflow described in dgit-maint-gbp(7)
