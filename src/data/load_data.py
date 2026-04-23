from pathlib import Path
import pandas as pd


RAW_PATH = Path("data/raw/telco_churn.csv")
PROCESSED_DIR = Path("data/processed")
REPORTS_DIR = Path("outputs/metrics")

COLUMN_RENAME_MAP = {
    "customerID": "customer_id",
    "gender": "gender",
    "SeniorCitizen": "senior_citizen",
    "Partner": "partner",
    "Dependents": "dependents",
    "tenure": "tenure",
    "PhoneService": "phone_service",
    "MultipleLines": "multiple_lines",
    "InternetService": "internet_service",
    "OnlineSecurity": "online_security",
    "OnlineBackup": "online_backup",
    "DeviceProtection": "device_protection",
    "TechSupport": "tech_support",
    "StreamingTV": "streaming_tv",
    "StreamingMovies": "streaming_movies",
    "Contract": "contract",
    "PaperlessBilling": "paperless_billing",
    "PaymentMethod": "payment_method",
    "MonthlyCharges": "monthly_charges",
    "TotalCharges": "total_charges",
    "Churn": "churn",
}

CUSTOMERS_COLS = [
    "customer_id",
    "gender",
    "senior_citizen",
    "partner",
    "dependents",
    "tenure",
]

SUBSCRIPTIONS_COLS = [
    "customer_id",
    "contract",
    "paperless_billing",
    "churn",
]

SERVICES_COLS = [
    "customer_id",
    "phone_service",
    "multiple_lines",
    "internet_service",
    "online_security",
    "online_backup",
    "device_protection",
    "tech_support",
    "streaming_tv",
    "streaming_movies",
]

BILLING_COLS = [
    "customer_id",
    "payment_method",
    "monthly_charges",
    "total_charges",
]


def log(message: str) -> None:
    print(f"[load_data] {message}")


def ensure_directories() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def load_raw_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Raw file not found: {path}")

    df = pd.read_csv(path)
    log(f"Loaded raw data with shape: {df.shape}")
    return df


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    missing_raw_cols = [col for col in COLUMN_RENAME_MAP.keys() if col not in df.columns]
    if missing_raw_cols:
        raise ValueError(f"Missing expected raw columns: {missing_raw_cols}")

    df = df.rename(columns=COLUMN_RENAME_MAP)
    log("Standardized column names to snake_case")
    return df


def strip_whitespace(df: pd.DataFrame) -> pd.DataFrame:
    object_cols = df.select_dtypes(include=["object"]).columns
    for col in object_cols:
        df[col] = df[col].astype(str).str.strip()
    return df


def normalize_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    # Chuẩn hóa các chuỗi rỗng / khoảng trắng thành NA
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].replace({"": pd.NA, " ": pd.NA, "nan": pd.NA})
    return df


def cast_data_types(df: pd.DataFrame) -> pd.DataFrame:
    df["senior_citizen"] = pd.to_numeric(df["senior_citizen"], errors="coerce").fillna(0).astype(int)
    df["tenure"] = pd.to_numeric(df["tenure"], errors="coerce")
    df["monthly_charges"] = pd.to_numeric(df["monthly_charges"], errors="coerce")
    df["total_charges"] = pd.to_numeric(df["total_charges"], errors="coerce")
    return df


def validate_required_columns(df: pd.DataFrame, required_cols: list[str], table_name: str) -> None:
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"{table_name}: missing required columns: {missing_cols}")


def validate_primary_key(df: pd.DataFrame, table_name: str) -> None:
    if "customer_id" not in df.columns:
        raise ValueError(f"{table_name}: missing customer_id")

    null_count = int(df["customer_id"].isna().sum())
    dup_count = int(df["customer_id"].duplicated().sum())

    if null_count > 0:
        raise ValueError(f"{table_name}: customer_id has {null_count} null values")
    if dup_count > 0:
        raise ValueError(f"{table_name}: customer_id has {dup_count} duplicated values")


def validate_categorical_values(df: pd.DataFrame) -> None:
    allowed_churn = {"Yes", "No"}
    actual_churn = set(df["churn"].dropna().unique())
    if not actual_churn.issubset(allowed_churn):
        raise ValueError(f"Unexpected churn values found: {actual_churn - allowed_churn}")


def build_tables(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    customers = df[CUSTOMERS_COLS].copy()
    subscriptions = df[SUBSCRIPTIONS_COLS].copy()
    services = df[SERVICES_COLS].copy()
    billing = df[BILLING_COLS].copy()

    return {
        "customers": customers,
        "subscriptions": subscriptions,
        "services": services,
        "billing": billing,
    }


def save_tables(tables: dict[str, pd.DataFrame]) -> None:
    for table_name, table_df in tables.items():
        output_path = PROCESSED_DIR / f"{table_name}.csv"
        table_df.to_csv(output_path, index=False)
        log(f"Saved {table_name}: {output_path} | shape={table_df.shape}")


def write_summary_report(raw_df: pd.DataFrame, tables: dict[str, pd.DataFrame]) -> None:
    report_path = REPORTS_DIR / "step3_data_split_summary.txt"

    total_charges_nulls = int(raw_df["total_charges"].isna().sum())
    lines = [
        "STEP 3 DATA SPLIT SUMMARY",
        "=" * 40,
        f"Raw dataset shape: {raw_df.shape}",
        "",
        "Processed tables:",
    ]

    for table_name, table_df in tables.items():
        lines.append(f"- {table_name}: shape={table_df.shape}")

    lines.extend(
        [
            "",
            "Validation checks:",
            f"- total_charges null count: {total_charges_nulls}",
            f"- customer_id unique in raw: {raw_df['customer_id'].nunique() == len(raw_df)}",
            "",
            "Dtypes preview:",
        ]
    )

    for table_name, table_df in tables.items():
        lines.append(f"\n[{table_name}]")
        for col, dtype in table_df.dtypes.items():
            lines.append(f"  - {col}: {dtype}")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    log(f"Saved summary report: {report_path}")


def print_preview(tables: dict[str, pd.DataFrame]) -> None:
    for table_name, table_df in tables.items():
        log(f"Preview for {table_name}")
        print(table_df.head(3))
        print(table_df.dtypes)
        print("-" * 60)


def main() -> None:
    ensure_directories()

    raw_df = load_raw_data(RAW_PATH)
    df = standardize_columns(raw_df)
    df = strip_whitespace(df)
    df = normalize_missing_values(df)
    df = cast_data_types(df)

    # Validate sau khi clean
    validate_required_columns(df, CUSTOMERS_COLS + SUBSCRIPTIONS_COLS[1:] + SERVICES_COLS[1:] + BILLING_COLS[1:], "raw_cleaned")
    validate_primary_key(df[["customer_id"]].copy(), "raw_cleaned")
    validate_categorical_values(df)

    tables = build_tables(df)

    for table_name, table_df in tables.items():
        validate_primary_key(table_df, table_name)

    save_tables(tables)
    write_summary_report(df, tables)
    print_preview(tables)

    log("Step 3 completed successfully.")


if __name__ == "__main__":
    main()