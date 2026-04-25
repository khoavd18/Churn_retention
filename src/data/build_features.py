import os
from pathlib import Path

import duckdb


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SQL_DIR = PROJECT_ROOT / "sql"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "outputs" / "metrics"

SQL_FILES = [
    SQL_DIR / "01_create_base_tables.sql",
    SQL_DIR / "02_feature_engineering.sql",
    SQL_DIR / "03_model_dataset.sql",
]


def log(message: str) -> None:
    print(f"[build_features] {message}")


def ensure_directories() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def run_sql_script(connection: duckdb.DuckDBPyConnection, script_path: Path) -> None:
    if not script_path.exists():
        raise FileNotFoundError(f"SQL file not found: {script_path}")

    script_text = script_path.read_text(encoding="utf-8")
    statements = [statement.strip() for statement in script_text.split(";") if statement.strip()]

    for statement in statements:
        connection.execute(statement)

    log(f"Executed SQL script: {script_path.relative_to(PROJECT_ROOT)}")


def export_model_dataset(connection: duckdb.DuckDBPyConnection) -> Path:
    output_path = PROCESSED_DIR / "model_dataset.csv"
    escaped_path = output_path.as_posix().replace("'", "''")

    connection.execute(
        f"""
        COPY model_dataset
        TO '{escaped_path}'
        WITH (FORMAT CSV, HEADER TRUE);
        """
    )
    log(f"Exported model dataset to: {output_path.relative_to(PROJECT_ROOT)}")
    return output_path


def collect_metrics(connection: duckdb.DuckDBPyConnection) -> dict[str, object]:
    feature_base_row_count = connection.execute("SELECT COUNT(*) FROM feature_base").fetchone()[0]
    model_dataset_row_count = connection.execute("SELECT COUNT(*) FROM model_dataset").fetchone()[0]
    missing_total_charges_count = connection.execute(
        "SELECT COUNT(*) FROM feature_base WHERE total_charges IS NULL"
    ).fetchone()[0]

    final_columns = [
        row[0]
        for row in connection.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'model_dataset'
            ORDER BY ordinal_position
            """
        ).fetchall()
    ]

    return {
        "feature_base_row_count": feature_base_row_count,
        "model_dataset_row_count": model_dataset_row_count,
        "dropped_row_count": feature_base_row_count - model_dataset_row_count,
        "missing_total_charges_count": missing_total_charges_count,
        "final_columns": final_columns,
    }


def write_summary_report(metrics: dict[str, object]) -> Path:
    report_path = REPORTS_DIR / "step4_feature_build_summary.txt"
    lines = [
        "STEP 4 FEATURE BUILD SUMMARY",
        "=" * 40,
        f"feature_base row count: {metrics['feature_base_row_count']}",
        f"model_dataset row count: {metrics['model_dataset_row_count']}",
        f"dropped row count: {metrics['dropped_row_count']}",
        f"missing total_charges count: {metrics['missing_total_charges_count']}",
        "",
        "Final column list:",
    ]

    for column_name in metrics["final_columns"]:
        lines.append(f"- {column_name}")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    log(f"Wrote summary report: {report_path.relative_to(PROJECT_ROOT)}")
    return report_path


def main() -> None:
    ensure_directories()

    original_cwd = Path.cwd()
    connection = duckdb.connect(database=":memory:")

    try:
        # SQL files use repo-relative CSV paths, so execute them from the project root.
        os.chdir(PROJECT_ROOT)

        for sql_file in SQL_FILES:
            run_sql_script(connection, sql_file)

        export_model_dataset(connection)
        metrics = collect_metrics(connection)
        write_summary_report(metrics)

        log("Step 4 completed successfully.")
    finally:
        connection.close()
        os.chdir(original_cwd)


if __name__ == "__main__":
    main()
