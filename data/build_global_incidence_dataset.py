"""
Build a global top-disease list by incidence from a GBD Results Tool CSV export.

Usage:
  python data/build_global_incidence_dataset.py --input path/to/gbd.csv --top 1000

Notes:
  - Requires a GBD Results Tool CSV export with incidence by cause.
  - If fewer than N causes exist (GBD lists 371 diseases/injuries),
    the script will output all available causes.
"""

import argparse
import json
from pathlib import Path

import pandas as pd


def pick_column(df, candidates):
    lower_map = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand in lower_map:
            return lower_map[cand]
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to GBD Results Tool CSV")
    parser.add_argument("--top", type=int, default=1000, help="Top N diseases by incidence")
    parser.add_argument("--year", type=int, default=None, help="Year filter (default: latest in file)")
    parser.add_argument("--output", default="data/global_incidence_top_diseases.json", help="Output JSON path")
    parser.add_argument("--output-csv", default="data/global_incidence_top_diseases.csv", help="Output CSV path")
    args = parser.parse_args()

    df = pd.read_csv(args.input)

    # Detect columns robustly
    col_cause = pick_column(df, ["cause", "cause_name", "cause name"])
    col_measure = pick_column(df, ["measure", "measure_name", "measure name"])
    col_metric = pick_column(df, ["metric", "metric_name", "metric name"])
    col_location = pick_column(df, ["location", "location_name", "location name"])
    col_sex = pick_column(df, ["sex", "sex_name", "sex name"])
    col_age = pick_column(df, ["age", "age_name", "age name"])
    col_year = pick_column(df, ["year"])
    col_val = pick_column(df, ["val", "value"])

    missing = [name for name, col in [
        ("cause", col_cause), ("measure", col_measure), ("metric", col_metric),
        ("location", col_location), ("sex", col_sex), ("age", col_age),
        ("year", col_year), ("val", col_val)
    ] if col is None]

    if missing:
        raise SystemExit(f"Missing required columns: {', '.join(missing)}")

    filtered = df.copy()

    # Measure: incidence
    filtered = filtered[filtered[col_measure].str.lower().str.contains("incidence", na=False)]

    # Metric: number (not rate/percent)
    if col_metric:
        filtered = filtered[filtered[col_metric].str.lower().str.contains("number", na=False)]

    # Location: Global
    if col_location:
        filtered = filtered[filtered[col_location].str.lower() == "global"]

    # Sex: Both
    if col_sex:
        filtered = filtered[filtered[col_sex].str.lower() == "both"]

    # Age: All ages
    if col_age:
        filtered = filtered[filtered[col_age].str.lower().str.contains("all", na=False)]

    # Year filter
    if col_year:
        if args.year is None:
            args.year = int(filtered[col_year].max())
        filtered = filtered[filtered[col_year] == args.year]

    if filtered.empty:
        raise SystemExit("No rows left after filtering. Check your CSV filters.")

    # Aggregate by cause (some exports have duplicate rows)
    grouped = (
        filtered.groupby(col_cause, as_index=False)[col_val]
        .sum()
        .sort_values(col_val, ascending=False)
    )

    top = grouped.head(args.top).copy()

    # Output JSON + CSV
    output_path = Path(args.output)
    output_csv_path = Path(args.output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    records = [
        {"rank": i + 1, "disease": row[col_cause], "incidence": float(row[col_val])}
        for i, (_, row) in enumerate(top.iterrows())
    ]

    output_path.write_text(json.dumps(records, indent=2))
    top.rename(columns={col_cause: "disease", col_val: "incidence"}).to_csv(output_csv_path, index=False)

    print(f"Saved {len(records)} diseases to {output_path} and {output_csv_path}")


if __name__ == "__main__":
    main()
