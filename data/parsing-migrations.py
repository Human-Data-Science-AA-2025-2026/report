"""
parse_migration.py

Reads raw/ directory containing:
  - [COUNTRY]-EUROSTAT-IMMIGRANTS-[YEAR].json
  - IT-ISTAT-[YEAR].csv

Produces: migration_gap.csv with columns:
  DESTINATION_STATE, YEAR, ISTAT_DELETED, DEST_REGISTERED
"""

import json
import csv
import re
from pathlib import Path

RAW_DIR     = Path("raw")
OUTPUT_FILE = Path("migration_gap.csv")

def compute_flat_index(dims, sizes, cats, selections):
    """
    Compute the flat (row-major) index for a JSON-stat dataset.
    dims:       ordered list of dimension names  (data["id"])
    sizes:      size of each dimension           (data["size"])
    cats:       dimension metadata               (data["dimension"])
    selections: { dim_name: category_code }
    """
    indices = []
    for dim in dims:
        code = selections[dim]
        indices.append(cats[dim]["category"]["index"][code])

    flat, stride = 0, 1
    for i in reversed(range(len(dims))):
        flat   += indices[i] * stride
        stride *= sizes[i]
    return flat


def parse_eurostat(path):
    """
    Extract total Italian immigrants (all ages, both sexes) from a JSON-stat file.
    Selects: agedef=COMPLET, age=TOTAL, sex=T.
    geo and time are inferred from the file (single-valued after filtering).
    """
    with open(path) as f:
        data = json.load(f)

    dims  = data["id"]
    sizes = data["size"]
    cats  = data["dimension"]

    geo_code  = next(iter(cats["geo"]["category"]["index"]))
    time_code = next(iter(cats["time"]["category"]["index"]))

    selections = {
        "freq":    "A",
        "citizen": "IT",
        "agedef":  "COMPLET",
        "age":     "TOTAL",
        "unit":    "NR",
        "sex":     "T",
        "geo":     geo_code,
        "time":    time_code,
    }

    key   = compute_flat_index(dims, sizes, cats, selections)
    value = data["value"].get(str(key))
    return int(value) if value is not None else None

def parse_istat(path):
    """
    Parse an ISTAT CSV (tab-separated, UTF-8 with optional BOM).

    Filters:
      CITIZENSHIP = IT    => only Italian citizens
      SEX         = 9     => total (both sexes)
      AGE         = TOTAL => all ages combined

    Observation value is the column immediately after TIME_PERIOD
    (ISTAT export does not name it).

    Returns: { COUNTRY_NEXT_RESID_code: count }
    """
    with open(path, encoding="utf-8-sig") as f:
        raw_lines = f.readlines()

    headers = [h.strip() for h in raw_lines[0].split("\t")]

    def col(name):
        try:
            return headers.index(name)
        except ValueError:
            raise RuntimeError(f"Column '{name}' not found in {path}.\nHeaders: {headers}")

    idx_citizenship = col("CITIZENSHIP")
    idx_sex         = col("SEX")
    idx_age         = col("AGE")
    idx_country     = col("COUNTRY_NEXT_RESID")
    idx_year        = col("TIME_PERIOD")
    idx_obs         = idx_year + 1   # observation value has no header name

    result = {}
    for line in raw_lines[1:]:
        cols = line.rstrip("\n").split("\t")
        if len(cols) <= idx_obs:
            continue
        if (
            cols[idx_citizenship].strip() == "IT"
            and cols[idx_sex].strip()     == "9"
            and cols[idx_age].strip()     == "TOTAL"
        ):
            country = cols[idx_country].strip()
            raw_val = cols[idx_obs].strip()
            try:
                result[country] = int(raw_val)
            except ValueError:
                pass

    return result

def main():
    eurostat_re = re.compile(r"^([A-Z]{2})-EUROSTAT-IMMIGRANTS-(\d{4})\.json$")
    istat_re    = re.compile(r"^IT-ISTAT-(\d{4})\.csv$")

    eurostat_files = {}
    istat_files    = {}

    for f in RAW_DIR.iterdir():
        m = eurostat_re.match(f.name)
        if m:
            eurostat_files[(m.group(1), m.group(2))] = f
            continue
        m = istat_re.match(f.name)
        if m:
            istat_files[m.group(1)] = f

    istat_cache = {}
    for year, path in sorted(istat_files.items()):
        print(f"Parsing ISTAT {year} ...")
        istat_cache[year] = parse_istat(path)

    rows = []
    for (country, year), path in sorted(eurostat_files.items()):
        dest_registered = parse_eurostat(path)
        istat_deleted   = istat_cache.get(year, {}).get(country)

        rows.append({
            "DESTINATION_STATE": country,
            "YEAR":              int(year),
            "ISTAT_DELETED":     istat_deleted   if istat_deleted   is not None else "",
            "DEST_REGISTERED":   dest_registered if dest_registered is not None else "",
        })
        print(f"  {country} {year}: ISTAT={str(istat_deleted):>6}  EUROSTAT={dest_registered}")

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["DESTINATION_STATE", "YEAR", "ISTAT_DELETED", "DEST_REGISTERED"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nDone => {OUTPUT_FILE}  ({len(rows)} rows)")


if __name__ == "__main__":
    main()