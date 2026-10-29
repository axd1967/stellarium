# Vendor branching : importing external artifacts without copy-pasta

**This project is WIP.**

*This file is huge due to the resistance against vendor branching. It should be cut in pieces and moved to the wiki.*

*In short: copy-pasting artefacts is a seemingly easy way to get things imported in a project. The problem is the maintainance effort that will follow. Do not assume the data is "written in stone" and will never change any more (be it inside your project or externally). Instead, every time you import anything from outside Stellarium, be it code or data, ***do not bluntly copy-paste***; don't just create a "fork" of foreign artefacts unless there really is no other way. Following describes the recommended way to import such external artefacts. The procedure looks daunting, but that is only appearance.*

Artefacts can be source code, data files, PDF files, supporting documentation...

Artefacts that can be managed by package managers are not discussed here. An inconvenience of package managers might be that local modifications might be more difficult to manage. This is precisely what vendor branching has been designed for.

Some artefacts are not available as text but in binary formats (eg [Yale Bright Star Catalog](http://tdc-www.harvard.edu/catalogs/catalogsb.html)).

The concept actually dates from the venerable [CVS](https://www.gnu.org/software/trans-coord/manual/cvs/cvs.html) and [SVN](https://subversion.apache.org/blog/)

- How I discovered vendor branches: https://svnbook.red-bean.com/en/1.8/svn.advanced.vendorbr.html
- and I indeed remember CVS already mentioned it long time ago in the Cederqvist PDF: https://www.gnu.org/software/trans-coord/manual/cvs/html_node/Tracking-sources.html (although it didn't mention how to contribute back)

If you don't know about vendor branching, skip following section and go straight to the "Discussion" section.

## SHORT HOW-TO

### 1/ define a **new vendor**

Follow these steps in order to import external artefacts for the first time.

1. **create a vendor branch** to import the vendor (e.g. ``vendor/CELESTRAK``). If the vendor provides multiple products, create the needed subbranches. (e.g. ``vendor/CELESTRAK/SGP4``). The "``vendor/``" segment is only meant to draw the attention to the concept.
1. create a suitable **vendor directory** tree (e.g. ``vendor/CELESTRAK``) that will hold the external vendor artefacts. The vendor directory can also reside inside a normal directory, such as e.g. [this directory](https://github.com/axd1967/stellarium/tree/b4343449a1d4e66dcc4c2a468dfa068282519687/plugins/Satellites/src/gsatellite).
1. unzip/copy/import/**explode**... the external data into the (until now empty) vendor directory. This is called a *vendor drop*.
1. Make sure that extracted file/directory *names* do not contain version information as a kind of implicit versioning scheme. Rename when needed. (Example: ``geonames.2.3.tgz`` might untar into ``geonames-2.3/ ``)
1. **Commit** the vendor branch. Make sure to add at least some information on the vendor version in the commit message

	``git add -A && git commit``

1. **Tag** the vendor branch, e.g. ``vendor/geonames/1.0``. A path structure allows to group tags in a more structured way. If the vendor does not provide a clear version number, use the UTC date/time of the drop, formatted as ISO: ``vendor/geonames/2021-09-09T1200`` or a date/time as stamped by the vendor.
1. **Switch** to your task branch
1. **merge** (avoid fast forward for clarity) the vendor branch. *Do not delete the vendor branch.*
`` git merge --no-ff <vendor branch>``
2. Add and commit a ``VENDOR.md`` file to ``vendor/CELESTRAK/`` that contains relevant **metadata** and instructions to help finding back the source. Avoid top-level (domain) adresses, try to make life easy for anyone wanting to update the data. Consider including the keyword "VENDOR" somewhere so that it can be grepped if needed. Make sure to include any PDF or comparable document that documents the vendor artefact, as well as where that PDF, data file, ... can be found.
1. Do whatever is needed to **localise** the vendor artefacts (source code, data, ...) into your project. This is done in your task branch, never in the vendor branch. Often, source code will not run or compile completely. Sometimes, data needs to be transformed; include scripts to run migrations/conversions, because future vendor drops might require them.
1. Have your task branch **integrated** into your main branch. Your project now contains folowing:
	- a new vendor directory
	- a vendor branch and a vendor tag
	- optionally, modified vendor code to make the vendor work seamlessly in your project
1. **Remember to also push the *vendor* branch and tag**

### 2/ perform a **vendor drop**

 When the vendor publishes an update, follow these steps to ingest those changes.

*FIXME: markdown list item numbering issues here, due to code blocks...*

1: **Switch** to the vendor branch

```
git switch <vendor branch>
```
2: **empty** the vendor directory  

```
cd <vendor directory>
git ls-files -z | xargs -0 rm -f # remove everything. or simply `rm`?
```
(see ``git help git-rm`` for details, search for "[vendor](https://github.com/git/git/blob/master/Documentation/git-rm.adoc#using-git-add--a)". *Do notice BTW that the concept is mentioned in Git!*)  

3: replace/**explode**/unzip/untar/...  

4: **Commit** the vendor drop  

```
   git add -A
   git commit
```
5: **Tag** the vendor branch with a vendor tag (``vendor/<vendor name>/<vendor product>/<tag>``) where `<tag>` is either a tag available from the vendor, or otherwise the ISO date/time of the vendor drop or a vendor's timestamp.

6: Merge the updated vendor branch to ``master`` (or, more probably, via an intermediate task/feature/bugfix branch, often in order to update local stuff). Run migration scripts if needed.

7. Deal with conflicts when needed. Such conflicts are expected to arise when the vendor changed something that was also changed locally, or when your project contributed to the vendor.

This is also needed when the external data disappears: in that case, mention that the external data is no longer available to the public to avoid developers searching for it (or even worse, continue with a copy that still exists elsewhere!! Such a copy does not belong on the vendor branch).

### 3/ contribute to the vendor project

It may happen that you find a bug in the vendor artefacts and can provide a fix.
Here are the steps to follow.
*Local modifications* are not meant to be shared with the vendor.

1. create a "contribution" branch **off a vendor tag**. Always start off an official version that is known by the vendor.
1. apply changes as necessary. merge and test locally. (this is the most git-intensive part). do not change the vendor branch itself.
1. send the contribution branch to the vendor as a patch (see Notes on patching)
1. merge the contribution branch to your local branches (task branch, main, ...)

### 4/ converting existing copy-pasted artefacts to their original vendor status

This is not discussed for now. You should have followed the vendor branch strategy ;-)
This requires courage; most will simply continue to dabble in their local copy.

The steps to follow include

1. create the vendor
1. rip out the old copy-pasta
1. merge the vendor branch
1. re-apply all changes that were performed on the original copy-pasta. This is probably a daunting task.

(TODO)

## Examples

### 1. SGP4 from Vallado/Celestrak (https://github.com/CelesTrak/fundamentals-of-astrodynamics)

This document's branch (``alex/gh/contrib/docs/vendor-branching``) contains an example how to import Celestrak artefacts in Stellarium.
It demonstrates
- a vendor creation
- a vendor update (pending a real update)
- a local modification (remove trailing whitespaces) (NOTE: this kind of change will rise tons of conflicts in the future.)

To make a more clear example how source code can move, we import ONLY the SGP4 from following two locations:

1. https://celestrak.org/publications/AIAA/2006-6753/AIAA-2006-6753.zip (Assuming it holds an older version)
1. https://github.com/CelesTrak/fundamentals-of-astrodynamics/tree/main/software/cpp/SGP4/SGP4 (assuming this is the latest version; as there are no tags, we use a specific version)

### 2. SceneryMC's Stellarium-star-catalogs
An upcoming Gaia DR3 draft patch uses references to two external repositories.
Note: Henry Leung - whose repo is forked by SceneryMC - has a bad habit of renaming files. This makes vendoring more difficult.

A branch has been pushed [here](https://github.com/axd1967/stellarium/tree/PR-4991-with-vendoring) to convert the Gaia DR3 PR to a "vendor compliant" approach.

## Discussion

Stellarium is constantly benefiting from open source artifacts and being enriched with text/data/source files that are **copy-pasted** from places outside Stellarium.

The basic problem with copy-pasting of external artifacts is **code (or data) rot and local adaptations**. More in detail, **external changes** will not magically appear in Stellarium. But they *might* be updated outside of Stellarium. *And often do.* Unless they are written in stone.

Sometimes this can be solved by using package managers that automate the importing and updating of external "stuff" (typically code) and - important - allow to fine tune which version is to be imported; Python's `pip -e` is a great example of this. But package managers do not allow to modify the imported code out of the box *and* benefit from external updates. Also, package managers are not always the easiest way to deal with vendors, sometimes due to a lack of experience of contributing C++ developers. **Vendor branching is far easier to work with** than configuring package managers, as all the required knowledge resides in how to deal with branching. For example, read the root [MAINTAINER_BUSINESS.md](MAINTAINER_BUSINESS.md); notice that the proposed approach becomes complicated when changes need to be made.

Sometimes this problem is then solved by manual labor: porting the external changes in Stellarium, a laborous approach prone to bugs. **Extremely instructive use cases are presented on [Wikipedia](https://en.wikipedia.org/wiki/Software_rot#Forked_online_forum_example)**.

Usually references of some form are added to the source code, e.g. ftp, snail mail, http, ... The problem is that these references might **disappear** at some point in the future. **This happens all the time with personal pages.** An example can be found in [this comment](https://github.com/Stellarium/stellarium/blob/dd006bc4095790dba6ceb7fe485284a6804a9fd4/plugins/Satellites/src/Satellites.cpp#L1929-L1931): **you will get a 404**: the pages are *gone*. *Those pages should somehow have been imported as vendor data.*

### Examples:

Here are several existing artifacts that (still) get copy-pasted in Stellarium:

- the upcoming [Gaia DR3 PR](https://github.com/Stellarium/stellarium/pull/4991)... It refers to forked code from
	- Henry Leung (https://github.com/henrysky/stellarium_star_catalogs)
	- "SceneryMC" (https://github.com/SceneryMC/stellarium_star_catalogs) (which - sic - forks off Leung's...)
	- `parse_hip_catalog.py`
	- `simbad_query_hipsaohdhr.py`
	- `py/geodesic.py`
	- references to CdC (eg https://github.com/pchev/skychart/blob/b2e4038f70bdff0cf994846aea39dff2c05a03bc/skychart/cu_catalog.pas#L6572-L6586)
- [CPM.cmake](https://github.com/cpm-cmake/CPM.cmake) [cmake/modules/CPM.cmake)](cmake/modules/CPM.cmake). This is a simple example where vendoring can further simplify things. For example, the history of [CPM.cmake](https://github.com/Stellarium/stellarium/commits/master/cmake/modules/CPM.cmake) is no more than a series of *manual* updates that can perfectly be done with successive vendor drops.
- copying code
	- from [Celestia](https://github.com/Stellarium/stellarium/blob/e0750c36b5becfe8704424edb6fd40e5c51531af/ChangeLog#L1444) *(TODO: find out which code that is)*
	- note: src/external/qtcompress/qzip.cpp (sic) is a copy from QtGui 2013 and which has been modified
- the [JSON parser](https://github.com/Stellarium/stellarium/blob/74b6264d6541f261840a771820262b884a905249/src/core/StelJsonParser.hpp#L28)
- geonames data ([external changes](https://www.geonames.org/recent-changes.html)), stored in [Stellarium data repository](https://github.com/Stellarium/stellarium-data/tags)
- [quasar data](plugins/Quasars/util/quasars.tsv)
- Almagest data (minor fixes, of course - this is essentially frozen data)
- HTC algorithms (Helene, Telesto, and Calypso (Lagrangian satellites of Dione) - taken from [IMCCE](ftp://ftp.imcce.fr/pub/ephem/satel/htc20/htc20.f) ? )
- various libraries under [src/external](src/external)
- The SPG4 library (see also [WP](https://en.wikipedia.org/wiki/Simplified_perturbations_models) updated 2020-03-12)
	- the [gsatellite directory](plugins/Satellites/src/gsatellite) seems to contain a lot of external code that has been modified locally.
	- used in the [satellite plugin](https://github.com/Stellarium/stellarium/blob/e75b00e6c249747c198fe0e2badd77a4adab9415/plugins/Satellites/src/Satellites.hpp#L56-L57).
	- It should be vendored and then adapted  (See Vallado link above)
	- Even minor changes should receive the vendor treatment: an example in the [Satellite plugin](https://github.com/Stellarium/stellarium/blob/9910a2f05c52d4d9f351ff490c9bc4d99670df1f/plugins/Satellites/README#L61-L63)
- and, of course, how could we forget: the [various ephemeris algorithms](src/core/planetsephems) (examples are also `jpleph.cpp`, `elp82b.h`, `gust86.h`, `htc20b.c` and `vsop87.c`). Their vendor is [JPL](https://ssd.jpl.nasa.gov/planets/eph_export.html) and VSOP ([FTP](ftp://ftp.imcce.fr/pub/ephem/planets/vsop87)).
- [SOFA sourcecode](https://www.iausofa.org/) (*Standards Of Fundamental Astronomy*), also mentioned in [Planet.cpp](https://github.com/Stellarium/stellarium/blob/ba80d33d4bc83d72fc15cca53f798cd9439482cf/src/core/modules/Planet.cpp#L1648).
- tons of tools imported for the web version (https://github.com/Stellarium/stellarium-web-engine/tree/master/ext_src)

Potential candidates for using vendor branching, other examples

-  Marc van der Sluys' [Constellation lines](https://github.com/MarcvdSluys/ConstellationLines) as a separate Sky Culture
- [meshwarp sample code](http://paulbourke.net/dataformats/meshwarp/) : yes, the sample code.
- [time ephemerides](http://timeephem.sourceforge.net/index.php)
- although less likely, copy-pasted snippets from Qt examples *could* be candidates ([example](https://github.com/Stellarium/stellarium/blob/2db52c18bc87aaefa00d3d4a280969349634af8f/src/gui/StelGuiItems.cpp#L352))
- [DASTCOM](https://ssd.jpl.nasa.gov/horizons/manual.html#dastcom): documentation and Fortran code
- API documentation, e.g. for [HORIZONS](https://ssd-api.jpl.nasa.gov/doc/horizons_file.html)
- [SPICE](https://naif.jpl.nasa.gov/naif/) data
- upcoming [OMM schema](https://spacedatastandards.org/#/schemas/OMM) (although this will be less trivial to deal with : *TODO*)
- contributed scripts, see https://stellarium.org/scripts.html. These are very likely to change over time...

Some random googling shows that this problem exists in other projects too (e.g. Celestia):

- star catalogs are being corrected after publication (even if they are unlikely to be updated from within Stellarium, so an update might be no more than a basic copy-paste...):
	- [Gaia DR3](stars/hip_gaia3/) (see the [release notes](https://www.cosmos.esa.int/web/gaia-users/archive/release-notes), look for "VERSION 3.2.1 [2023-02-07]")
	- JWST Star Catalog ([documentation](https://jwst-docs.stsci.edu/jwst-observatory-characteristics/jwst-pointing-performance/jwst-guide-stars/jwst-guide-star-catalog-updates))
- [Celestia](http://celestia.simulatorlabbs.com/CelSL/src/celephem/)
- QtQui contains (sic) copied `parts from [zlib](src/external/zlib) (which is also copied into Stellarium...)
- https://github.com/Bill-Gray/jpl_eph/blob/master/jpleph.h
- [Stanford JSOC](http://jsoc.stanford.edu/cvs/JSOC/proj/timed/apps/Attic/jpleph.c?hidecvsroot=1&search=None&hideattic=1&sortby=rev&logsort=date&rev=1.1&content-type=text%2Fvnd.viewcvs-markup&diff_format=h)
- https://apollo.astro.amu.edu.pl/PAD/pmwiki.php?n=Dybol.JPLEph:  
**do notice the phrase** *"According to JPL fortran asc2eph.f (lines 101-102 and 197-198) I added new lines handling RPT and TPT arrays. "*. This is the typical meta issue that vendor branching tries to solve.
- more SGP4 forks
	- https://www.projectpluto.com/sat_code.htm
	- https://pypi.org/project/sgp4/ (unconfirmed...)
- the KIK case demonstrates what happens when one doesn't vendor: 
	- https://www.theregister.com/2016/03/23/npm_left_pad_chaos/
	- https://qz.com/646467/how-one-programmer-broke-the-internet-by-deleting-a-tiny-piece-of-code
	- https://arstechnica.com/information-technology/2016/03/rage-quit-coder-unpublished-17-lines-of-javascript-and-broke-the-internet/
	- https://www.activestate.com/blog/pythons-atomicwrites-and-software-dependency-availability-issues/

Although some examples above are unlikely to ever change - or be very ephemeral (sic) - the reasoning is always: prevent rather than cure, and exercise a lot, until it becomes second nature. Just keep Murphy's Law in mind...

As it is obvious that the problem is widespread, it feels unlikely that many users will change their minds... So this whole discussion is mainly oriented to those who are still fresh in the discipline...

### The problem

Notice how it is not always obvious to trace back the original files. In the case of ephemeride routines, these reside in "ancient", core Stellarium files, it is extremely likely that they were copied (and *maybe* recent changes have been manually  and painfully incorporated in Stellarium). One aspect of the recommended vendor branch procedure details how to include such *meta information* so as to help find back the (original, root) source at all times.

The external (source) version of such artifacts will often continue to evolve, but these modifications obviously will not be magically reflected in the project repository, thus *sometimes, if not often* leading to artifacts slowly getting totally outdated (hence the term "[code rot](https://en.wikipedia.org/wiki/Software_rot)").

Importing external artifacts therefore requires a specific (and in this case a *simple* - believe me, it is not rocket science - as well as generic) approach: the **Vendor Branch** approach. Other approaches exist, such as subtrees (but this is not part of core Git) and submodules (in case the external artifacts are versioned under Git, BUT submodules do not provide the flexibility of vendor branching), but have inconveniences and are not discussed here; the proposed Vendor Branch approach is KISS: *simple to apply to novice programmers*. By the way, the approach is valid in any VCS, such as SVN (where it seems to have emerged), Git, Mercurial, ClearCase, TFS, cvs, you name it.

Importing external artefacts in vendor branches will also provide insight in what changed in those artefacts, just by inspecting the "diff" between successive vendor versions. Normally such changes should also be announced by the vendor.

## The solution

1. Keep external information alive (and updated) on a **separate** branch, called a "**vendor branch**" . Every copied dataset/tool/sourcecode lives unmodified in its own vendor branch (and possibly in its own (sub)directory; a subdirectory will always be needed in order to separate vendor artefacts from your project's). A vendor branch tracks a *pristine* copy/mirror of the external data.
1. Ideally, the external information is stored in a separate directory (e.g. ``external/<vendor>/<toolname>``). If all the vendor publishes is a single file, then it will have to live in some subdirectory.
1. **vendor tags** describe which version of the vendor artifacts has been imported (e.g. ``vendor/geonames/2021-08-21``; do use the ISO date/time format; if possible, prefef the vendor's tag info.)
1. The vendor branch is merged to wherever it is needed (normally a feature branch, which will eventually be merged to ``master``)
1. A ``VENDOR`` file - which is added in our local version of the vendor data - explains where the external/original information can be found, so that it can be updated when necessary.
1. If needed (which is often the case), external information is modified *locally* (usually via a feature/master branch, but *never* in its vendor branch)
1. Ideally, issues in the vendor artifacts should be reported to the vendor, so that updates can then be imported back via a fresh *vendor drop*. Alternatively, a developer can solve issues locally, but *never* in the vendor branch. Alternatively, a fix branch can be created from the vendor branch and a patch transmited to the vendor as well as merged locally.

Sometimes, conversion routines need to be written or updated so that external data fits with the project. These routines do not belong in the vendor branch, but in the project itself. Remember that every vendor drop starts with an emptied vendor directory.

## Notes

### patching

In some circumstances you want to also contribute to the vendor's project.
Even if you vendored into a Git repo, even if the vendor uses a Git repo, you cannot simply create a pull request.
This is because your vendor drop contains totally different SHA-1 commits, so Git wouldn't know how to create a patch.
NOTE: `git bundle` might be a possibility to import the SHA-1 too.

There are a few ways to handle this situation.

#### create a patch file with `diff`

If your changes don't contain binary files, run a diff and send that to the vendor.
Remember to generate a diff relative to the vendor directory.

```
git diff --relative=<vendor path>  <branch base>..<branch head>
```

It might be good to review the generated text file, you never know... For example, to detect if the patch did touch binary files.

The vendor will apply your patch (probably via a branch) using `git apply` or the classical `patch` program

```
git apply <patchfile>
# alternative for non-Git repos
patch -p1 < patchfile
```

#### how to deal with binaries

If your patch adds/changes binary files, then supply those separately.

TO CONFIRM: edit the patch file, remove the references to binaries(?), and mention this to the vendor.

#### creating a patch using `git archive`

The easiest way (also to avoid the binaries issue) is to send an entire archive *of the vendor directory* of your branch.
The vendor will then ingest that in a branch (actually they are doing a kind of vendor drop...) and run their diff/merge/etc.

```
git archive --format=tgz --output=<tarfile>.tgz <head>:<path to vendor directory> [path]
```

This creates a tgz file (run `git archive --list` for the formats) of the commit `<head>` relative to the vendor directory dirname.

Note that this even works for a single vendor file, should you have chosen not to use a directory for the vendor artefact.

### how to vendor drop a remote git repo

Sometimes, it might be desirable to convert a Git repo to an archive in order to perform the vendor drop.

### what about `git submodules` (complex, delicate) and `git subtree` (requires a remote git repo)?

These are partial solutions offered by Git but do not provide the flexibility of vendor branching.
To expand further.

### what if external data is not available as text files

Sometimes, artefacts are not available as ready to ingest source code. But as a PDF that contains (parts of) source code. Or a binary formatted file.

Such artefacts cannot magically be turned into source code.

The idea is to store the artefact (PDF, binary file, ...) in a separate folder in the vendor branch, then painfully (yes...) extract the code into another separate folder in the vendor branch. And/or ask the author to provide a git repo, a file, archive, ...

If there is no tarball to explode, do not empty the vendor directory, but manually update what changed. Often this can be accomplished via scripts. (??)

And then only merge to main/master/...

### dealing with coding style/conventions

When modifying vendor code, stick to the vendor coding style/conventions. Rewriting for readbility etc. will likely lead to massive conflicts at the next vendor drop.

### dealing with trailing whitespace

*TODO: add directives how to deal with external artefacts originating from other platform environments.
This is not directly related to vendor branching.*

Git tips (TO CONFIRM):

- check your current global/local/worktree whitespace handling
```
	git config --get-all --show-origin core.whitespace
	git config --global core.whitespace trailing-space,-space-before-tab,indent-with-non-tab,cr-at-eol
```
- enable your repo's pre-commit hook (it checks for various whitespace issues. See also ``git help hooks``

### ...and platform end of line issues

*TODO: replace with ``.gitattributes`` ?*

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
Sometimes a format is accompanied by a metadata section describing the format of the data. This metadata is an important artefact to commit to an vendor branch. *Changes to the schema will be readily identified as diffs in the vendor branch. That's why such files must be ingested too.*

### When conflicts are no longer manageable

In some cases, merging vendor updates may become too difficult if not impossible. Welcome to merge hell? Nevertheless, vendor drops will continue to provide the means to port changes, by allowing the developer to study at least what changed in the vendor branch, and apply those changes ... manually.

``git rerere`` might become helpful.

### Importing vendor code written in other languages

If the artifact is not usable without extensive rewriting (e.g. Fortran code in a C++ project), it might still make sense to vendor the original file and keep it as a neutral (uncompiled) text file that will serve as an excellent reference.

This also applies for cases where explanatory/example (pseudo) sourcecode is offered; this code is essential documentation that the vendor might update occasionally.

A typical example is the set of [JPL DExxx development ephemerides](https://ssd.jpl.nasa.gov/planets/eph_export.html), that are accompanied by important documentation *that is to be stored in the vendor branch too*:

- https://ssd.jpl.nasa.gov/ftp/eph/planets/ascii/ascii_format.txt
- https://ssd.jpl.nasa.gov/ftp/eph/planets/fortran/ (complete!) (includes https://ssd.jpl.nasa.gov/ftp/eph/planets/fortran/userguide.txt)
- https://ssd.jpl.nasa.gov/ftp/eph/planets/other_readers.txt

Should any of those "other readers" be used in any way in Stellarium, then these belong in separate vendor branches.

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

### How to deal with module files that are updated externally and still not vendored internally

All hope is not lost! The basic idea is to create a vendor branch with the new artifact, and do some manual "undo-redo" work in the task branch .

### Version information in vendor file/directory paths

Sometimes, developers add directories/files with path names containing version information. An example is the FAQ file of [this landscape](http://www.alienbasecamp.com/Stellarium/sun.htm).

This is a bad practice, usually done by developers that do not have access to a good VCS. (Note also the CR/LF issue.)

In such cases, the version information should be removed before committing the vendor drop; this will present the additional advantage that the history of such a file becomes available. This is a delicate step, as the "pristine copy" requirement is no longer fulfilled. If filename information is part of the correct functioning of the imported artifacts (e.g. it is also referenced in vendor scripts, in linked data, etc), then you are facing a difficult problem. In such a case (for now), it might be better to not rename the vendor file paths at all and accept that file history must be discovered by other means (e.g. a manual diff). *TODO find a better way here.*

### Using config data from other users

The vendor branch approach also works for users that want to keep track of other user's configuration data (e.g. Ocular config) or scripts while at the same time apply local changes. This works better for file formats that are easily merged because being insensitive to line numbers, such as YAML or - even better, but neither are supported by Qt - KVN; a bad example is the (Qt backed) INI numbering format (e.g. [Ocular config files](https://github.com/Stellarium/stellarium/blob/ba80d33d4bc83d72fc15cca53f798cd9439482cf/plugins/Oculars/resources/default_ocular.ini)). An improvement is to use [Qt XML](https://doc.qt.io/qt-6/qtxml-index.html). See also https://www.surfsidemedia.in/post/what-are-some-alternatives-to-ini-files-for-configuration-management

## See also

### vendor branching concept
- https://stackoverflow.com/questions/tagged/vendor-branch?sort=votes
- https://stackoverflow.com/questions/769786/vendor-branches-in-git
- https://en.wikipedia.org/wiki/Branching_%28version_control%29#Motivations_for_branching
- https://blog.bigsmoke.us/2009/07/20/svn-vendor-branches
- https://portal.perforce.com/s/article/3374
- https://stackoverflow.com/questions/1710027/arguments-for-and-against-including-3rd-party-libraries-in-version-control/1710050

## external discussions
- https://github.com/cpm-cmake/CPM.cmake/discussions/720
- https://github.com/CelesTrak/fundamentals-of-astrodynamics/discussions/173

### Stellarium
- https://github.com/Stellarium/stellarium/discussions/1856
- https://github.com/Stellarium/stellarium/pull/1906
- https://github.com/axd1967/stellarium/blob/contrib/docs/vendor-branching/VENDOR_BRANCHING.md (this file)
- https://github.com/Stellarium/stellarium/wiki/Branching-Strategy (defunct but a copy exists)

### Copy-pasta
- https://en.wikipedia.org/wiki/Software_rot
- https://en.wikipedia.org/wiki/Copypasta#Technology
- "*[copy-paste is evil](https://stackoverflow.com/questions/2490884/why-is-copy-and-paste-of-code-dangerous)*"
- https://www.cisa.gov/resources-tools/resources/product-security-bad-practices: _"Cache copies of all open-source dependencies within the manufacturer’s own build systems and do not update products or customer systems directly from unverified public sources."_ (Dead link, track https://github.com/cisagov/bad-practices/discussions/101)

### Git
- https://github.com/git/git/blob/master/Documentation/technical/unit-tests.adoc
- how to correctly vendor drop: https://github.com/git/git/blob/master/Documentation/git-rm.adoc#using-git-add--a
- `git subtree`:
	- https://apenwarr.ca/log/20090430-a-new-alternative-to-git-submodules-git-subtree
	- https://github.com/git/git/blob/master/contrib/subtree/git-subtree.adoc
	- https://david.rothlis.net/vendor-branch/
	- https://www.atlassian.com/git/tutorials/git-subtree
- `git submodule`:
	- https://github.com/git/git/blob/master/Documentation/user-manual.adoc#submodules

### to be evaluated:
- if you read this far, we need to ingest this: https://talesfromthearmchair.net/a-rebasing-vendor-branch-workflow-for.html
- https://github.com/brettlangdon/git-vendor (https://medium.com/opsops/git-vendor-295db4bcec3a)
- https://github.com/thejoshwolfe/git-vendor

Think vendor branching is difficult? Eat [this](https://www.refontelearning.com/blog/tle-to-omm-six-digit-catalog-migration)!

