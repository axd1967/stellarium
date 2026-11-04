# Vendor artifacts in Stellarium

# DRAFT

---

Document revisions

2026-11-05 v0.1

---

This file is being reformatted.

This document lists vendor branching issues in Stellarium.

- https://github.com/CelesTrak/fundamentals-of-astrodynamics/discussions/173
- https://github.com/cpm-cmake/CPM.cmake/discussions/720

Related projects:

1. the recipe for a generic vendor branch (VB) strategy is explained at https://github.com/axd1967/vendor-branching.
1. For SGPO4 related VB aspects, see https://github.com/axd1967/SGP4-vendor-branching

### The problem

The Stellarium project regularly "copy-pastes" files from the outside. 

A solution to this problem is called [Vendor Branching](https://github.com/axd1967/vendor-branching).

Stellarium is constantly benefiting from open source artifacts and being enriched with text/data/source files that are **copy-pasted** from places outside Stellarium.
Notice how it is not always obvious to trace back the original files. In the case of ephemeride routines, these reside in "ancient", core Stellarium files, it is extremely likely that they were copied (and *maybe* recent changes have been manually  and painfully incorporated in Stellarium). One aspect of the recommended vendor branch procedure details how to include such *meta information* so as to help find back the (original, root) source at all times.

Sometimes this can be solved by using package managers that automate the importing and updating of external "stuff" (typically code) and - important - allow to fine tune which version is to be imported; Python's `pip -e` is a great example of this. But package managers do not allow to modify the imported code out of the box *and* benefit from external updates. Also, package managers are not always the easiest way to deal with vendors, sometimes due to a lack of experience of contributing C++ developers. **Vendor branching is far easier to work with** than configuring package managers, as all the required knowledge resides in how to deal with branching. For example, read the root [MAINTAINER_BUSINESS.md](MAINTAINER_BUSINESS.md); notice that the proposed approach becomes complicated when changes need to be made.

## artefacts that have been copy-pasted into Stellarium
Please note: this was the common, if not standard approach by most devs. 

https://github.com/Stellarium/stellarium/issues?q=vendor_branching

Notice how it is not always obvious to trace back the original files. In the case of ephemeride routines, these reside in "ancient", core Stellarium files, it is extremely likely that they were copied (and *maybe* recent changes have been manually  and painfully incorporated in Stellarium). One aspect of the recommended vendor branch procedure details how to include such *meta information* so as to help find back the (original, root) source at all times.

## Future candidates

- The reference SGP4 implementation from Vallado/Celestrak (https://github.com/CelesTrak/fundamentals-of-astrodynamics). See also https://github.com/axd1967/SGP4-vendor-branching.
- An upcoming Gaia DR3 draft patch by SceneryMC uses explicit references to two external repositories.
See [Gaia DR3 PR](https://github.com/Stellarium/stellarium/pull/4991)... It refers to forked code from
	- Henry Leung (https://github.com/henrysky/stellarium_star_catalogs)
	- "SceneryMC" himself refers to artefacts in his repo (https://github.com/SceneryMC/stellarium_star_catalogs) (which - sic - forks off Leung's...)
	- `parse_hip_catalog.py`
	- `simbad_query_hipsaohdhr.py`
	- `py/geodesic.py`
Note: Henry Leung - whose repo is forked by SceneryMC - has a bad habit of renaming files. This makes vendoring more difficult.
A branch has been pushed [here](https://github.com/axd1967/stellarium/tree/PR-4991-with-vendoring) to convert the Gaia DR3 PR to a "vendor compliant" approach.

## Discussion


### Examples:

Here are several existing artifacts that (still) get copy-pasted in Stellarium:

- several places:
	- a dependeny to an external repo: https://github.com/axd1967/stellarium/commit/5f334842ec6205f2cc9d33dfbf6f3c5345c66b92
	- https://github.com/Stellarium/stellarium/commit/7e2d7a952579cb88e214fd5bc275b5cc457dd94e
	- https://github.com/Stellarium/stellarium/commit/186b06fa215bd28ea03cc291dc861b552af8d99a (especially https://github.com/Stellarium/stellarium/commit/186b06fa215bd28ea03cc291dc861b552af8d99a#diff-1e7de1ae2d059d21e1dd75d5812d5a34b0222cef273b7c3a2af62eb747f9d20aR756)
	- https://github.com/Stellarium/stellarium/commit/01976bd723b66526f04f4e11bad3a70ec169ac1e
	- https://github.com/Stellarium/stellarium/commit/b22283f63bbaa21482c66367d4ab325a7855f55a
	- https://github.com/Stellarium/stellarium/commit/b3d6cee6e7338ec64ac77f79d93742f274fd5cd5
- various libraries under [src/external](src/external)
- references to CdC (eg https://github.com/pchev/skychart/blob/b2e4038f70bdff0cf994846aea39dff2c05a03bc/skychart/cu_catalog.pas#L6572-L6586)
- [CPM.cmake](https://github.com/cpm-cmake/CPM.cmake) [cmake/modules/CPM.cmake)](cmake/modules/CPM.cmake). This is a simple example where vendoring can further simplify things. For example, the history of [CPM.cmake](https://github.com/Stellarium/stellarium/commits/master/cmake/modules/CPM.cmake) is no more than a series of *manual* updates that can perfectly be done with successive vendor drops.
- copying code
	- from [Celestia](https://github.com/Stellarium/stellarium/blob/e0750c36b5becfe8704424edb6fd40e5c51531af/ChangeLog#L1444) *(TODO: find out which code that is)*
	- note: [src/external/qtcompress/qzip.cpp](src/external/qtcompress/qzip.cpp) is a copy from QtGui 2013 and which has itself (sic) been modified
- the [JSON parser](https://github.com/Stellarium/stellarium/blob/74b6264d6541f261840a771820262b884a905249/src/core/StelJsonParser.hpp#L28)
- geonames data ([external changes](https://www.geonames.org/recent-changes.html)), stored in [Stellarium data repository](https://github.com/Stellarium/stellarium-data/tags)
- [quasar data](plugins/Quasars/util/quasars.tsv)
- Almagest data (minor fixes, of course - this is essentially frozen data)
- HTC algorithms (Helene, Telesto, and Calypso (Lagrangian satellites of Dione) - taken from [IMCCE](ftp://ftp.imcce.fr/pub/ephem/satel/htc20/htc20.f) ? )
- The SPG4 routines
	- please see https://github.com/axd1967/SGP4-vendor-branching
	- the [gsatellite directory](plugins/Satellites/src/gsatellite) seems to contain a lot of external code that has been modified locally.
	- used in the [satellite plugin](https://github.com/Stellarium/stellarium/blob/e75b00e6c249747c198fe0e2badd77a4adab9415/plugins/Satellites/src/Satellites.hpp#L56-L57).
	- It should be vendored and then adapted  (See Vallado link above)
	- Even minor changes should receive the vendor treatment: an example in the [Satellite plugin](https://github.com/Stellarium/stellarium/blob/9910a2f05c52d4d9f351ff490c9bc4d99670df1f/plugins/Satellites/README#L61-L63)
- and, of course, how could we forget: the [various ephemeris algorithms](src/core/planetsephems) (examples are also `jpleph.cpp`, `elp82b.h`, `gust86.h`, `htc20b.c` and `vsop87.c`). Their vendor is [JPL](https://ssd.jpl.nasa.gov/planets/eph_export.html) and VSOP ([FTP](ftp://ftp.imcce.fr/pub/ephem/planets/vsop87)).
- (TODO: SOURCE) [SOFA sourcecode](https://www.iausofa.org/) (*Standards Of Fundamental Astronomy*), also mentioned in [Planet.cpp](https://github.com/Stellarium/stellarium/blob/ba80d33d4bc83d72fc15cca53f798cd9439482cf/src/core/modules/Planet.cpp#L1648).
- tons of tools imported for the web version (https://github.com/Stellarium/stellarium-web-engine/tree/master/ext_src)

Potential candidates for using vendor branching, other examples

-  Marc van der Sluys' [Constellation lines](https://github.com/MarcvdSluys/ConstellationLines) as a separate Sky Culture
- [time ephemerides](http://timeephem.sourceforge.net/index.php)
- although less likely, copy-pasted snippets from Qt examples *could* be candidates ([example](https://github.com/Stellarium/stellarium/blob/2db52c18bc87aaefa00d3d4a280969349634af8f/src/gui/StelGuiItems.cpp#L352))
- [DASTCOM](https://ssd.jpl.nasa.gov/horizons/manual.html#dastcom): documentation and Fortran code
- API documentation, e.g. for [Horizons API](https://ssd-api.jpl.nasa.gov/doc/horizons_file.html)
- [SPICE](https://naif.jpl.nasa.gov/naif/)
	- https://naif.jpl.nasa.gov/naif/toolkit.html
	- https://naif.jpl.nasa.gov/pub/naif/ (!!)
- contributed scripts, see https://stellarium.org/scripts.html. These are very likely to change over time... 

Some random googling shows that this problem exists in other projects too (e.g. Celestia):

- star catalogs are being corrected after publication (even if they are unlikely to be updated from within Stellarium, so an update might be no more than a basic copy-paste...):
	- [Gaia DR3](stars/hip_gaia3/) (see the [release notes](https://www.cosmos.esa.int/web/gaia-users/archive/release-notes), look for "VERSION 3.2.1 [2023-02-07]")
	- JWST Star Catalog ([documentation](https://jwst-docs.stsci.edu/jwst-observatory-characteristics/jwst-pointing-performance/jwst-guide-stars/jwst-guide-star-catalog-updates))
- [Celestia](http://celestia.simulatorlabbs.com/CelSL/src/celephem/)
- https://github.com/Bill-Gray/jpl_eph/blob/master/jpleph.h
- [Stanford JSOC](http://jsoc.stanford.edu/cvs/JSOC/proj/timed/apps/Attic/jpleph.c?hidecvsroot=1&search=None&hideattic=1&sortby=rev&logsort=date&rev=1.1&content-type=text%2Fvnd.viewcvs-markup&diff_format=h)
- https://apollo.astro.amu.edu.pl/PAD/pmwiki.php?n=Dybol.JPLEph:  
**do notice the phrase** *"According to JPL fortran asc2eph.f (lines 101-102 and 197-198) I added new lines handling RPT and TPT arrays. "*. This is the typical meta issue that vendor branching tries to solve.
Although some examples above are unlikely to ever change - or be very ephemeral (sic) - the reasoning is always: prevent rather than cure, and exercise a lot, until it becomes second nature. Just keep Murphy's Law in mind...

### example: VSOP87 data

VSOP87 is outdated, but the approach remains the same for VSOP2013 (as well as JPL).

The data available as VSOP [FTP](ftp://ftp.imcce.fr/pub/ephem/planets/vsop87) has - a long time ago - been manually (and heroically) merged/transformed into a [sourcecode file](https://github.com/Stellarium/stellarium/blob/v0.21.2/src/core/planetsephems/vsop87.c). Such a transformed file is very difficult to update should a change appear in the original. Note that the current VSOP87 artifacts seem to be the ultimate (maybe only) version (and at first sight there were no modifications *- wow, code without bugs...*), later ephemeris iterations seem to take a different approach (eg VSOP2010, VSOP2013 using Chebyshev polynomials rather than elliptic elements). In 2013 (after VSOP2013), a small change happened in VSOP2010; such a change could have been identified with correct vendor branching (but was also [announced](ftp://ftp.imcce.fr/pub/ephem/planets/vsop2010/revision-notice.pdf).

Including the raw data files would be ideal, but a massive overkill with an unacceptable impact on executable size as well as startup time.

A solution could be to use scripts that process the original data files available via ftp, and convert the data files in a form than can be included in Stellarium; this is what very likely occurred when creating [`vsop87.c`](src/core/planetsephems/vsop87.c): notice how that file is in fact a huge data file with a small executable "appendix". Scripts should be run that "somehow" transform the VSOP data files into an `.hpp` file that is then included in the `vsop87.c` file, that in itself refers to the example Fortran code that will be managed in the vendor branch (see below). Normally, generated files (such as the proposed `.hpp`) should not be versioned, but it would be too heavy to put the burden to recompile those files every time. Instead, the generation should be left to the core Stellarium team. The generated header file should certainly bear a big warning `"THIS IS A GENERATED FILE"` (with sufficient explanation by what script it was generated).

What belongs in the vendor branch of (eg) [VSOP2013](ftp://ftp.imcce.fr/pub/ephem/planets/vsop2013) (e.g. branch AND directory `vendor/IMCCE.FR/ephem/planets/VSOP/2013`) ?

- PDF/Word/text files
- Fortran example code (`.f`)

These files describe formats and algorithms and therefore represent the essential documentation that developers need in order to maintain the transformation scripts and `.C` files, without having to dig for them on the Internet (assuming these will not disappear...). (It is unlikely that these files will change, nevertheless they are managed by an outside entity and therefore should be tracked with a vendor branch.)

**Optionally**, a copy of the data files *could* be stored at [Stellarium-data](https://github.com/Stellarium/stellarium-data/), but we may assume that [IMCCE](https://www.imcce.fr/) (*L’Institut de mécanique céleste et de calcul des éphémérides*) can offer sufficient guarantees to maintain the data for a very long time.

A typical example is the set of [JPL DExxx development ephemerides](https://ssd.jpl.nasa.gov/planets/eph_export.html), that are accompanied by important documentation *that is to be stored in the vendor branch too*:

- https://ssd.jpl.nasa.gov/ftp/eph/planets/ascii/ascii_format.txt
- https://ssd.jpl.nasa.gov/ftp/eph/planets/fortran/ (complete!) (includes https://ssd.jpl.nasa.gov/ftp/eph/planets/fortran/userguide.txt)
- https://ssd.jpl.nasa.gov/ftp/eph/planets/other_readers.txt

Should any of those "other readers" be used in any way in Stellarium, then these belong in separate vendor branches.

### Using config data from other users

The vendor branch approach could also works for users that want to keep track of other user's configuration data (e.g. Ocular config) or scripts while at the same time apply local changes. However, this works better for file formats that are easily merged because being insensitive to *line numbers*, such as YAML or - even better, but neither are supported by Qt - KVN; a bad example is the (Qt backed) INI numbering format (e.g. [Ocular config files](https://github.com/Stellarium/stellarium/blob/ba80d33d4bc83d72fc15cca53f798cd9439482cf/plugins/Oculars/resources/default_ocular.ini)). An improvement is to use [Qt XML](https://doc.qt.io/qt-6/qtxml-index.html). See also https://www.surfsidemedia.in/post/what-are-some-alternatives-to-ini-files-for-configuration-management

## external discussions

### Stellarium
- https://github.com/Stellarium/stellarium/discussions/1856
- https://github.com/Stellarium/stellarium/pull/1906
- https://github.com/axd1967/stellarium/blob/contrib/docs/vendor-branching/VENDOR_BRANCHING.md (this file)
- https://github.com/Stellarium/stellarium/wiki/Branching-Strategy (defunct but a copy exists)

Think vendor branching is difficult? Eat [this](https://www.refontelearning.com/blog/tle-to-omm-six-digit-catalog-migration)!

## BUSY
## TODO

