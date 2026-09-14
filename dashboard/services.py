import csv
import hashlib
import io
import math
import re

MAX_BYTES = 12 * 1024 * 1024
COLUMNS = [
    "TIME_PERIOD", "CLIM_ACT_POL", "Climate actions and policies",
    "MEASURE", "OBS_VALUE", "OBS_STATUS",
]


def parse_csv(raw: bytes, filename: str) -> dict:
    """Validate an OECD CAPMF Ireland export and return dashboard-ready data."""
    if len(raw) > MAX_BYTES:
        raise ValueError("The CSV must be smaller than 12 MiB.")
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""), strict=True)
    headers = reader.fieldnames or []
    if len(headers) != len(set(headers)):
        raise ValueError("The CSV contains duplicate column names.")
    missing = set(COLUMNS) - set(headers)
    if missing:
        raise ValueError("Missing columns: " + ", ".join(sorted(missing)))

    records, seen, labels, countries = [], set(), {}, set()
    status_counts = {}
    for line, row in enumerate(reader, start=2):
        if line > 150001:
            raise ValueError("The CSV exceeds 150,000 observations.")
        if None in row or any(value is None for value in row.values()):
            raise ValueError(f"Row {line}: incorrect number of fields.")
        measure = row["MEASURE"].strip()
        if measure not in {"POL_STRINGENCY", "POL_COUNT"}:
            continue
        country = row.get("REF_AREA", "").strip()
        if country:
            countries.add(country)
        year_text = row["TIME_PERIOD"].strip()
        if not re.fullmatch(r"\d{4}", year_text):
            raise ValueError(f"Row {line}: invalid year.")
        year = int(year_text)
        if not 1990 <= year <= 2100:
            raise ValueError(f"Row {line}: year outside 1990–2100.")
        policy = row["CLIM_ACT_POL"].strip()
        if not re.fullmatch(r"LEV[1-4]_[A-Z0-9_]+", policy):
            raise ValueError(f"Row {line}: invalid policy code.")
        label = row["Climate actions and policies"].strip()
        if not label or (policy in labels and labels[policy] != label):
            raise ValueError(f"Row {line}: missing or inconsistent policy label.")
        labels[policy] = label
        value_text = row["OBS_VALUE"].strip()
        try:
            value = float(value_text) if value_text else None
        except ValueError as error:
            raise ValueError(f"Row {line}: OBS_VALUE must be numeric or empty.") from error
        if value is not None and (not math.isfinite(value) or value < 0):
            raise ValueError(f"Row {line}: invalid observation value.")
        if value is not None and measure == "POL_STRINGENCY" and value > 10:
            raise ValueError(f"Row {line}: stringency must be between 0 and 10.")
        status = row["OBS_STATUS"].strip()
        if status not in {"", "A", "E", "M", "K"}:
            raise ValueError(f"Row {line}: unsupported status flag.")
        key = (policy, measure, year)
        if key in seen:
            raise ValueError(f"Row {line}: duplicate policy/measure/year record.")
        seen.add(key)
        status_counts[status] = status_counts.get(status, 0) + 1
        records.append([year, policy, label, measure, value, status])

    if countries and countries != {"IRL"}:
        raise ValueError("Please use a single-country Ireland extract.")
    scores = [record for record in records if record[3] == "POL_STRINGENCY"]
    if not scores:
        raise ValueError("No POL_STRINGENCY observations were found.")
    digest = hashlib.sha256(raw).hexdigest()
    return {
        "columns": COLUMNS,
        "rows": records,
        "meta": {
            "country": "Ireland", "source_name": filename, "sha256": digest,
            "version": f"{filename} · SHA256 {digest[:12]}",
            "start_year": min(record[0] for record in scores),
            "end_year": max(record[0] for record in scores),
            "row_count": len(records), "stringency_rows": len(scores),
            "count_rows": len(records) - len(scores), "status_counts": status_counts,
            "edition": "OECD edition not specified in export; filename is extraction metadata.",
        },
    }
