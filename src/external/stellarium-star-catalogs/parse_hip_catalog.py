#!/usr/bin/env python3
r"""Resumable, script version of Parse_HIP_Catalog.ipynb (both cells).

Turns the raw SIMBAD dumps (simbad_query_results/*_combined.dat) into:
  - hip_processed_with_binary.dat   (HIP main table, binaries split into components)
  - cross-id.cat                    (21-byte binary cross-identification catalog)

Robustness:
  - All network calls are retried with backoff (5s/20s/60s, 4 attempts).
  - Every network result is cached on disk (Gaia DR2->DR3 lookup CSV,
    SIMBAD hierarchy cache, Gaia cone-search cache), so re-runs skip
    completed work automatically.
  - Two dataframe checkpoints (pickle) bracket the network-heavy stages:
        ckpt_s1_binary.pkl  - after binary-system resolution
        ckpt_s2_cone.pkl    - after the remaining cone-search pass
    Delete them to force re-running the corresponding stage.
  - The notebook's per-star time.sleep(1.0) is removed; the cone-search
    pass runs on a small thread pool instead (3 workers, per-thread Gaia
    session).

Run from the repository root (same working directory as the notebook):
    venv\Scripts\python parse_hip_catalog.py
"""

import hashlib
import pathlib
import re
import struct
import threading
import time
import warnings
from concurrent.futures import ThreadPoolExecutor

import astropy.units as u
import pandas as pd
import tqdm
from astropy.coordinates.name_resolve import NameResolveError
from astropy.table import Table
from astroquery.gaia import Gaia, GaiaClass

from py.utils import custom_simbad

# ---------------------------------------------------------------- paths / config
base_path = pathlib.Path("simbad_query_results")
hip_combined_path = base_path / "hip_combined.dat"
sao_combined_path = base_path / "sao_combined.dat"
hd_combined_path = base_path / "hd_combined.dat"
hr_combined_path = base_path / "hr_combined.dat"
gaia_id_path = base_path / "gaia_source_id_lookup.csv"
simbad_heriarchy_cache = base_path / "heriarchy_cache"
cone_cache_dir = base_path / "cone_cache"
ckpt_s1_path = base_path / "ckpt_s1_binary.pkl"
ckpt_s2_path = base_path / "ckpt_s2_cone.pkl"

CONE_WORKERS = 3          # parallel cone searches (Gaia archive friendly)
LOOKUP_SAVE_EVERY = 25    # persist DR2->DR3 lookup csv every N new entries

for p in [hip_combined_path, sao_combined_path, hd_combined_path, hr_combined_path]:
    if not p.exists():
        raise FileNotFoundError(f"{p} does not exist. Run simbad_query_hipsaohdhr.py first.")
simbad_heriarchy_cache.mkdir(parents=True, exist_ok=True)
cone_cache_dir.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------- retry helper
def retry_call(fn, desc, attempts=4, no_retry=(NameResolveError, IndexError)):
    """Call fn() with exponential backoff on transient exceptions.

    Exception types in no_retry are deterministic failures (bad name, missing
    row) where waiting cannot help; they are re-raised immediately.
    """
    waits = [5, 20, 60]
    for attempt in range(1, attempts + 1):
        try:
            return fn()
        except no_retry:
            raise
        except Exception as e:
            if attempt == attempts:
                print(f"  [FAIL] {desc}: {type(e).__name__}: {str(e)[:120]} (giving up)")
                raise
            print(f"  [retry {attempt}/{attempts-1}] {desc}: {type(e).__name__}: {str(e)[:100]} - wait {waits[attempt-1]}s", flush=True)
            time.sleep(waits[attempt - 1])


# ---------------------------------------------------------------- regex & globals
re_gaiadr2 = re.compile(r"Gaia DR2\s+(\d+)")
re_gaiadr3 = re.compile(r"Gaia DR3\s+(\d+)")
re_hip = re.compile(r"HIP\s+(\d+)")
re_sao = re.compile(r"SAO\s+(\d+)")
re_hd = re.compile(r"HD\s+(\d+)")
re_hr = re.compile(r"HR\s+(\d+)")

# DR2 -> DR3 lookup cache (persisted to CSV, appended periodically)
try:
    gaia_id_df = pd.read_csv(gaia_id_path, dtype="Int64")
except FileNotFoundError:
    gaia_id_df = pd.DataFrame(columns=["dr2_sourceid", "dr3_sourceid"], dtype="Int64")
    gaia_id_df.to_csv(gaia_id_path, index=False)
_lookup_dirty = 0

# per-thread Gaia session (the shared astroquery session is not thread-safe)
_tls = threading.local()
_lookup_lock = threading.Lock()


def thread_gaia():
    if not hasattr(_tls, "gaia"):
        _tls.gaia = GaiaClass()
    return _tls.gaia


def save_lookup(force=False):
    global _lookup_dirty
    if force or _lookup_dirty >= LOOKUP_SAVE_EVERY:
        gaia_id_df.to_csv(gaia_id_path, index=False)
        _lookup_dirty = 0


def cone_search_cached(query_text):
    """Gaia cone search (7.5") with disk cache. Returns source_id or pd.NA."""
    key = hashlib.sha1(query_text.encode("utf-8")).hexdigest()
    cache_file = cone_cache_dir / f"{key}.txt"
    if cache_file.exists():
        val = cache_file.read_text().strip()
        return int(val) if val else pd.NA

    def do_query():
        return thread_gaia().cone_search(query_text, radius=7.5 * u.arcsecond).results

    try:
        res = retry_call(do_query, f"cone_search {query_text}")
    except NameResolveError:
        res = None
    except Exception:
        res = None  # after retries exhausted: treat as not found, keep going
    sid = ""
    if res is not None and len(res) > 0:
        sid = str(int(res[0]["source_id"]))
    tmp = cache_file.with_suffix(".tmp")
    tmp.write_text(sid)
    tmp.replace(cache_file)
    return int(sid) if sid else pd.NA


def extract_gaia_number_prov(text, strict=False, cone_search=False):
    """Same resolution as the notebook, but also returns the method used.

    Returns (sid_or_pd.NA, method_or_None) where method is one of:
      'dr3_direct'    - SIMBAD's ids contained "Gaia DR3 X"
      'dr2_to_dr3'    - ids contained "Gaia DR2 X", resolved to DR3 via archive
      'cone_search'   - resolved by 7.5" Gaia cone search by name
      None            - not resolved (NA/empty input, or strict/lookup both failed)
    """
    global gaia_id_df, _lookup_dirty

    if pd.isna(text) or text == "":
        return pd.NA, None

    match = re_gaiadr3.search(text)
    if match:
        return int(match.group(1)), "dr3_direct"
    if strict and not cone_search:
        return pd.NA, None

    if not cone_search and (match := re_gaiadr2.search(text)):
        dr2_id = int(match.group(1))
        with _lookup_lock:
            in_lookup_row = gaia_id_df[gaia_id_df["dr2_sourceid"] == dr2_id]
        if len(in_lookup_row) > 0:
            return int(in_lookup_row["dr3_sourceid"].values[0]), "dr2_to_dr3"
        # is dr2 == dr3?
        res = retry_call(
            lambda: thread_gaia().launch_job(
                f"SELECT source_id FROM gaiadr3.gaia_source WHERE source_id={dr2_id}"
            ).results,
            f"dr2==dr3 check {dr2_id}")
        if len(res) > 0:
            with _lookup_lock:
                gaia_id_df = pd.concat([gaia_id_df, pd.DataFrame(
                    {"dr2_sourceid": [dr2_id], "dr3_sourceid": [dr2_id]})], ignore_index=True)
                _lookup_dirty += 1
                save_lookup()
            return dr2_id, "dr2_to_dr3"
        # cone search the DR2 position propagated to J2016.0
        def fetch_dr2_row():
            t = thread_gaia().launch_job(
                f"SELECT designation, source_id, ra, dec, parallax, pmra, pmdec, phot_g_mean_mag, bp_rp, radial_velocity "
                f"FROM gaiadr2.gaia_source WHERE source_id={dr2_id}"
            ).results.filled(0)
            return t[0] if len(t) > 0 else None

        gaia_dr2 = retry_call(fetch_dr2_row, f"dr2 row {dr2_id}")
        if gaia_dr2 is None:
            print(f"  Gaia DR2 {dr2_id} not found in DR2")
            return pd.NA, None
        query = rf"""SELECT TOP 10 designation, source_id, ra, dec,
DISTANCE(POINT('ICRS' , gaiadr3.gaia_source.ra, gaiadr3.gaia_source.dec),
POINT('ICRS',
COORD1(EPOCH_PROP_POS({gaia_dr2["ra"]}, {gaia_dr2["dec"]}, {gaia_dr2["parallax"]}, {gaia_dr2["pmra"]}, {gaia_dr2["pmdec"]}, {gaia_dr2["radial_velocity"]}, 2015.5, 2016.0)),
COORD2(EPOCH_PROP_POS({gaia_dr2["ra"]}, {gaia_dr2["dec"]}, {gaia_dr2["parallax"]}, {gaia_dr2["pmra"]}, {gaia_dr2["pmdec"]}, {gaia_dr2["radial_velocity"]}, 2015.5, 2016.0)))) AS "target_separation (deg)"
FROM gaiadr3.gaia_source
WHERE CONTAINS(
	POINT('ICRS',gaiadr3.gaia_source.ra,gaiadr3.gaia_source.dec),
	CIRCLE(
		'ICRS',
		COORD1(EPOCH_PROP_POS({gaia_dr2["ra"]}, {gaia_dr2["dec"]}, {gaia_dr2["parallax"]}, {gaia_dr2["pmra"]}, {gaia_dr2["pmdec"]}, {gaia_dr2["radial_velocity"]}, 2015.5, 2016.0)),
		COORD2(EPOCH_PROP_POS({gaia_dr2["ra"]}, {gaia_dr2["dec"]}, {gaia_dr2["parallax"]}, {gaia_dr2["pmra"]}, {gaia_dr2["pmdec"]}, {gaia_dr2["radial_velocity"]}, 2015.5, 2016.0)),
		{(15 * u.arcsecond).to(u.deg).value})
)=1 ORDER BY "target_separation (deg)"
"""
        tmp = retry_call(lambda: thread_gaia().launch_job(query).results, f"dr2->dr3 cone {dr2_id}")
        if len(tmp) == 0:
            print(f"  Gaia DR2 {dr2_id} not found in DR3")
            return pd.NA, None
        dr3_id = int(tmp[0]["source_id"])
        with _lookup_lock:
            gaia_id_df = pd.concat([gaia_id_df, pd.DataFrame(
                {"dr2_sourceid": [dr2_id], "dr3_sourceid": [dr3_id]})], ignore_index=True)
            _lookup_dirty += 1
            save_lookup()
        return dr3_id, "dr2_to_dr3"
    else:
        if cone_search and text:
            parts = text.split("|")
            query_text = parts[1] if len(parts) > 1 else parts[0]
            return cone_search_cached(query_text), "cone_search"
        return pd.NA, None


def extract_gaia_number(text, strict=False, cone_search=False):
    """Backward-compatible wrapper returning only the sid."""
    return extract_gaia_number_prov(text, strict=strict, cone_search=cone_search)[0]


# ---------------------------------------------------------------- stage 1: binary resolution
def stage1_resolve_binaries(simbad_table):
    simbad_table["otype"] = simbad_table["otype"].fillna("")
    simbad_table = simbad_table[simbad_table["otype"].apply(lambda x: "err" not in x)]
    # _prov tracks how each row's source_id was resolved. Default empty here;
    # filled by parse_cross_id (for SIMBAD-native parents) or by this stage
    # (for hierarchy children) or by stage2_cone_pass (for cone-search resolves).
    simbad_table["_prov"] = ""

    source_id = simbad_table["ids"].apply(lambda x: extract_gaia_number(x, strict=True))
    hip_wo_source_id_idx = (
        pd.isna(source_id)
        & (simbad_table["V"].fillna(99.99) > 3.0)
        & (simbad_table["J"].fillna(99.99) > 2.0)
        & ~pd.isna(simbad_table["ids"])
    )
    simbad_table_temp = simbad_table[hip_wo_source_id_idx]
    print(f"  {len(simbad_table_temp)} suspect rows without Gaia id (V>3 or J>2)")
    result = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for i, irow in tqdm.tqdm(simbad_table_temp.iterrows(),
                                 total=len(simbad_table_temp),
                                 desc="Resolving potential binary"):
            parent_sao = re_sao.search(irow["ids"])
            parent_hd = re_hd.search(irow["ids"])
            parent_hr = re_hr.search(irow["ids"])

            tmp_query = custom_simbad.query_hierarchy(
                irow["main_id"], hierarchy="children",
                get_query_payload=True, detailed_hierarchy=False)["QUERY"]
            tmp_hash = hashlib.sha1(tmp_query.encode("utf-8")).hexdigest()
            tmp_file = simbad_heriarchy_cache / f"{tmp_hash}.dat"
            if tmp_file.exists():
                temp = pd.read_csv(tmp_file)
            else:
                temp = retry_call(
                    lambda: custom_simbad.query_hierarchy(
                        irow["main_id"], hierarchy="children", detailed_hierarchy=False),
                    f"hierarchy {irow['main_id']}")
                temp = temp.to_pandas()
                temp["user_specified_id"] = irow["user_specified_id"].strip()
                child_results = temp["ids"].apply(
                    lambda x: extract_gaia_number_prov(x, cone_search=True))
                child_sid = [r[0] for r in child_results]
                child_method = [r[1] for r in child_results]
                for idx, row in temp.iterrows():
                    temp.loc[idx, "user_specified_id"] = f"{row['user_specified_id']}{chr(65 + idx)}"
                    temp.loc[idx, "ids"] = f"{temp.loc[idx, 'user_specified_id']}|{temp.loc[idx, 'ids']}"
                    if not pd.isna(child_sid[idx]):
                        temp.loc[idx, "ids"] = f"{temp.loc[idx, 'ids']}|Gaia DR3 {child_sid[idx]}"
                # persist child_method on the cached frame so cached re-runs see it
                temp["_child_method"] = child_method
                temp.to_csv(tmp_file, index=False)
            # source_id on temp's ids (post-append): this determines the sid we keep.
            # _child_method records how that sid was resolved (dr3_direct / dr2_to_dr3 / cone_search),
            # or None if the child had no sid (we'll mark such children unresolved below).
            if "_child_method" not in temp.columns:
                # cached file from a pre-provenance run: re-derive method per child.
                temp["_child_method"] = temp["ids"].apply(
                    lambda x: extract_gaia_number_prov(x)[1])
            source_id = temp["ids"].apply(lambda x: extract_gaia_number(x))
            if len(temp) <= 1:
                continue
            if pd.isna(source_id[1:]).any() or source_id.duplicated(keep=False).any():
                continue
            temp["ids"] = temp["ids"].apply(
                lambda x: f"{x}|SAO {parent_sao.group(1)}" if parent_sao else x)
            temp["ids"] = temp["ids"].apply(
                lambda x: f"{x}|HD {parent_hd.group(1)}" if parent_hd else x)
            temp["ids"] = temp["ids"].apply(
                lambda x: f"{x}|HR {parent_hr.group(1)}" if parent_hr else x)
            # row-level provenance: hierarchy_child_<method>, or hierarchy_child_unresolved
            temp["_prov"] = temp["_child_method"].apply(
                lambda m: f"hierarchy_child_{m}" if m else "hierarchy_child_unresolved")
            result.append(temp)
            simbad_table.drop(i, inplace=True)
    print(f"  resolved {len(result)} binary systems into components")
    if len(result) > 0:
        simbad_table = pd.concat([simbad_table, *result])
    simbad_table = simbad_table.dropna(how="all")
    simbad_table.reset_index(drop=True, inplace=True)
    return simbad_table


# ---------------------------------------------------------------- stage 2: remaining cone searches
def stage2_cone_pass(simbad_table):
    source_id = simbad_table["ids"].apply(lambda x: extract_gaia_number(x, strict=True))
    wo_source_id_idx = (
        pd.isna(source_id)
        & (simbad_table["V"].fillna(99.99) > 3.0)
        & ~pd.isna(simbad_table["ids"])
    )
    todo = simbad_table[wo_source_id_idx]
    print(f"  {len(todo)} rows still without Gaia id, cone searching ({CONE_WORKERS} workers)")
    if len(todo) == 0:
        return simbad_table

    keys = list(todo.index)
    texts = [todo.loc[idx, "ids"] for idx in keys]

    def resolve(text):
        try:
            return extract_gaia_number_prov(text, cone_search=True)
        except Exception:
            return (pd.NA, None)

    with ThreadPoolExecutor(max_workers=CONE_WORKERS) as ex:
        results = list(tqdm.tqdm(ex.map(resolve, texts), total=len(texts),
                                 desc="Resolving Gaia DR3 ID xmatch"))
    n_hit = 0
    for idx, (sid, method) in zip(keys, results):
        if not pd.isna(sid):
            simbad_table.loc[idx, "ids"] = f"{simbad_table.loc[idx, 'ids']}|Gaia DR3 {sid}"
            # Only overwrite _prov if it was empty (don't clobber hierarchy_child_*)
            cur = simbad_table.loc[idx, "_prov"]
            if cur == "" or cur is None:
                simbad_table.loc[idx, "_prov"] = method if method else "unresolved"
            n_hit += 1
    print(f"  cone search resolved {n_hit}/{len(todo)}")
    return simbad_table


# ---------------------------------------------------------------- cross-id parsing
def parse_cross_id(result):
    def extract_id(text, sid, group_id=1):
        if not pd.isna(text):
            if isinstance(sid, str):
                match = re.search(rf"{sid}\s+(\d+)([A-Z]?)", text)
            elif isinstance(sid, re.Pattern):
                match = sid.search(text)
            else:
                raise ValueError("sid must be either str or re.Pattern")
            if match and match.group(group_id) != "":
                return match.group(group_id).strip()
        return pd.NA

    def parse_component(text):
        if pd.isna(text) or text == "" or text == 0:
            return pd.NA
        return text

    df = pd.DataFrame(columns=["hip", "gaia_dr3", "component", "sao", "hd", "hr"], dtype="Int64")
    df["component"] = df["component"].astype(pd.StringDtype())
    hip, sao, hd, hr = [
        result["ids"].apply(lambda x: extract_id(x, sid)).astype("Int64")
        for sid in [re_hip, re_sao, re_hd, re_hr]
    ]
    # Gaia ids: fast local DR3-regex pass first; rows that only have a DR2 id
    # need online DR2->DR3 resolution -- collect and run them in parallel.
    ids_texts = result["ids"]
    gaia = ids_texts.apply(lambda x: extract_gaia_number(x, strict=True))
    need_dr2 = gaia.isna() & ids_texts.apply(
        lambda x: (not pd.isna(x)) and bool(re_gaiadr2.search(x)))
    n_dr2 = int(need_dr2.sum())
    if n_dr2 > 0:
        print(f"  {n_dr2} rows have only a Gaia DR2 id - resolving online ({CONE_WORKERS} workers, cached)", flush=True)
        dr2_texts = list(ids_texts[need_dr2])
        def safe_resolve(text):
            try:
                return extract_gaia_number(text)
            except Exception:
                return pd.NA
        with ThreadPoolExecutor(max_workers=CONE_WORKERS) as ex:
            resolved = list(tqdm.tqdm(ex.map(safe_resolve, dr2_texts),
                                      total=n_dr2, desc="DR2->DR3 lookups"))
        gaia.loc[need_dr2] = resolved
        save_lookup(force=True)
    component = (
        result["ids"]
        .apply(lambda x: parse_component(extract_id(x, "HIP", group_id=2)))
        .astype(pd.StringDtype())
    )
    df["hip"] = hip
    df["sao"] = sao
    df["hd"] = hd
    df["hr"] = hr
    df["gaia_dr3"] = gaia.astype("Int64")
    df["component"] = component

    # provenance: stage1/stage2 already set _prov on the simbad table for rows
    # they resolved (hierarchy_child_*, dr3_direct / dr2_to_dr3 / cone_search).
    # Rows with empty _prov are SIMBAD-native (DR3 from original ids) or
    # resolved by the need_dr2 pass here, or unresolved.
    prov = result["_prov"].values.copy() if "_prov" in result.columns else [""] * len(result)
    for i in range(len(result)):
        if prov[i] and prov[i] != "":
            continue
        sid = gaia.iloc[i]
        if pd.isna(sid) or sid == 0:
            prov[i] = "unresolved"
        elif need_dr2.iloc[i]:
            prov[i] = "dr2_to_dr3"
        else:
            prov[i] = "dr3_direct"
    df["prov"] = prov
    return df


# ---------------------------------------------------------------- main flow
def main():
    print("=== Stage 0: load tables ===", flush=True)
    hip_combined_table = Table.read(hip_combined_path, format="ascii")
    sao_combined_table = Table.read(sao_combined_path, format="ascii")
    hd_combined_table = Table.read(hd_combined_path, format="ascii")
    # hr_combined_table is loaded by the notebook but never actually used

    # remove the known bad HIP stars (positional 1-based row indices)
    hip_to_remove = [1902, 24647, 29116, 35194, 54948, 88759, 91906, 98623]
    hip_combined_table.remove_rows([i - 1 for i in hip_to_remove])

    # ---------------- Stage 1: binary resolution (network-heavy)
    if ckpt_s1_path.exists():
        print(f"=== Stage 1: binary resolution - SKIPPED (checkpoint {ckpt_s1_path.name}) ===", flush=True)
        simbad_table = pd.read_pickle(ckpt_s1_path)
    else:
        print("=== Stage 1: binary resolution ===", flush=True)
        simbad_table = stage1_resolve_binaries(hip_combined_table.to_pandas())
        simbad_table.to_pickle(ckpt_s1_path)
        save_lookup(force=True)
        print(f"  checkpoint saved: {ckpt_s1_path.name}", flush=True)

    # ---------------- Stage 2: remaining cone searches (network-heavy)
    if ckpt_s2_path.exists():
        print(f"=== Stage 2: cone-search pass - SKIPPED (checkpoint {ckpt_s2_path.name}) ===", flush=True)
        simbad_table = pd.read_pickle(ckpt_s2_path)
    else:
        print("=== Stage 2: cone-search pass ===", flush=True)
        simbad_table = stage2_cone_pass(simbad_table)
        simbad_table.to_pickle(ckpt_s2_path)
        save_lookup(force=True)
        print(f"  checkpoint saved: {ckpt_s2_path.name}", flush=True)

    # ---------------- Stage 3: Sirius + write hip_processed_with_binary.dat
    print("=== Stage 3: Sirius fix, write hip_processed_with_binary.dat ===", flush=True)
    hip_with_binary = simbad_table
    # deal with Sirius A and Sirius B, because SIMBAD said Sirius does not have children
    hip_with_binary.loc[hip_with_binary["main_id"] == "* alf CMa", "ids"] = (
        "HIP 32349A|"
        + hip_with_binary.loc[hip_with_binary["main_id"] == "* alf CMa", "ids"]
    )
    result = retry_call(lambda: custom_simbad.query_object("Sirius B"), "query Sirius B")
    result["ids"] = "HIP 32349B|" + result["ids"]
    simbad_table = pd.concat([hip_with_binary, result.to_pandas()])
    # Sirius B source_id comes directly from SIMBAD's own ids (DR3 extracted by parse_cross_id)
    simbad_table.loc[simbad_table.index[-1], "_prov"] = "dr3_direct"
    simbad_table = simbad_table.dropna(subset=["ids"])

    cross_id_df = parse_cross_id(simbad_table)

    simbad_table_db = simbad_table.copy()
    simbad_table_db["hip"] = cross_id_df["hip"].fillna(0)
    simbad_table_db["source_id"] = cross_id_df["gaia_dr3"].fillna(0)
    simbad_table_db["source_id_provenance"] = cross_id_df["prov"].values
    simbad_table_db["componentid"] = cross_id_df["component"]
    simbad_table_db["componentid"] = simbad_table_db["componentid"].apply(
        lambda x: 0 if pd.isna(x) else ord(x) - 64)
    simbad_table_db.to_csv(base_path / "hip_processed_with_binary.dat", index=False)
    n_prov = simbad_table_db["source_id_provenance"].value_counts().to_dict()
    print(f"  wrote hip_processed_with_binary.dat ({len(simbad_table_db)} rows)", flush=True)
    for k, v in n_prov.items():
        print(f"    source_id_provenance[{k}] : {v}", flush=True)

    # ---------------- Stage 4: fill missing SAO / HD into cross-id table
    print("=== Stage 4: fill missing SAO/HD ===", flush=True)
    existing_sao_ids = set(cross_id_df["sao"].dropna().astype(int))
    all_sao_ids = set(range(1, len(sao_combined_table) + 1))
    missing_sao_idx = list(all_sao_ids - existing_sao_ids)
    missing_sao = sao_combined_table[[i - 1 for i in missing_sao_idx]]
    cross_id_df = pd.concat([cross_id_df, parse_cross_id(missing_sao.to_pandas())])
    print(f"  added {len(missing_sao_idx)} SAO-only rows", flush=True)

    existing_hd_ids = set(cross_id_df["hd"].dropna().astype(int))
    all_hd_ids = set(range(1, len(hd_combined_table) + 1))
    missing_hd_idx = list(all_hd_ids - existing_hd_ids)
    missing_hd = hd_combined_table[[i - 1 for i in missing_hd_idx]]
    cross_id_df = pd.concat([cross_id_df, parse_cross_id(missing_hd.to_pandas())])
    print(f"  added {len(missing_hd_idx)} HD-only rows", flush=True)
    save_lookup(force=True)

    # ---------------- Stage 5: write cross-id.cat (notebook cell 2)
    print("=== Stage 5: write cross-id.cat ===", flush=True)
    cross_id_df = cross_id_df.dropna(how="all")
    cross_id_df.to_csv(base_path / "cross_id_with_gaiaid.dat", index=False, sep="\t")
    cross_id_df.loc[pd.isna(cross_id_df["hip"]), "hip"] = cross_id_df.loc[
        pd.isna(cross_id_df["hip"]), "gaia_dr3"].values
    cross_id_df = cross_id_df.drop(columns=["gaia_dr3"])
    cross_id_df = cross_id_df[
        (~pd.isna(cross_id_df["sao"]) | ~pd.isna(cross_id_df["hd"]) | ~pd.isna(cross_id_df["hr"]))
        & ~pd.isna(cross_id_df["hip"])
    ]
    cross_id_df = cross_id_df.sort_values(["hip", "component"]).astype({"component": "object"})
    # prov column was already written to hip_processed_with_binary.dat; cross-id.cat is the old format
    if "prov" in cross_id_df.columns:
        cross_id_df = cross_id_df.drop(columns=["prov"])
    cross_id_df["component"] = cross_id_df["component"].apply(
        lambda x: 0 if pd.isna(x) else ord(x) - ord("A") + 1)
    cross_id_df.fillna(0, inplace=True)
    cross_id_df = cross_id_df.astype("Int64")
    record_size = 21
    bdata = bytearray(record_size * len(cross_id_df))
    # 21-byte record: Q=hip (or gaia id), B=component, i=sao, i=hd, i=hr
    for i, row in enumerate(cross_id_df.itertuples(index=False)):
        byte_data = struct.pack("=QBiii", row.hip, row.component, row.sao, row.hd, row.hr)
        bdata[i * record_size:(1 + i) * record_size] = byte_data
    with open(base_path / "cross-id.cat", "wb") as f:
        f.write(bdata)
    print(f"  wrote cross-id.cat ({len(cross_id_df)} records, {len(bdata)} bytes)", flush=True)

    print("\nAll done.", flush=True)


if __name__ == "__main__":
    main()
