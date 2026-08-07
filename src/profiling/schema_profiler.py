from pathlib import Path
import json
import polars as pl


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
REPORT_DIR = PROJECT_ROOT / "reports" / "schema"

REPORT_DIR.mkdir(parents=True, exist_ok=True)


def profile_csv(file_path: Path) -> dict:
    df = pl.read_csv(
        file_path,
        infer_schema_length=10_000,
    )

    row_count = len(df)

    columns = []

    for column in df.columns:
        series = df.get_column(column)
        unique_count = series.n_unique()
        null_count = series.null_count()

        columns.append(
            {
                "name": column,
                "dtype": str(series.dtype),
                "null_count": null_count,
                "null_percentage": round(
                    null_count / row_count * 100,
                    2,
                )
                if row_count > 0
                else 0,
                "unique_count": unique_count,
                "uniqueness_percentage": round(
                    unique_count / row_count * 100,
                    2,
                )
                if row_count > 0
                else 0,
            }
        )

    duplicate_row_count = row_count - df.unique().height

    return {
        "file_name": file_path.name,
        "file_size_bytes": file_path.stat().st_size,
        "row_count": row_count,
        "column_count": len(df.columns),
        "duplicate_row_count": duplicate_row_count,
        "columns": columns,
    }


def main():
    csv_files = sorted(RAW_DATA_DIR.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files found in {RAW_DATA_DIR}"
        )

    profiles = []

    for file_path in csv_files:
        print(f"Profiling: {file_path.name}")

        profile = profile_csv(file_path)
        profiles.append(profile)

    output_file = REPORT_DIR / "schema_profile.json"

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(profiles, file, indent=2)

    print()
    print(f"Profile completed: {len(profiles)} files")
    print(f"Output: {output_file}")


if __name__ == "__main__":
    main()