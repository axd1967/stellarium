# Vendor branching : importing external artifacts

**This file is WIP.**

*In short: if you import anything from outside Stellarium, be it code or data, do not bluntly copy-paste; don't just create a fork of the foreign artefacts if not necessary. The following procedure looks daunting, but that is only appearance.*

## SHORT HOW-TO

### 1/ define a **new vendor**

Follow these steps in order to import external artefacts.

1. **create a vendor branch** to import the vendor (e.g. ``vendor/CELESTRAK``). If the vendor provides multiple products, create the needed subbranches. (e.g. ``vendor/CELESTRAK/SGP4``). The vendor directory can also reside inside a normal directory, such as e.g. [this directory](https://github.com/axd1967/stellarium/tree/b4343449a1d4e66dcc4c2a468dfa068282519687/plugins/Satellites/src/gsatellite).
1. create a suitable **vendor directory** tree (e.g. ``vendor/CELESTRAK``) that will hold the external vendor artefacts.
1. unzip/copy/import/**explode**... the external data ito the (until now empty) vendor directory. This is called a *vendor drop*.
1. Make sure that file/directory *names* do not contain version information as a kind of implicit versioning scheme. Rename when needed. (Example: ``geonames.2.3.tgz`` might untar into ``geonames-2.3/ ``)
1. **Commit** the vendor branch. make sure to add at least some information on the vendor version in the commit message

	``git add -A && git commit``

1. **Tag** the vendor branch, e.g. ``vendor/geonames/1.0``. If the vendor does not provide a clear version number, use the UTC date/time of the drop, formatted as ISO: ``vendor/geonames/2021-09-09T1200``
1. **Switch** to your task branch
1. **merge** the vendor branch. *Do not delete the vendor branch.*
1. Add and commit a ``VENDOR.md`` file to ``vendor/CELESTRAK/`` that contains relevant **metadata** and instructions to help finding back the source. Avoid top-level (domain) adresses, try to make life easy for anyone wanting to update the data. Consider including the keyword "VENDOR" somewhere so that it can be grepped if needed.
1. Do whatever is needed to **localise** the vendor artefacts (source code, data, ...) into your project. This must be done in your task branch, never in the vendor branch. Often, source code will not run or compile completely. Sometimes, data needs to be transformed; include scripts to run migrations/conversions, because future vendor drops might require them.
1. Have your task branch **integrated** into your main branch. Your project now contains folowing:
	- a new vendor directory
	- a vendor branch
	- optionally, modified vendor code to make the vendor work seamlessly in your project

### 2/ perform a **vendor drop**
 When the vendor publishes an update, follow these steps to ingest those changes.

*FIXME: markdown item numbering issues here, due to code blocks...*

1: **Switch** to the vendor branch

```
git switch branch
```
2: **empty** the vendor directory  

```
cd vendor directory
git ls-files -z | xargs -0 rm -f
```
(see ``git help git-rm`` for details, search for "vendor".)  

3: replace/**explode**/unzip/untar/...  

4: **Commit** the vendor drop  

```
   git add -A
   git commit
```
5: **Tag** the vendor branch with a vendor tag (``vendor/<vendor name>/<vendor product>/<tag>``) where `<tag>` is either a tag available from the vendor, or otherwise the ISO date/time of the vendor drop.

6: Merge the updated vendor branch to ``master`` (or, more probably, via an intermediate task/feature/bugfix branch, often in order to update local stuff). Run migration scripts if needed.

7. Deal with conflicts when needed. Such conflicts are expected to arise when the vendor changed something that was also changed locally, or when your project contributed to the vendor.

This is also needed when the external data disappears: in that case, mention that the external data is no longer available to the public to avoid developers searching for it (or even worse, continue with a copy that still exists elsewhere!! Such a copy does not belong on the vendor branch).

### 3/ contribute to the vendor project

It may happen that you find a bug in the vendor artefacts and can provide a fix.
Here are the steps to follow.
Local *adaptations* are not meant to be shared with the vendor.

1. create a "contribution" branch off a vendor tag
1. apply changes as necessary
1. send the contribution branch to the vendor (as a patch, push, bundle, ...)
1. merge the contribution branch to your local branches (task branch, manin, ...)

### 4/ converting existing copy-pasted artefacts to their original vendor status
This is not discussed for now.

## Examples
### 1. SGP4 from Vallado/Celestrak (https://github.com/CelesTrak/fundamentals-of-astrodynamics)
This document's branch (``alex/gh/contrib/docs/vendor-branching``) contains an example how to import Celestrak artefacts in Stellarium.
It demonstrates
- a vendor creation
- a vendor update (pending a real update)
- a local modification (remove trailing whitespaces)

To make a more clear example how source code can move, we import ONLY the SGP4 from following two locations:

1. https://celestrak.org/publications/AIAA/2006-6753/AIAA-2006-6753.zip (Assuming it holds an older version)
1. https://github.com/CelesTrak/fundamentals-of-astrodynamics/tree/main/software/cpp/SGP4/SGP4 (assuming this is the latest version; as there are no tags, we use a specific version)

## Discussion

Stellarium is constantly benefiting from open source artifacts and being enriched with text/data/source files that are **copy-pasted** from places outside Stellarium.

The basic problem with the copy-pasting of external artifacts is **code (or data) rot**. More in detail, **external changes** will not magically appear in Stellarium. But they might be updated outside of Stellarium.

Sometimes this can be solved by using package managers that automate the importing of external "stuff" (typically code) and allow to fine tune which version is to be imported; Python's `pip -e` is a great example of this. But package managers do not allow to modify the imported code out of the box *and* benefit from external updates. Also, package managers are not always the easiest way to deal with vendors, sometimes due to a lack of experience of contributing C++ developers: vendor branching is far easier to work with than configuring package managers, as all the requireed knowlegd resides in how to deal with branching. For example, read the root MAINTAINER_BUSINESS.md; notice that the proposed approach becomes complicated when changes need to be made.

Sometimes this problem is then solved by manual labor: porting the external changes in Stellarium, a laborous approach prone to bugs. See also [this example](https://en.wikipedia.org/wiki/Software_rot#Forked_online_forum_example).

Usually references of some form are added to the source code, e.g. ftp, snail mail, http, ... The problem is that these references might disappear at some point in the future. An example can be found in [this comment](https://github.com/Stellarium/stellarium/blob/dd006bc4095790dba6ceb7fe485284a6804a9fd4/plugins/Satellites/src/Satellites.cpp#L1929-L1931).

### Examples:

Here are several existing artifacts that have been copy-pasted in Stellarium over the years:

- the [JSON parser](https://github.com/Stellarium/stellarium/blob/74b6264d6541f261840a771820262b884a905249/src/core/StelJsonParser.hpp#L28)
- geonames data ([external changes](https://www.geonames.org/recent-changes.html)), stored in [Stellarium data repository](https://github.com/Stellarium/stellarium-data/tags)
- [quasar data](https://github.com/Stellarium/stellarium/blob/master/plugins/Quasars/util/quasars.tsv)
- Almagest data (minor fixes, of course - this is essentially frozen data)
- HTC algorithms (Helene, Telesto, and Calypso (Lagrangian satellites of Dione) - taken from [IMCCE](ftp://ftp.imcce.fr/pub/ephem/satel/htc20/htc20.f) ? )
- various libraries under [src/external](https://github.com/Stellarium/stellarium/tree/master/src/external):
- the [gsatellite directory](https://github.com/Stellarium/stellarium/tree/master/plugins/Satellites/src/gsatellite) seems to contain a lot of external code that has been modified locally.
- The SPG4 algorithm (see also [WP](https://en.wikipedia.org/wiki/Simplified_perturbations_models) updated 2020-03-12)
	- used in the [satellite plugin](https://github.com/Stellarium/stellarium/blob/e75b00e6c249747c198fe0e2badd77a4adab9415/plugins/Satellites/src/Satellites.hpp#L56-L57) ). 
	- It should be replaced by vendor dropped and then adapted  (See Vallado link above)
	- Even minor changes should receive the vendor treatment: https://github.com/Stellarium/stellarium/blob/9910a2f05c52d4d9f351ff490c9bc4d99670df1f/plugins/Satellites/README#L61-L63
- and, of course, how could we forget: the [various ephemeris algorithms](https://github.com/Stellarium/stellarium/commits/master/src/core/planetsephems) (examples are also `jpleph.cpp`, `elp82b.h`, `gust86.h`, `htc20b.c` and `vsop87.c`). Their true source is [JPL](https://ssd.jpl.nasa.gov/planets/eph_export.html) and VSOP ([FTP](ftp://ftp.imcce.fr/pub/ephem/planets/vsop87)). Some random googling shows that the problem exists elsewhere too (e.g. Celestia):
	- https://github.com/Bill-Gray/jpl_eph/blob/master/jpleph.h
	- [Stanford JSOC](http://jsoc.stanford.edu/cvs/JSOC/proj/timed/apps/Attic/jpleph.c?hidecvsroot=1&search=None&hideattic=1&sortby=rev&logsort=date&rev=1.1&content-type=text%2Fvnd.viewcvs-markup&diff_format=h)
	- https://apollo.astro.amu.edu.pl/PAD/pmwiki.php?n=Dybol.JPLEph
	- [Celestia](http://celestia.simulatorlabbs.com/CelSL/src/celephem/)
- [SOFA sourcecode](https://www.iausofa.org/) (*Standards Of Fundamental Astronomy*), also mentioned in [Planet.cpp](https://github.com/Stellarium/stellarium/blob/ba80d33d4bc83d72fc15cca53f798cd9439482cf/src/core/modules/Planet.cpp#L1648).
- ironically, [CPM.cmake](https://github.com/cpm-cmake/CPM.cmake) also deserves vendor branching, as [v0.42](cmake/modules/CPM.cmake) was dropped but has evolved past v1.0.
- tons of tools imported for the web version (https://github.com/Stellarium/stellarium-web-engine/tree/master/ext_src)

Potential candidates for using vendor branching, other examples

-  Marc van der Sluys' [Constellation lines](https://github.com/MarcvdSluys/ConstellationLines) as a separate Sky Culture
- [meshwarp sample code](http://paulbourke.net/dataformats/meshwarp/) : yes, the sample code.
- [time ephemerides](http://timeephem.sourceforge.net/index.php)
- although less likely, copy-pasted snippets from Qt examples *could* be candidates ([example](https://github.com/Stellarium/stellarium/blob/2db52c18bc87aaefa00d3d4a280969349634af8f/src/gui/StelGuiItems.cpp#L352))
- [DASTCOM](https://ssd.jpl.nasa.gov/horizons/manual.html#dastcom): documentation and Fortran code
- API documentation, e.g. for [HORIZONS](https://ssd-api.jpl.nasa.gov/doc/horizons_file.html)
- [SPICE](https://naif.jpl.nasa.gov/naif/) data
- upcoming [OMM schema](https://spacedatastandards.org/#/schemas/OMM) (although this will be less trivial to deal with : TODO)

Although some examples above are unlikely to ever change - or be very ephemeral (sic) - the reasoning is always: prevent rather than cure, and exercise a lot, until it becomes second nature. Just keep Murphy's Law in mind...

### The problem

Notice how it is not always obvious to trace back the original files. In the case of ephemeride routines, these reside in "ancient", core Stellarium files, it is extremely likely that they were copied (and *maybe* recent changes have been manually  and painfully incorporated in Stellarium). One aspect of the recommended vendor branch procedure details how to include such *meta information* so as to help find back the (original, root) source at all times.

The external (source) version of such artifacts will often continue to evolve, but these modifications obviously will not be magically reflected in the project repository, thus *sometimes, if not often* leading to artifacts slowly getting totally outdated (hence the term "[code rot](https://en.wikipedia.org/wiki/Software_rot)").

Importing external artifacts therefore requires a specific (and in this case a *simple* - believe me, it is not rocket science - as well as generic) approach: the **Vendor Branch** approach. Other approaches exist, such as subtrees (but this is not part of core Git) and submodules (in case the external artifacts are versioned under Git, BUT submodules do not provide the flexibility of vendor branching), but have inconveniences and are not discussed here; the proposed Vendor Branch approach is KISS: *simple to apply to novice programmers*. By the way, the approach is valid in any VCS, such as SVN (where it seems to have emerged), Git, Mercurial, ClearCase, TFS, cvs, you name it.

Importing external artefacts in vendor branches will also provide insight in what changed in those artefacts, just by inspecting the "diff" between successive vendor versions. Normally such changes should also be announced by the vendor.

## The solution
1. Keep external information alive (and updated) on a **separate** branch, called a "**vendor branch**" . Every copied dataset/tool/sourcecode lives in its own vendor branch (and in its own (sub)directory). A vendor branch tracks a *pristine* copy/mirror of the external data.
1. Ideally, the external information is stored in a separate directory (e.g. ``external/<vendor>/<toolname>``). But the approach works just as fine for individual files.
1. A ``VENDOR`` file - which is added in our ``master`` version of the vendor data - explains where the external/original information can be found, so that it can be updated when necessary.
1. **vendor tags** describe which version of the vendor artifacts has been imported (e.g. ``vendor/geonames/2021-08-21``; do use the ISO date/time format; if possible, also include the vendor's tag info.)
1. The vendor branch is merged to wherever it is needed (normally a feature branch, which will eventually be merged to ``master``)
1. If needed (which is often the case), external information is modified *locally* (usually via a feature/master branch, but *never* in its vendor branch)
1. Ideally, issues in the vendor artifacts should be reported to the vendor, so that updates can then be imported back via a fresh *vendor drop*. Alternatively, a developer can solve issues locally, but *never* in the vendor branch. Alternatively, a fix branch can be created from the vendor branch and a patch transmited to the vendor as well as merged in ``master``.

Sometimes, conversion routines need to be written or updated so that external data fits with the project. These routines do not belong in the vendor branch, but in the project itself.

## Notes

### coding style/conventions

When modifying vendor code, stick to the vendor coding style/conventions. Rewriting for readbility etc. will likely lead to massive conflicts at the next vendor drop.

### dealing with trailing whitespace

TODO: add directives how to deal with external artefacts originating from other platform environments.

Git tips (TO CONFIRM):

- check your current global/local/worktree whitespace handling
```
	git config --get-all --show-origin core.whitespace
	git config --global core.whitespace trailing-space,-space-before-tab,indent-with-non-tab,cr-at-eol
```
- enable your repo's pre-commit hook (it checks for various whitespace issues. See also ``git help hooks``

### ...and platform end of line issues

TODO: replace with ``.gitattributes`` ?

- check line ending handling
```
	git config --get-all --show-origin core.autocrlf # empty == 'false'
	git config --get-all --show-origin core.safecrlf # empty == 'false'
	git config --get-all --show-origin core.eol # empty = 'native'
```
- make sure...
- as a **Windows** developer, that CRLF is converted to LF when comitting:
```
	$ git config --global core.autocrlf true
```
- as a **Linux** dev, ensure that
```
	git config --global core.autocrlf input
```
 See also
- ``git help config``
- https://git-scm.com/book/en/v2/Customizing-Git-Git-Configuration
- https://adaptivepatchwork.com/2012/03/01/mind-the-end-of-your-line/
- https://docs.github.com/en/get-started/git-basics/configuring-git-to-handle-line-endings

### Schema
Sometimes a format is accompanied by a metadata section describing the format of the data. This metadata is an important artefact to commit to an vendor branch.

### When conflicts are no longer manageable

In some cases, merging vendor updates may become too difficult if not impossible. Nevertheless, vendor drops will continue to provide the means to port changes, by allowing the developer to study at least what changed in the vendor branch, and apply those changes manually...

``git rerere`` might become helpful.

### Importing vendor code written in other languages

If the artifact is not usable without extensive rewriting (e.g. Fortran code in a C++ project), it might still make sense to vendor the original file and keep it as a neutral (uncompiled) text file that will serve as an excellent reference.

This also applies for cases where explanatory/example (pseudo) sourcecode is offered; this code is essential documentation that the vendor will update occasionally.

A typical example is the set of [JPL DExxx development ephemerides](https://ssd.jpl.nasa.gov/planets/eph_export.html), that are accompanied by important documentation *that is to be stored in the vendor branch too*:

- https://ssd.jpl.nasa.gov/ftp/eph/planets/ascii/ascii_format.txt
- https://ssd.jpl.nasa.gov/ftp/eph/planets/fortran/ (complete!) (includes https://ssd.jpl.nasa.gov/ftp/eph/planets/fortran/userguide.txt)
- https://ssd.jpl.nasa.gov/ftp/eph/planets/other_readers.txt

Should any of those "other readers" be used in any way in Stellarium, then these belong in separate vendor branches.

### example: VSOP87 data

VSOP87 is outdated, but the approach remains the same for VSOP2013 (as well as JPL).

The data available as VSOP [FTP](ftp://ftp.imcce.fr/pub/ephem/planets/vsop87) has - a long time ago - been manually (and heroically) merged/transformed into a [sourcecode file](https://github.com/Stellarium/stellarium/blob/v0.21.2/src/core/planetsephems/vsop87.c). Such a transformed file is very difficult to update should a change appear in the original. Note that the current VSOP87 artifacts seem to be the ultimate (maybe only) version (and at first sight there were no modifications *- wow, code without bugs...*), later ephemeris iterations seem to take a different approach (eg VSOP2010, VSOP2013 using Chebyshev polynomials rather than elliptic elements). In 2013 (after VSOP2013), a small change happened in VSOP2010; such a change could have been identified with correct vendor branching (but was also [announced](ftp://ftp.imcce.fr/pub/ephem/planets/vsop2010/revision-notice.pdf).

Including the raw data files would be ideal, but a massive overkill with an unacceptable impact on executable size as well as startup time.

A solution could be to use scripts that process the original data files available via ftp, and convert the data files in a form than can be included in Stellarium; this is what very likely occurred when creating `vsop87.c`: notice how that file is in fact a huge data file with a small executable "appendix". Scripts should be run that "somehow" transform the VSOP data files into an `.hpp` file that is then included in the `vsop87.c` file, that in itself refers to the example Fortran code that will be managed in the vendor branch (see below). Normally, generated files (such as the proposed `.hpp`) should not be versioned, but it would be too heavy to put the burden to recompile those files every time. Instead, the generation should be left to the core Stellarium team. The generated header file should certainly bear a big warning "THIS IS A GENERATED FILE" (with sufficient explanation by what script it was generated).

What belongs in the vendor branch of (eg) [VSOP2013](ftp://ftp.imcce.fr/pub/ephem/planets/vsop2013) (e.g. branch AND directory `vendor/IMCCE.FR/ephem/planets/VSOP/2013`) ?

- PDF/Word/text files
- Fortran example code (`.f`)

These files describe formats and algorithms and therefore represent the essential documentation that developers need in order to maintain the transformation scripts and `.C` files, without having to dig for them on the Internet. (It is unlikely that these files will change, nevertheless they are managed by an outside entity and therefore should be tracked with a vendor branch.)

**Optionally**, a copy of the data files *could* be stored at [Stellarium-data](https://github.com/Stellarium/stellarium-data/), but we may assume that [IMCCE](https://www.imcce.fr/) (*L’Institut de mécanique céleste et de calcul des éphémérides*) can offer sufficient guarantees to maintain the data for a very long time period.

### How to deal with module files that are updated externally and still not vendored internally

The basic idea is to create a vendor branch with the new artifact, and do some manual "undo-redo" work.

### Version information in vendor file/directory paths

Sometimes, developers add directories/files with path names containing version information. An example is the FAQ file of [this landscape](http://www.alienbasecamp.com/Stellarium/sun.htm). 

This is a bad practice, usually done by developers that do not have access to a good VCS.

In such cases, the version information should be removed before committing the vendor drop; this will present the additional advantage that the history of such a file becomes available. This is a delicate step, as the "pristine copy" requirement is no longer fulfilled. If filename information is part of the correct functioning of the imported artifacts (e.g. it is also referenced in vendor scripts, in linked data, etc), then you are facing a difficult problem. In such a case (for now), it might be better to not rename the vendor file paths at all and accept that file history must be discovered by other means (e.g. a manual diff).

### Using data from other users

The vendor branch approach also works for users that want to keep track of other user's configuration data or scripts while at the same time apply local changes. This works better for file formats that are easily merged because being insensitive to line numbers, such as YAML or - even better, but neither are supported by Qt - KVN; a bad example is the INI numbering format chosen in the [Ocular config files](https://github.com/Stellarium/stellarium/blob/ba80d33d4bc83d72fc15cca53f798cd9439482cf/plugins/Oculars/resources/default_ocular.ini).

## See also
- https://github.com/brettlangdon/git-vendor
- In the Stellarium project:
	- https://github.com/Stellarium/stellarium/discussions/1856
	- https://github.com/Stellarium/stellarium/pull/1906
	- https://github.com/axd1967/stellarium/tree/contrib/docs/vendor-branching
	- https://github.com/Stellarium/stellarium/wiki/Branching-Strategy (defunct but a copy exists)
	- https://github.com/CelesTrak/fundamentals-of-astrodynamics/discussions/173
- https://svnbook.red-bean.com/en/1.8/svn.advanced.vendorbr.html
- https://blog.bigsmoke.us/2009/07/20/svn-vendor-branches
- https://stackoverflow.com/questions/tagged/vendor-branch?sort=votes
- https://en.wikipedia.org/wiki/Branching_%28version_control%29#Motivations_for_branching
- https://en.wikipedia.org/wiki/Software_rot
- https://en.wikipedia.org/wiki/Copypasta#Technology
- "*[copy-paste is evil](https://stackoverflow.com/questions/2490884/why-is-copy-and-paste-of-code-dangerous)*")
- https://www.cisa.gov/resources-tools/resources/product-security-bad-practices: _"Cache copies of all open-source dependencies within the manufacturer’s own build systems and do not update products or customer systems directly from unverified public sources."_

Think vendor branching is difficult? Eat [this](https://www.refontelearning.com/blog/tle-to-omm-six-digit-catalog-migration)!

