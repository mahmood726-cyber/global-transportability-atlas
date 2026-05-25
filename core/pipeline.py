import csv
import datetime
import hashlib
import json
import math
import os
import string
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RESULTS_PATH = REPO_ROOT / "data" / "atlas_results.json"

SOURCE_MATRIX_ENV = "GLOBAL_TRANSPORTABILITY_MATRIX"
WORLD_BANK_CATALOG_ENV = "WORLD_BANK_COUNTRIES_CSV"
WORLD_BANK_WDI_ENV = "WORLD_BANK_WDI_COUNTRY_CSV"

SOURCE_MATRIX_SUFFIXES = (
    Path("transportability_ma/output/global_transportability_matrix.csv"),
    Path("Projects/transportability_ma/output/global_transportability_matrix.csv"),
)
WORLD_BANK_CATALOG_SUFFIXES = (
    Path("WorldBankData/catalogs/countries.csv"),
    Path("Projects/WorldBankData/catalogs/countries.csv"),
)
WORLD_BANK_WDI_SUFFIXES = (
    Path("WorldBankData/bulk_downloads/WDI_CSV/WDICountry.csv"),
    Path("Projects/WorldBankData/bulk_downloads/WDI_CSV/WDICountry.csv"),
)


def _iter_drive_roots():
    for letter in string.ascii_uppercase:
        root = Path(f"{letter}:/")
        if root.exists():
            yield root


def _candidate_bases():
    seen = set()
    for base in (REPO_ROOT.parent, REPO_ROOT.parent.parent, *list(_iter_drive_roots())):
        resolved = str(base.resolve())
        if resolved not in seen:
            seen.add(resolved)
            yield base


def _resolve_input_path(env_name, suffixes):
    env_value = os.environ.get(env_name)
    if env_value:
        env_path = Path(env_value).expanduser()
        if env_path.exists():
            return env_path
        raise FileNotFoundError(f"{env_name} points to a missing path: {env_path}")

    for base in _candidate_bases():
        for suffix in suffixes:
            candidate = base / suffix
            if candidate.exists():
                return candidate

    suffix_list = ", ".join(str(s) for s in suffixes)
    raise FileNotFoundError(
        f"Unable to locate a source file for {env_name}. "
        f"Set the environment variable or place one of these relative paths on an available drive: {suffix_list}"
    )


def _read_csv_rows(path):
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _safe_float(value):
    if value in (None, "", "NA", "NaN", "nan"):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _mean(values):
    nums = [value for value in values if value is not None]
    if not nums:
        return None
    return sum(nums) / len(nums)


def _clip(value, lower, upper):
    return max(lower, min(upper, value))


def generate_signature(data):
    data_str = json.dumps(data, sort_keys=True)
    return hashlib.sha256(data_str.encode("utf-8")).hexdigest()


def generate_truthcert_hash(data):
    return f"SHA256:{generate_signature(data)}"


def _load_country_metadata(catalog_path, wdi_country_path):
    catalog_rows = _read_csv_rows(catalog_path)
    wdi_rows = _read_csv_rows(wdi_country_path)

    iso2_meta = {}
    for row in catalog_rows:
        iso2 = (row.get("iso2Code") or "").strip().upper()
        if not iso2:
            continue
        lon = _safe_float(row.get("longitude"))
        lat = _safe_float(row.get("latitude"))
        coordinates = [lat, lon] if lat is not None and lon is not None else None
        iso2_meta[iso2] = {
            "country_name": (row.get("name") or "").strip() or iso2,
            "region": (row.get("region") or "").strip() or "Unknown",
            "coordinates": coordinates,
        }

    metadata = {}
    for row in wdi_rows:
        iso3 = (row.get("Country Code") or "").strip().upper()
        iso2 = (row.get("2-alpha code") or "").strip().upper()
        if not iso3 or not iso2 or iso2 not in iso2_meta:
            continue
        country_meta = iso2_meta[iso2]
        metadata[iso3] = {
            "country_name": (row.get("Short Name") or "").strip() or country_meta["country_name"],
            "region": country_meta["region"],
            "coordinates": country_meta["coordinates"],
        }
    return metadata


def _aggregate_country_rows(matrix_rows, country_metadata):
    grouped = defaultdict(list)
    for row in matrix_rows:
        iso3 = (row.get("iso3c") or "").strip().upper()
        if iso3:
            grouped[iso3].append(row)

    map_data = []
    priority_raw_max = 0.0

    for iso3, rows in sorted(grouped.items()):
        transported_effect = _mean(_safe_float(row.get("transported_effect")) for row in rows)
        ci_lb = _mean(_safe_float(row.get("ci_lb")) for row in rows)
        ci_ub = _mean(_safe_float(row.get("ci_ub")) for row in rows)
        transportability_score = _clip(_mean(_safe_float(row.get("relevance_score")) for row in rows) or 0.0, 0.0, 1.0)
        evidence_gap = 1.0 - transportability_score
        e_value = _mean(_safe_float(row.get("e_value")) for row in rows) or 0.0
        population = _mean(_safe_float(row.get("population")) for row in rows) or 0.0
        priority_raw = evidence_gap * math.log10(population + 1.0) * e_value
        priority_raw_max = max(priority_raw_max, priority_raw)

        meta = country_metadata.get(iso3, {})
        country_name = meta.get("country_name", iso3)

        covariates = {
            "age_65up": _mean(_safe_float(row.get("age_65up")) for row in rows),
            "life_exp": _mean(_safe_float(row.get("life_exp")) for row in rows),
            "hexp_pc": _mean(_safe_float(row.get("hexp_pc")) for row in rows),
            "physicians": _mean(_safe_float(row.get("physicians")) for row in rows),
            "stability": _mean(_safe_float(row.get("stability")) for row in rows),
            "diabetes_prev": _mean(_safe_float(row.get("diabetes_prev")) for row in rows),
            "age_dependency": _mean(_safe_float(row.get("age_dependency")) for row in rows),
            "population": population,
        }

        effect_ratio = math.exp(transported_effect) if transported_effect is not None else None
        effect_ci = (
            [math.exp(ci_lb), math.exp(ci_ub)]
            if ci_lb is not None and ci_ub is not None
            else None
        )

        map_data.append(
            {
                "iso3": iso3,
                "country_name": country_name,
                "region": meta.get("region", "Unknown"),
                "transportability_score": transportability_score,
                "transport_propensity": transportability_score,
                "evidence_gap": evidence_gap,
                "priority_score_raw": priority_raw,
                "priority_score": 0.0,
                "effect_ratio": effect_ratio,
                "effect_ci": effect_ci,
                "transported_effect": transported_effect,
                "e_value": e_value,
                "sexes": sorted({(row.get("sex") or "").strip() for row in rows if (row.get("sex") or "").strip()}),
                "sex_row_count": len(rows),
                "readiness_score": transportability_score * 100.0,
                "covariates": covariates,
                "spatial_metrics": {
                    "coordinates": meta.get("coordinates"),
                    "region": meta.get("region", "Unknown"),
                },
            }
        )

    scale = priority_raw_max or 1.0
    for row in map_data:
        row["priority_score"] = (row["priority_score_raw"] / scale) * 100.0

    return map_data


def _build_reference_profile(map_data):
    return {
        "label": "Matrix Mean",
        "age_65up": _mean(row["covariates"]["age_65up"] for row in map_data),
        "life_exp": _mean(row["covariates"]["life_exp"] for row in map_data),
        "hexp_pc": _mean(row["covariates"]["hexp_pc"] for row in map_data),
        "physicians": _mean(row["covariates"]["physicians"] for row in map_data),
    }


def run_pipeline(
    source_matrix_path=None,
    world_bank_catalog_path=None,
    world_bank_wdi_path=None,
    output_path=RESULTS_PATH,
):
    source_matrix_path = Path(source_matrix_path) if source_matrix_path else _resolve_input_path(SOURCE_MATRIX_ENV, SOURCE_MATRIX_SUFFIXES)
    world_bank_catalog_path = Path(world_bank_catalog_path) if world_bank_catalog_path else _resolve_input_path(WORLD_BANK_CATALOG_ENV, WORLD_BANK_CATALOG_SUFFIXES)
    world_bank_wdi_path = Path(world_bank_wdi_path) if world_bank_wdi_path else _resolve_input_path(WORLD_BANK_WDI_ENV, WORLD_BANK_WDI_SUFFIXES)
    output_path = Path(output_path)

    matrix_rows = _read_csv_rows(source_matrix_path)
    country_metadata = _load_country_metadata(world_bank_catalog_path, world_bank_wdi_path)
    map_data = _aggregate_country_rows(matrix_rows, country_metadata)
    reference_profile = _build_reference_profile(map_data)

    payload = {
        "reference_profile": reference_profile,
        "map_data": map_data,
    }
    payload_hash = generate_signature(payload)

    audit = {
        "timestamp": datetime.datetime.now().isoformat(),
        "methodology": "Local transportability matrix rebuild from F-drive source outputs",
        "source_files": {
            "global_transportability_matrix": str(source_matrix_path),
            "world_bank_catalog": str(world_bank_catalog_path),
            "world_bank_wdi_country": str(world_bank_wdi_path),
        },
        "country_count": len(map_data),
        "matrix_row_count": len(matrix_rows),
        "hash": f"SHA256:{payload_hash}",
        "signatures": {
            "payload_hash": f"SHA256:{payload_hash}",
        },
    }

    output = {
        "audit": audit,
        "reference_profile": reference_profile,
        "map_data": map_data,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Rebuilt atlas with {len(map_data)} countries from {source_matrix_path}.")
    return output


if __name__ == "__main__":
    run_pipeline()
