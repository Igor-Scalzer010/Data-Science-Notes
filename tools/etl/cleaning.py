"""Reusable ETL helpers for basic DataFrame cleaning."""

import re
import unicodedata
from typing import Iterable, Optional

import pandas as pd


def _normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return normalized.encode("ascii", "ignore").decode("utf-8")


def standardize_column_name(column_name: object) -> str:
    """Convert a column name to snake_case ASCII."""
    column = _normalize_text(str(column_name).strip()).lower()
    column = re.sub(r"[^\w]+", "_", column)
    column = re.sub(r"_+", "_", column)
    return column.strip("_")


def standardize_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with normalized snake_case column names."""
    df = dataframe.copy()
    df.columns = [standardize_column_name(column) for column in df.columns]
    return df


def standardize_text_columns(
    dataframe: pd.DataFrame,
    columns: Optional[Iterable[str]] = None,
    *,
    lowercase: bool = True,
) -> pd.DataFrame:
    """Trim whitespace and normalize text values for selected columns."""
    df = dataframe.copy()
    target_columns = list(columns) if columns is not None else list(df.select_dtypes(include=["object", "string"]).columns)

    for column in target_columns:
        if column not in df.columns:
            continue

        series = df[column]
        if not isinstance(series, pd.Series):
            continue

        df[column] = series.map(
            lambda value: _standardize_value(value, lowercase=lowercase)
        )

    return df


def _standardize_value(value: object, *, lowercase: bool) -> object:
    if not isinstance(value, str):
        return value

    clean_value = _normalize_text(value).strip()
    clean_value = re.sub(r"\s+", " ", clean_value)

    if lowercase:
        clean_value = clean_value.lower()

    return clean_value


def normalize_missing_values(
    dataframe: pd.DataFrame,
    missing_tokens: Optional[Iterable[str]] = None,
) -> pd.DataFrame:
    """Replace common textual missing markers with pandas NA."""
    df = dataframe.copy()
    tokens = list(missing_tokens) if missing_tokens is not None else [
        "",
        " ",
        "nan",
        "null",
        "none",
        "na",
        "n/a",
        "não informado",
        "nao informado",
    ]

    normalized_tokens = {_standardize_value(token, lowercase=True) for token in tokens}

    object_columns = df.select_dtypes(include=["object", "string"]).columns
    for column in object_columns:
        series = df[column]
        if not isinstance(series, pd.Series):
            continue

        df[column] = series.apply(
            lambda value: pd.NA
            if isinstance(value, str)
            and _standardize_value(value, lowercase=True) in normalized_tokens
            else value
        )

    return df


def coerce_numeric_columns(
    dataframe: pd.DataFrame,
    columns: Iterable[str],
) -> pd.DataFrame:
    """Convert selected columns to numeric dtype."""
    df = dataframe.copy()

    for column in columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    return df


def coerce_datetime_columns(
    dataframe: pd.DataFrame,
    columns: Iterable[str],
    *,
    dayfirst: bool = False,
) -> pd.DataFrame:
    """Convert selected columns to datetime dtype and reset time to midnight."""
    df = dataframe.copy()

    for column in columns:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors="coerce", dayfirst=dayfirst).dt.normalize()

    return df


def standardize_dataframe(
    dataframe: pd.DataFrame,
    *,
    text_columns: Optional[Iterable[str]] = None,
    numeric_columns: Optional[Iterable[str]] = None,
    datetime_columns: Optional[Iterable[str]] = None,
    lowercase_text: bool = True,
    drop_duplicates: bool = True,
) -> pd.DataFrame:
    """Run a basic ETL cleaning pipeline for a DataFrame."""
    df = standardize_columns(dataframe)
    df = standardize_text_columns(df, columns=text_columns, lowercase=lowercase_text)
    df = normalize_missing_values(df)

    if numeric_columns is not None:
        df = coerce_numeric_columns(df, numeric_columns)

    if datetime_columns is not None:
        df = coerce_datetime_columns(df, datetime_columns)

    if drop_duplicates:
        df = df.drop_duplicates()

    return df

