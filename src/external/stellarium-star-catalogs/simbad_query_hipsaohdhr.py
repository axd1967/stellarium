import pathlib
import time

import tqdm
from astropy.table import Table, vstack

from py.utils import custom_simbad


def batch_ok(path):
    """Parse-level completeness check: exists, parses cleanly, has the expected 28 columns.

    Note: result.write() runs locally only after a successful network query, so a
    network failure can never leave a partially-written file. The only suspect is
    the newest existing batch, which the caller re-fetches unconditionally.
    """
    if not path.exists():
        return False
    try:
        t = Table.read(path, format="ascii")
    except Exception:
        return False
    return len(t.colnames) == 28


def query_with_retry(ids, batch_desc, attempts=3, wait=30):
    for attempt in range(1, attempts + 1):
        try:
            return custom_simbad.query_objects(ids)
        except Exception as e:
            if attempt == attempts:
                raise
            print(f"\n{batch_desc}: attempt {attempt} failed ({type(e).__name__}: {e}), retry in {wait}s")
            time.sleep(wait)

base_path = pathlib.Path("simbad_query_results")
base_path.mkdir(parents=True, exist_ok=True)
hip_subdir = base_path / "hip"
hip_subdir.mkdir(parents=True, exist_ok=True)
sao_subdir = base_path / "sao"
sao_subdir.mkdir(parents=True, exist_ok=True)
hd_subdir = base_path / "hd"
hd_subdir.mkdir(parents=True, exist_ok=True)
hr_subdir = base_path / "hr"
hr_subdir.mkdir(parents=True, exist_ok=True)
hip_combined_path = base_path / "hip_combined.dat"
sao_combined_path = base_path / "sao_combined.dat"
hd_combined_path = base_path / "hd_combined.dat"
hr_combined_path = base_path / "hr_combined.dat"
max_hip_id = 120416
max_sao_id = 258997
max_hd_id = 272150
max_hr_id = 9110
query_batch_size = 2000


for subdir, max_id, combined_path in zip(
    [hip_subdir, sao_subdir, hd_subdir, hr_subdir], [max_hip_id, max_sao_id, max_hd_id, max_hr_id], [hip_combined_path, sao_combined_path, hd_combined_path, hr_combined_path]):
    if combined_path.exists():  # if the combined file already exists, skip
        print(f"Skipping {subdir.name} as the combined file already exists. If you want to re-query, delete the combined file.")
        continue
    n_batches = max_id // query_batch_size + 1
    # Re-fetch the newest existing batch unconditionally: it is the only one that
    # could theoretically be incomplete (a crash between query and write).
    existing = [b for b in range(n_batches) if (subdir / f"simbad_{subdir.name}_{b}.dat").exists()]
    refetch = max(existing) if existing else -1
    if refetch >= 0:
        print(f"Resuming {subdir.name}: {len(existing)} batches found, re-fetching newest batch {refetch} for safety")
    for batch in tqdm.tqdm(range(n_batches), desc=f"Querying {subdir.name}"):
        batch_path = subdir / f"simbad_{subdir.name}_{str(batch)}.dat"
        if batch != refetch and batch_ok(batch_path):
            continue
        max_id_clipped = min(max_id, batch * query_batch_size + query_batch_size)
        ids = [f"{subdir.name.upper()} {str(i)}".strip() for i in range(1 + batch * query_batch_size, 1 + max_id_clipped)]
        result = query_with_retry(ids, f"{subdir.name} batch {batch}")
        result.write(batch_path, format="ascii", overwrite=True)
    # merge all the tables
    files_list = subdir.glob("simbad_*.dat")
    table_list = []
    counter = 0
    curr_path = subdir / f"simbad_{subdir.name}_{str(counter)}.dat"
    while curr_path.exists():  # need to loop through all the files in the exact order. can't use glob("*")
        table_list.append(Table.read(curr_path, format="ascii"))
        counter += 1
        curr_path = subdir / f"simbad_{subdir.name}_{str(counter)}.dat"
    simbad_table = vstack(table_list)
    simbad_table.write(combined_path, format="ascii", overwrite=True)
