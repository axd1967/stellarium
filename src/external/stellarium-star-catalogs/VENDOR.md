## VENDOR INFORMATION

This directory contains two related vendors that are currently mentioned as companion code in the UG: (FIXME)

- henrysky (https://github.com/henrysky/stellarium_star_catalogs)
- SceneryMC (https://github.com/SceneryMC/stellarium_star_catalogs) whichis itself a fork of henrysky's.

Note that both are Git repos and actually fork off each other; in these vendor drops the link is broken; both are assumed to be independent. The `git subtree` approach is not used.

(Unfortuantely both suffer from whitespace/endspace issues which force me to bypass my git pre-commit hook.)

Ideally, only one vendor should be vendored: but obviously both seem to work together.
The alternative it to get rid of the external forks (other than for archiving purposes) so that the forks no longer exist.
