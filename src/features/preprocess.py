from __future__ import annotations

from typing import Tuple

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


TARGET_COLUMN = "churn"
ID_COLUMN = "customer_id"
POSITIVE_CLASS = "Yes"
NEGATIVE_CLASS = "No"


def validate_model_dataset(df: pd.DataFrame) -> None:
    required_columns = {ID_COLUMN, TARGET_COLUMN}
    missing_columns = sorted(required_columns - set(df.columns))
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    expected_target_values = {NEGATIVE_CLASS, POSITIVE_CLASS}
    actual_target_values = set(df[TARGET_COLUMN].dropna().unique())
    unexpected_values = sorted(actual_target_values - expected_target_values)
    if unexpected_values:
        raise ValueError(f"Unexpected churn values: {unexpected_values}")


def split_features_target(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, pd.Series]:
    validate_model_dataset(df)

    X = df.drop(columns=[ID_COLUMN, TARGET_COLUMN])
    y = df[TARGET_COLUMN].map({NEGATIVE_CLASS: 0, POSITIVE_CLASS: 1}).astype(int)
    customer_ids = df[ID_COLUMN].copy()

    return X, y, customer_ids


def get_feature_columns(X: pd.DataFrame) -> tuple[list[str], list[str]]:
    numeric_features = X.select_dtypes(include=["number"]).columns.tolist()
    categorical_features = X.select_dtypes(exclude=["number"]).columns.tolist()

    return numeric_features, categorical_features


def build_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    numeric_features, categorical_features = get_feature_columns(X)

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric_features),
            ("categorical", categorical_pipeline, categorical_features),
        ]
    )
