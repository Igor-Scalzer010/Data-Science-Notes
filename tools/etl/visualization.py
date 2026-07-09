"""Visualization helpers for exploratory data analysis."""

from typing import Literal, Optional

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import pandas as pd



def plot_histogram(
    dataframe: pd.DataFrame,
    column: str,
    *,
    bins: int = 30,
    figsize: tuple[int, int] = (10, 6),
    color: str = "steelblue",
    edgecolor: Optional[str] = None,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: str = "Frequencia",
    grid: bool = True,
) -> Axes:
    """Generate a histogram for a numeric column."""
    if column not in dataframe.columns:
        raise ValueError(f"Column '{column}' was not found in the DataFrame.")

    series = dataframe[column]
    if not isinstance(series, pd.Series):
        raise TypeError(f"Column '{column}' could not be interpreted as a pandas Series.")

    numeric_series = pd.to_numeric(series, errors="coerce").dropna()
    if numeric_series.empty:
        raise ValueError(f"Column '{column}' does not contain valid numeric values for a histogram.")

    _, axis = plt.subplots(figsize=figsize)
    edgecolor = edgecolor or color
    axis.hist(numeric_series, bins=bins, color=color, edgecolor=edgecolor)
    axis.set_title(title or f"Histograma de {column}")
    axis.set_xlabel(xlabel or column)
    axis.set_ylabel(ylabel)

    if grid:
        axis.grid(alpha=0.3)

    return axis


def plot_boxplot(
    dataframe: pd.DataFrame,
    column: str,
    *,
    figsize: tuple[int, int] = (10, 4),
    color: str = "steelblue",
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    grid: bool = True,
    orientation: Literal["horizontal", "vertical"] = "horizontal"
) -> Axes:
    """Generate a boxplot for a numeric column."""
    if column not in dataframe.columns:
        raise ValueError(f"Column '{column}' was not found in the DataFrame.")

    series = dataframe[column]
    if not isinstance(series, pd.Series):
        raise TypeError(f"Column '{column}' could not be interpreted as a pandas Series.")

    numeric_series = pd.to_numeric(series, errors="coerce").dropna()
    if numeric_series.empty:
        raise ValueError(f"Column '{column}' does not contain valid numeric values for a boxplot.")

    if orientation not in {"horizontal", "vertical"}:
        raise ValueError("orientation must be 'horizontal' or 'vertical'.")

    _, axis = plt.subplots(figsize=figsize)
    axis.boxplot(
        numeric_series,
        vert=orientation == "vertical",
        patch_artist=True,
        boxprops={"facecolor": color, "edgecolor": color},
        whiskerprops={"color": color},
        capprops={"color": color},
        medianprops={"color": "black"},
        flierprops={"markeredgecolor": color},
    )
    axis.set_title(title or f"Boxplot de {column}")

    if orientation == "horizontal":
        axis.set_xlabel(xlabel or column)
        axis.set_ylabel(ylabel or "")
    else:
        axis.set_xlabel(xlabel or "")
        axis.set_ylabel(ylabel or column)

    if grid:
        axis.grid(alpha=0.3)

    return axis
