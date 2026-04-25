from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def calculate_binary_metrics(y_true, y_pred, y_proba) -> dict[str, float]:
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "roc_auc": roc_auc_score(y_true, y_proba),
    }


def build_classification_report(y_true, y_pred) -> str:
    return classification_report(
        y_true,
        y_pred,
        target_names=["No churn", "Churn"],
        digits=4,
        zero_division=0,
    )


def build_confusion_matrix(y_true, y_pred) -> pd.DataFrame:
    matrix = confusion_matrix(y_true, y_pred, labels=[0, 1])
    return pd.DataFrame(
        matrix,
        index=["actual_no_churn", "actual_churn"],
        columns=["predicted_no_churn", "predicted_churn"],
    )


def build_prediction_frame(customer_ids, y_true, y_pred, y_proba) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "customer_id": customer_ids.values,
            "actual_churn": y_true.values,
            "predicted_churn": y_pred,
            "churn_probability": y_proba,
        }
    )


def ensure_output_dirs(*paths: Path) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)
