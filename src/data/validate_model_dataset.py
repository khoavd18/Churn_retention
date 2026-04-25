from pathlib import Path

import pandas as pd
from pandas.api.types import is_numeric_dtype, is_object_dtype, is_string_dtype


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = PROJECT_ROOT / "data" / "processed" / "model_dataset.csv"
REPORTS_DIR = PROJECT_ROOT / "outputs" / "metrics"

REPORT_PATH = REPORTS_DIR / "step5_model_data_quality_report.txt"
MISSING_SUMMARY_PATH = REPORTS_DIR / "step5_missing_summary.csv"
CONSTANT_COLUMNS_PATH = REPORTS_DIR / "step5_constant_columns.txt"
TARGET_DISTRIBUTION_PATH = REPORTS_DIR / "step5_target_distribution.csv"

ALLOWED_CHURN_VALUES = {"Yes", "No"}
EXPECTED_COLUMNS = [
    "customer_id",
    "gender",
    "senior_citizen",
    "partner",
    "dependents",
    "tenure",
    "contract",
    "paperless_billing",
    "churn",
    "phone_service",
    "multiple_lines",
    "internet_service",
    "online_security",
    "online_backup",
    "device_protection",
    "tech_support",
    "streaming_tv",
    "streaming_movies",
    "payment_method",
    "monthly_charges",
    "total_charges",
    "tenure_group",
    "is_new_customer",
    "is_month_to_month",
    "is_paperless_billing",
    "has_online_security",
    "has_online_backup",
    "has_device_protection",
    "has_tech_support",
    "has_streaming_tv",
    "has_streaming_movies",
    "monthly_charge_band",
    "is_electronic_check",
    "is_total_charges_missing",
]
STRING_COLUMNS = [
    "customer_id",
    "gender",
    "partner",
    "dependents",
    "contract",
    "paperless_billing",
    "churn",
    "phone_service",
    "multiple_lines",
    "internet_service",
    "online_security",
    "online_backup",
    "device_protection",
    "tech_support",
    "streaming_tv",
    "streaming_movies",
    "payment_method",
    "tenure_group",
    "monthly_charge_band",
]
NUMERIC_COLUMNS = [
    "senior_citizen",
    "tenure",
    "monthly_charges",
    "total_charges",
    "is_new_customer",
    "is_month_to_month",
    "is_paperless_billing",
    "has_online_security",
    "has_online_backup",
    "has_device_protection",
    "has_tech_support",
    "has_streaming_tv",
    "has_streaming_movies",
    "is_electronic_check",
    "is_total_charges_missing",
]
BINARY_FLAG_COLUMNS = [
    "is_new_customer",
    "is_month_to_month",
    "is_paperless_billing",
    "has_online_security",
    "has_online_backup",
    "has_device_protection",
    "has_tech_support",
    "has_streaming_tv",
    "has_streaming_movies",
    "is_electronic_check",
    "is_total_charges_missing",
]
MODELING_EXCLUDE_COLUMNS = ["customer_id"]
OVERLAP_COLUMN_PAIRS = [
    ("contract", "is_month_to_month"),
    ("paperless_billing", "is_paperless_billing"),
    ("online_security", "has_online_security"),
    ("online_backup", "has_online_backup"),
    ("device_protection", "has_device_protection"),
    ("tech_support", "has_tech_support"),
    ("streaming_tv", "has_streaming_tv"),
    ("streaming_movies", "has_streaming_movies"),
]


def log(message: str) -> None:
    print(f"[validate_model_dataset] {message}")


def ensure_directories() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def load_dataset(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Model dataset not found: {path}")

    df = pd.read_csv(path)
    log(f"Loaded dataset: {path.relative_to(PROJECT_ROOT)} | shape={df.shape}")
    return df


def format_list(items: list[str]) -> str:
    return ", ".join(items) if items else "None"


def format_metric(value: int | None) -> str:
    return str(value) if value is not None else "N/A (required column missing)"


def validate_schema(df: pd.DataFrame) -> dict[str, list[str]]:
    missing_columns = [column for column in EXPECTED_COLUMNS if column not in df.columns]
    unexpected_columns = [column for column in df.columns if column not in EXPECTED_COLUMNS]
    dtype_issues: list[str] = []

    for column in STRING_COLUMNS:
        if column in df.columns and not (is_object_dtype(df[column]) or is_string_dtype(df[column])):
            dtype_issues.append(f"{column}: expected string-like, found {df[column].dtype}")

    for column in NUMERIC_COLUMNS:
        if column in df.columns and not is_numeric_dtype(df[column]):
            dtype_issues.append(f"{column}: expected numeric, found {df[column].dtype}")

    return {
        "missing_columns": missing_columns,
        "unexpected_columns": unexpected_columns,
        "dtype_issues": dtype_issues,
    }


def build_missing_summary(df: pd.DataFrame) -> pd.DataFrame:
    denominator = len(df) if len(df) > 0 else 1
    summary = pd.DataFrame(
        {
            "column_name": df.columns,
            "missing_count": df.isna().sum().values,
            "missing_pct": ((df.isna().sum() / denominator) * 100).round(4).values,
        }
    )
    return summary.sort_values(["missing_count", "column_name"], ascending=[False, True]).reset_index(drop=True)


def build_constant_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for column_name in df.columns:
        distinct_count = int(df[column_name].nunique(dropna=False))
        if distinct_count <= 1:
            unique_values = df[column_name].drop_duplicates().tolist()
            constant_value = unique_values[0] if unique_values else pd.NA
            rows.append(
                {
                    "column_name": column_name,
                    "distinct_count": distinct_count,
                    "constant_value": constant_value,
                }
            )

    return pd.DataFrame(rows, columns=["column_name", "distinct_count", "constant_value"])


def build_target_distribution(df: pd.DataFrame) -> pd.DataFrame:
    if "churn" not in df.columns:
        return pd.DataFrame(columns=["churn", "row_count", "row_pct"])

    churn_series = df["churn"].fillna("MISSING")
    distribution = (
        churn_series.value_counts(dropna=False)
        .rename_axis("churn")
        .reset_index(name="row_count")
    )
    denominator = len(df) if len(df) > 0 else 1
    distribution["row_pct"] = (distribution["row_count"] / denominator).round(6)
    return distribution


def collect_binary_flag_issues(df: pd.DataFrame) -> list[str]:
    issues: list[str] = []

    for column in BINARY_FLAG_COLUMNS:
        if column not in df.columns:
            continue

        invalid_values = sorted(set(df[column].dropna().unique()) - {0, 1})
        if invalid_values:
            issues.append(f"{column}: invalid values {invalid_values}")

    return issues


def collect_business_rule_results(df: pd.DataFrame) -> dict[str, int | None]:
    contract_flag_mismatches = None
    if {"contract", "is_month_to_month"}.issubset(df.columns):
        contract_flag_mismatches = int(
            (df["is_month_to_month"] != (df["contract"] == "Month-to-month").astype(int)).sum()
        )

    paperless_flag_mismatches = None
    if {"paperless_billing", "is_paperless_billing"}.issubset(df.columns):
        paperless_flag_mismatches = int(
            (df["is_paperless_billing"] != (df["paperless_billing"] == "Yes").astype(int)).sum()
        )

    negative_tenure_count = int(df["tenure"].lt(0).sum()) if "tenure" in df.columns else None
    negative_monthly_charges_count = int(df["monthly_charges"].lt(0).sum()) if "monthly_charges" in df.columns else None
    negative_total_charges_count = int(df["total_charges"].lt(0).sum()) if "total_charges" in df.columns else None

    return {
        "contract_flag_mismatches": contract_flag_mismatches,
        "paperless_flag_mismatches": paperless_flag_mismatches,
        "negative_tenure_count": negative_tenure_count,
        "negative_monthly_charges_count": negative_monthly_charges_count,
        "negative_total_charges_count": negative_total_charges_count,
    }


def identify_modeling_flags(df: pd.DataFrame, constant_df: pd.DataFrame) -> dict[str, list[str]]:
    identifier_columns = [column for column in MODELING_EXCLUDE_COLUMNS if column in df.columns]
    constant_columns = constant_df["column_name"].tolist() if not constant_df.empty else []
    overlap_pairs = [
        f"{raw_column} + {derived_column}"
        for raw_column, derived_column in OVERLAP_COLUMN_PAIRS
        if raw_column in df.columns and derived_column in df.columns
    ]

    return {
        "identifier_columns": identifier_columns,
        "constant_columns": constant_columns,
        "overlap_pairs": overlap_pairs,
    }


def determine_readiness(
    df: pd.DataFrame,
    schema_results: dict[str, list[str]],
    customer_id_nulls: int | None,
    customer_id_duplicates: int | None,
    churn_nulls: int | None,
    unexpected_churn_values: list[str],
    binary_flag_issues: list[str],
    business_rules: dict[str, int | None],
    modeling_flags: dict[str, list[str]],
) -> dict[str, object]:
    eda_blockers: list[str] = []

    if df.empty:
        eda_blockers.append("Dataset has 0 rows.")
    if schema_results["missing_columns"]:
        eda_blockers.append(f"Missing required columns: {format_list(schema_results['missing_columns'])}.")
    if schema_results["dtype_issues"]:
        eda_blockers.append(f"Schema dtype issues: {format_list(schema_results['dtype_issues'])}.")
    if customer_id_nulls is not None and customer_id_nulls > 0:
        eda_blockers.append(f"customer_id has {customer_id_nulls} null value(s).")
    if customer_id_duplicates is not None and customer_id_duplicates > 0:
        eda_blockers.append(f"customer_id has {customer_id_duplicates} duplicate row(s).")
    if churn_nulls is not None and churn_nulls > 0:
        eda_blockers.append(f"churn has {churn_nulls} null value(s).")
    if unexpected_churn_values:
        eda_blockers.append(f"Unexpected churn values found: {format_list(unexpected_churn_values)}.")
    if binary_flag_issues:
        eda_blockers.append(f"Binary flag issues found: {format_list(binary_flag_issues)}.")

    for rule_name, count in business_rules.items():
        if count is not None and count > 0:
            eda_blockers.append(f"{rule_name} failed for {count} row(s).")

    step6_required_fixes = list(eda_blockers)

    if modeling_flags["identifier_columns"]:
        step6_required_fixes.append(
            f"Exclude identifier columns before modeling: {format_list(modeling_flags['identifier_columns'])}."
        )

    if modeling_flags["constant_columns"]:
        step6_required_fixes.append(
            f"Drop constant columns before modeling: {format_list(modeling_flags['constant_columns'])}."
        )

    return {
        "eda_ready": len(eda_blockers) == 0,
        "eda_blockers": eda_blockers,
        "step6_model_ready": len(step6_required_fixes) == 0,
        "step6_required_fixes": step6_required_fixes,
    }


def write_missing_summary(summary_df: pd.DataFrame) -> None:
    summary_df.to_csv(MISSING_SUMMARY_PATH, index=False)
    log(f"Wrote missing summary: {MISSING_SUMMARY_PATH.relative_to(PROJECT_ROOT)}")


def write_constant_columns(constant_df: pd.DataFrame) -> None:
    lines = [
        "STEP 5 CONSTANT COLUMNS",
        "=" * 40,
    ]

    if constant_df.empty:
        lines.append("No constant columns found.")
    else:
        lines.append(f"Found {len(constant_df)} constant column(s):")
        for _, row in constant_df.iterrows():
            lines.append(
                f"- {row['column_name']} | distinct_count={row['distinct_count']} | constant_value={row['constant_value']}"
            )

        lines.extend(
            [
                "",
                "Required action before Step 6:",
                "- Drop or exclude constant columns from the modeling feature set.",
            ]
        )

        if "is_total_charges_missing" in constant_df["column_name"].values:
            lines.extend(
                [
                    "- is_total_charges_missing is constant because Step 4 removed rows with missing total_charges.",
                    "- Keep it flagged in quality review, but do not pass it into modeling.",
                ]
            )

    CONSTANT_COLUMNS_PATH.write_text("\n".join(lines), encoding="utf-8")
    log(f"Wrote constant column report: {CONSTANT_COLUMNS_PATH.relative_to(PROJECT_ROOT)}")


def write_target_distribution(distribution_df: pd.DataFrame) -> None:
    distribution_df.to_csv(TARGET_DISTRIBUTION_PATH, index=False)
    log(f"Wrote target distribution: {TARGET_DISTRIBUTION_PATH.relative_to(PROJECT_ROOT)}")


def write_quality_report(
    df: pd.DataFrame,
    schema_results: dict[str, list[str]],
    missing_summary_df: pd.DataFrame,
    constant_df: pd.DataFrame,
    target_distribution_df: pd.DataFrame,
    customer_id_nulls: int | None,
    customer_id_duplicates: int | None,
    churn_nulls: int | None,
    unexpected_churn_values: list[str],
    binary_flag_issues: list[str],
    business_rules: dict[str, int | None],
    modeling_flags: dict[str, list[str]],
    readiness: dict[str, object],
) -> None:
    lines = [
        "STEP 5 MODEL DATA QUALITY REPORT",
        "=" * 40,
        f"Dataset path: {DATASET_PATH.relative_to(PROJECT_ROOT)}",
        f"Dataset shape: {df.shape}",
        "",
        "Summary status:",
        f"- EDA-ready: {'YES' if readiness['eda_ready'] else 'NO'}",
        f"- Step 6 model-ready: {'YES' if readiness['step6_model_ready'] else 'NO'}",
        "",
        "Schema validation:",
        f"- missing required columns: {format_list(schema_results['missing_columns'])}",
        f"- unexpected columns: {format_list(schema_results['unexpected_columns'])}",
        f"- dtype issues: {format_list(schema_results['dtype_issues'])}",
        "",
        "Key validation results:",
        f"- customer_id nulls: {format_metric(customer_id_nulls)}",
        f"- customer_id duplicates: {format_metric(customer_id_duplicates)}",
        f"- churn nulls: {format_metric(churn_nulls)}",
        f"- churn unexpected values: {format_list(unexpected_churn_values)}",
        f"- columns with missing values > 0: {int((missing_summary_df['missing_count'] > 0).sum())}",
        f"- constant columns: {format_list(modeling_flags['constant_columns'])}",
        f"- binary flag issues: {format_list(binary_flag_issues)}",
        "",
        "Business rule checks:",
        f"- contract vs is_month_to_month mismatches: {format_metric(business_rules['contract_flag_mismatches'])}",
        f"- paperless_billing vs is_paperless_billing mismatches: {format_metric(business_rules['paperless_flag_mismatches'])}",
        f"- negative tenure rows: {format_metric(business_rules['negative_tenure_count'])}",
        f"- negative monthly_charges rows: {format_metric(business_rules['negative_monthly_charges_count'])}",
        f"- negative total_charges rows: {format_metric(business_rules['negative_total_charges_count'])}",
        "",
        "Target distribution:",
    ]

    if target_distribution_df.empty:
        lines.append("- Not available because churn column is missing.")
    else:
        for _, row in target_distribution_df.iterrows():
            lines.append(f"- {row['churn']}: count={row['row_count']}, pct={row['row_pct']:.6f}")

    lines.extend(
        [
            "",
            "Modeling prep flags:",
            f"- identifier columns to exclude before modeling: {format_list(modeling_flags['identifier_columns'])}",
            f"- constant columns to drop before modeling: {format_list(modeling_flags['constant_columns'])}",
            f"- overlapping raw + derived column pairs to review before Step 6: {format_list(modeling_flags['overlap_pairs'])}",
            "",
            "Schema / dtypes:",
        ]
    )

    for column_name, dtype in df.dtypes.items():
        lines.append(f"- {column_name}: {dtype}")

    lines.extend(
        [
            "",
            "EDA blockers:",
        ]
    )

    if readiness["eda_blockers"]:
        for issue in readiness["eda_blockers"]:
            lines.append(f"- {issue}")
    else:
        lines.append("- No blocking data quality issues found for EDA.")

    lines.extend(
        [
            "",
            "Required fixes before Step 6:",
        ]
    )

    if readiness["step6_required_fixes"]:
        for issue in readiness["step6_required_fixes"]:
            lines.append(f"- {issue}")
    else:
        lines.append("- No required fixes identified before Step 6.")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    log(f"Wrote quality report: {REPORT_PATH.relative_to(PROJECT_ROOT)}")


def main() -> None:
    ensure_directories()

    df = load_dataset(DATASET_PATH)
    schema_results = validate_schema(df)

    customer_id_nulls = int(df["customer_id"].isna().sum()) if "customer_id" in df.columns else None
    customer_id_duplicates = int(df["customer_id"].duplicated().sum()) if "customer_id" in df.columns else None
    churn_nulls = int(df["churn"].isna().sum()) if "churn" in df.columns else None
    unexpected_churn_values = (
        sorted(set(df["churn"].dropna().unique()) - ALLOWED_CHURN_VALUES)
        if "churn" in df.columns
        else []
    )

    missing_summary_df = build_missing_summary(df)
    constant_df = build_constant_summary(df)
    target_distribution_df = build_target_distribution(df)
    binary_flag_issues = collect_binary_flag_issues(df)
    business_rules = collect_business_rule_results(df)
    modeling_flags = identify_modeling_flags(df, constant_df)
    readiness = determine_readiness(
        df=df,
        schema_results=schema_results,
        customer_id_nulls=customer_id_nulls,
        customer_id_duplicates=customer_id_duplicates,
        churn_nulls=churn_nulls,
        unexpected_churn_values=unexpected_churn_values,
        binary_flag_issues=binary_flag_issues,
        business_rules=business_rules,
        modeling_flags=modeling_flags,
    )

    write_missing_summary(missing_summary_df)
    write_constant_columns(constant_df)
    write_target_distribution(target_distribution_df)
    write_quality_report(
        df=df,
        schema_results=schema_results,
        missing_summary_df=missing_summary_df,
        constant_df=constant_df,
        target_distribution_df=target_distribution_df,
        customer_id_nulls=customer_id_nulls,
        customer_id_duplicates=customer_id_duplicates,
        churn_nulls=churn_nulls,
        unexpected_churn_values=unexpected_churn_values,
        binary_flag_issues=binary_flag_issues,
        business_rules=business_rules,
        modeling_flags=modeling_flags,
        readiness=readiness,
    )

    log("Step 5 validation completed successfully.")


if __name__ == "__main__":
    main()
