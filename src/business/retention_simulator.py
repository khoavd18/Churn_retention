from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
METRICS_DIR = PROJECT_ROOT / "outputs" / "metrics"
REPORTS_DIR = PROJECT_ROOT / "reports"

THRESHOLD_INPUT_PATH = METRICS_DIR / "threshold_comparison.csv"
TOPK_INPUT_PATH = METRICS_DIR / "topk_comparison.csv"
SIMULATION_OUTPUT_PATH = METRICS_DIR / "retention_simulation.csv"
RECOMMENDATION_OUTPUT_PATH = REPORTS_DIR / "business_recommendation.md"

MODEL_NAME = "GradientBoostingClassifier"
THRESHOLD_VALUE = 0.40
TOP_K_VALUE = 0.10

OUTREACH_COST_PER_CUSTOMER = 5
SAVE_SUCCESS_RATE = 0.15
RETAINED_VALUE_PER_RECOVERED_CUSTOMER = 200


def require_single_row(df: pd.DataFrame, mask: pd.Series, description: str) -> pd.Series:
    matches = df.loc[mask]
    if matches.empty:
        raise ValueError(f"Could not find required setup in existing metrics: {description}")
    if len(matches) > 1:
        raise ValueError(f"Found multiple rows for required setup: {description}")
    return matches.iloc[0]


def calculate_business_values(
    scenario: str,
    operating_setup: str,
    selected_customers: int,
    observed_churners_captured: int,
) -> dict[str, object]:
    expected_recovered_customers = observed_churners_captured * SAVE_SUCCESS_RATE
    campaign_cost = selected_customers * OUTREACH_COST_PER_CUSTOMER
    expected_retained_value = expected_recovered_customers * RETAINED_VALUE_PER_RECOVERED_CUSTOMER

    return {
        "scenario": scenario,
        "model": MODEL_NAME,
        "operating_setup": operating_setup,
        "selected_customers": int(selected_customers),
        "observed_churners_captured": int(observed_churners_captured),
        "expected_recovered_customers": round(float(expected_recovered_customers), 2),
        "campaign_cost": round(float(campaign_cost), 2),
        "expected_retained_value": round(float(expected_retained_value), 2),
        "expected_net_value": round(float(expected_retained_value - campaign_cost), 2),
    }


def load_simulation_inputs() -> tuple[pd.Series, pd.Series]:
    if not THRESHOLD_INPUT_PATH.exists():
        raise FileNotFoundError(f"Missing threshold metrics: {THRESHOLD_INPUT_PATH}")
    if not TOPK_INPUT_PATH.exists():
        raise FileNotFoundError(f"Missing top-k metrics: {TOPK_INPUT_PATH}")

    threshold_df = pd.read_csv(THRESHOLD_INPUT_PATH)
    topk_df = pd.read_csv(TOPK_INPUT_PATH)

    threshold_row = require_single_row(
        threshold_df,
        (threshold_df["model"].eq(MODEL_NAME))
        & ((threshold_df["threshold"] - THRESHOLD_VALUE).abs() < 1e-9),
        f"{MODEL_NAME} threshold {THRESHOLD_VALUE:.2f}",
    )
    topk_row = require_single_row(
        topk_df,
        (topk_df["model"].eq(MODEL_NAME)) & ((topk_df["top_k"] - TOP_K_VALUE).abs() < 1e-9),
        f"{MODEL_NAME} top {TOP_K_VALUE:.0%}",
    )

    return threshold_row, topk_row


def build_simulation() -> pd.DataFrame:
    threshold_row, topk_row = load_simulation_inputs()

    rows = [
        calculate_business_values(
            scenario="Threshold 0.40",
            operating_setup="Score threshold >= 0.40",
            selected_customers=int(threshold_row["true_positives"] + threshold_row["false_positives"]),
            observed_churners_captured=int(threshold_row["true_positives"]),
        ),
        calculate_business_values(
            scenario="Top 10% targeting",
            operating_setup="Highest-risk 10% of customers",
            selected_customers=int(topk_row["selected_count"]),
            observed_churners_captured=int(topk_row["churners_captured"]),
        ),
    ]

    return pd.DataFrame(rows)


def format_number(value: float) -> str:
    if float(value).is_integer():
        return f"{value:,.0f}"
    return f"{value:,.2f}"


def format_money(value: float) -> str:
    return f"${value:,.2f}"


def simulation_to_markdown(simulation_df: pd.DataFrame) -> str:
    display_df = simulation_df.copy()
    display_df["campaign_cost"] = display_df["campaign_cost"].map(format_money)
    display_df["expected_retained_value"] = display_df["expected_retained_value"].map(format_money)
    display_df["expected_net_value"] = display_df["expected_net_value"].map(format_money)
    display_df["expected_recovered_customers"] = display_df["expected_recovered_customers"].map(format_number)

    columns = [
        "scenario",
        "selected_customers",
        "observed_churners_captured",
        "expected_recovered_customers",
        "campaign_cost",
        "expected_retained_value",
        "expected_net_value",
    ]
    headers = [
        "scenario",
        "selected_customers",
        "observed_churners_captured",
        "expected_recovered_customers",
        "campaign_cost",
        "expected_retained_value",
        "expected_net_value",
    ]

    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in display_df[columns].iterrows():
        lines.append("| " + " | ".join(str(row[column]) for column in columns) + " |")

    return "\n".join(lines)


def write_business_recommendation(simulation_df: pd.DataFrame) -> None:
    primary = simulation_df.sort_values("expected_net_value", ascending=False).iloc[0]
    secondary = simulation_df[simulation_df["scenario"].ne(primary["scenario"])].iloc[0]

    lines = [
        "# Business Recommendation",
        "",
        "## Assumptions",
        "",
        f"- Outreach cost per customer: ${OUTREACH_COST_PER_CUSTOMER}",
        f"- Save success rate among observed churners contacted: {SAVE_SUCCESS_RATE:.0%}",
        f"- Retained value per recovered customer: ${RETAINED_VALUE_PER_RECOVERED_CUSTOMER}",
        "- Inputs reuse `outputs/metrics/threshold_comparison.csv` and `outputs/metrics/topk_comparison.csv`.",
        "",
        "## Scenarios",
        "",
        simulation_to_markdown(simulation_df),
        "",
        "## Recommended Operating Setup",
        "",
        (
            f"Primary recommendation: use `{primary['scenario']}`. It has the higher expected net value "
            f"({format_money(primary['expected_net_value'])}) and captures more observed churners "
            f"({int(primary['observed_churners_captured'])}) under the stated assumptions."
        ),
        "",
        (
            f"Secondary option: use `{secondary['scenario']}` when campaign capacity or budget is tighter. "
            f"It contacts fewer customers ({int(secondary['selected_customers'])}) and has lower total campaign "
            f"cost ({format_money(secondary['campaign_cost'])}), but it also produces a lower expected net value "
            f"({format_money(secondary['expected_net_value'])})."
        ),
        "",
        "## Business Trade-Offs",
        "",
        (
            "The threshold setup reaches a larger group, so it costs more to operate but recovers more expected "
            "customers and produces the stronger expected net value in this scenario."
        ),
        "",
        (
            "The top 10% setup is easier to use as a fixed-capacity campaign list. It is the cleaner choice when "
            "the retention team can only contact a small number of high-risk customers."
        ),
        "",
        (
            "These are scenario-based estimates from held-out model results. They are not observed causal outcomes "
            "from an experiment, so the next business validation step should be a controlled campaign or A/B test."
        ),
    ]

    RECOMMENDATION_OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    simulation_df = build_simulation()
    simulation_df.to_csv(SIMULATION_OUTPUT_PATH, index=False)
    write_business_recommendation(simulation_df)

    print("Retention simulation completed.")
    print(f"Simulation CSV: {SIMULATION_OUTPUT_PATH.relative_to(PROJECT_ROOT)}")
    print(f"Recommendation: {RECOMMENDATION_OUTPUT_PATH.relative_to(PROJECT_ROOT)}")
    print(simulation_df.to_string(index=False))


if __name__ == "__main__":
    main()
