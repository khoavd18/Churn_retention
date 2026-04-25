from __future__ import annotations

import math
import sys
from pathlib import Path

import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.features.preprocess import split_features_target
from src.models.evaluate import ensure_output_dirs
from src.models.train_compare_models import (
    METRICS_DIR,
    RANDOM_STATE,
    TEST_SIZE,
    build_pipeline,
    dataframe_to_markdown,
    load_data,
)


THRESHOLDS = [0.20, 0.25, 0.30, 0.35, 0.40, 0.50]
TOP_K_LEVELS = [0.05, 0.10, 0.20]


def build_finalist_configs() -> dict[str, object]:
    return {
        "LogisticRegression": LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
        "GradientBoostingClassifier": GradientBoostingClassifier(random_state=RANDOM_STATE),
    }


def calculate_threshold_row(model_name: str, threshold: float, y_true, y_proba) -> dict[str, object]:
    y_pred = (y_proba >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()

    return {
        "model": model_name,
        "threshold": threshold,
        "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 6),
        "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 6),
        "f1": round(float(f1_score(y_true, y_pred, zero_division=0)), 6),
        "predicted_positive_rate": round(float(y_pred.mean()), 6),
        "true_positives": int(tp),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "true_negatives": int(tn),
    }


def calculate_topk_row(model_name: str, top_k: float, y_true: pd.Series, y_proba) -> dict[str, object]:
    selected_count = math.ceil(len(y_true) * top_k)
    scored = pd.DataFrame({"actual_churn": y_true.values, "churn_probability": y_proba})
    selected = scored.sort_values("churn_probability", ascending=False).head(selected_count)

    churners_captured = int(selected["actual_churn"].sum())
    total_churners = int(scored["actual_churn"].sum())

    return {
        "model": model_name,
        "top_k": top_k,
        "selected_count": int(selected_count),
        "churners_captured": churners_captured,
        "precision_at_k": round(float(churners_captured / selected_count), 6),
        "recall_at_k": round(float(churners_captured / total_churners), 6),
    }


def select_best_threshold_candidates(threshold_df: pd.DataFrame) -> pd.DataFrame:
    candidates = []

    for model_name, model_df in threshold_df.groupby("model"):
        best_f1 = model_df.sort_values(["f1", "recall"], ascending=False).iloc[0].copy()
        best_f1["selection_reason"] = "best_f1_for_model"
        candidates.append(best_f1)

        highest_recall = model_df.sort_values(["recall", "precision"], ascending=False).iloc[0].copy()
        highest_recall["selection_reason"] = "highest_recall_for_model"
        candidates.append(highest_recall)

    candidate_df = pd.DataFrame(candidates).drop_duplicates(["model", "threshold", "selection_reason"])
    return candidate_df.sort_values(["selection_reason", "model"])


def select_best_topk_candidates(topk_df: pd.DataFrame) -> pd.DataFrame:
    return (
        topk_df.sort_values(["recall_at_k", "precision_at_k"], ascending=False)
        .groupby("top_k", as_index=False)
        .head(1)
        .sort_values("top_k")
    )


def write_summary(threshold_df: pd.DataFrame, topk_df: pd.DataFrame, output_path: Path) -> None:
    best_threshold_candidates = select_best_threshold_candidates(threshold_df)
    best_topk_candidates = select_best_topk_candidates(topk_df)

    recommended_threshold = (
        threshold_df.query("predicted_positive_rate <= 0.40")
        .sort_values(["recall", "f1"], ascending=False)
        .iloc[0]
    )
    recommended_topk = topk_df[topk_df["top_k"].eq(0.20)].sort_values(["recall_at_k", "precision_at_k"], ascending=False).iloc[0]

    lines = [
        "# Threshold Tuning Summary",
        "",
        "Dataset: `data/processed/model_dataset.csv`",
        f"Split: same stratified train/test split as prior modeling, test_size={TEST_SIZE}, random_state={RANDOM_STATE}",
        "",
        "This step evaluates business-friendly operating points for the two finalist models. "
        "No hyperparameter tuning was performed.",
        "",
        "## Best Threshold Candidates",
        "",
        dataframe_to_markdown(best_threshold_candidates),
        "",
        "## Best Top-K Candidates",
        "",
        dataframe_to_markdown(best_topk_candidates),
        "",
        "## Recommendation",
        "",
        (
            f"For a recall-sensitive retention program, start with `{recommended_threshold['model']}` at a "
            f"{recommended_threshold['threshold']:.2f} threshold. This captures "
            f"{int(recommended_threshold['true_positives'])} churners out of "
            f"{int(recommended_threshold['true_positives'] + recommended_threshold['false_negatives'])} "
            f"on the test set, with recall {recommended_threshold['recall']:.3f}, precision "
            f"{recommended_threshold['precision']:.3f}, and a predicted positive rate of "
            f"{recommended_threshold['predicted_positive_rate']:.3f}."
        ),
        "",
        (
            f"If the business prefers a fixed contact list, use the top 20% list from "
            f"`{recommended_topk['model']}`. It selects {int(recommended_topk['selected_count'])} customers "
            f"and captures {int(recommended_topk['churners_captured'])} churners, with precision@k "
            f"{recommended_topk['precision_at_k']:.3f} and recall@k {recommended_topk['recall_at_k']:.3f}."
        ),
        "",
        "## Trade-Off",
        "",
        "Lowering the threshold catches more likely churners, which is useful for retention, but it also increases "
        "false positives and the number of customers the business must contact. Top-k targeting is easier to align "
        "with campaign capacity, but it may miss churners outside the selected group. The right operating point "
        "depends on retention team capacity, contact cost, offer cost, and the value of saving a customer.",
    ]

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ensure_output_dirs(METRICS_DIR)

    df = load_data()
    X, y, customer_ids = split_features_target(df)

    X_train, X_test, y_train, y_test, _customer_ids_train, _customer_ids_test = train_test_split(
        X,
        y,
        customer_ids,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    threshold_rows = []
    topk_rows = []

    for model_name, estimator in build_finalist_configs().items():
        pipeline = build_pipeline(X_train, estimator)
        pipeline.fit(X_train, y_train)
        y_proba = pipeline.predict_proba(X_test)[:, 1]

        for threshold in THRESHOLDS:
            threshold_rows.append(calculate_threshold_row(model_name, threshold, y_test, y_proba))

        for top_k in TOP_K_LEVELS:
            topk_rows.append(calculate_topk_row(model_name, top_k, y_test, y_proba))

    threshold_df = pd.DataFrame(threshold_rows)
    threshold_path = METRICS_DIR / "threshold_comparison.csv"
    threshold_df.to_csv(threshold_path, index=False)

    topk_df = pd.DataFrame(topk_rows)
    topk_path = METRICS_DIR / "topk_comparison.csv"
    topk_df.to_csv(topk_path, index=False)

    summary_path = METRICS_DIR / "threshold_summary.md"
    write_summary(threshold_df, topk_df, summary_path)

    print("Threshold tuning completed.")
    print(f"Threshold comparison: {threshold_path.relative_to(PROJECT_ROOT)}")
    print(f"Top-k comparison: {topk_path.relative_to(PROJECT_ROOT)}")
    print(f"Summary: {summary_path.relative_to(PROJECT_ROOT)}")
    print("\nThreshold comparison:")
    print(threshold_df.to_string(index=False))
    print("\nTop-k comparison:")
    print(topk_df.to_string(index=False))


if __name__ == "__main__":
    main()
