from __future__ import annotations

from pathlib import Path
import re
from typing import Dict, List

from datasets import load_dataset
import pandas as pd

from ..config import settings

DATASET_NAME = "ManikaSaini/zomato-restaurant-recommendation"
REQUIRED_COLUMNS = ["name", "location", "cuisine", "avg_cost", "rating", "cost"]

SOURCE_COLUMN_ALIASES: Dict[str, List[str]] = {
    "name": ["restaurant name", "name", "restaurant", "res_name"],
    "location": ["location", "city", "area", "address"],
    "cuisine": ["cuisine", "cuisines", "food_type"],
    "avg_cost": [
        "average cost",
        "average cost for two",
        "avg_cost",
        "cost for two",
        "cost",
        "approx cost for two people",
    ],
    "rating": ["rating", "aggregate rating", "user rating", "rate"],
}


def _normalize_column_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value).strip().lower()).strip()


def _match_source_column(columns: List[str], aliases: List[str]) -> str | None:
    normalized = {_normalize_column_name(col): col for col in columns}
    for alias in aliases:
        alias_key = _normalize_column_name(alias)
        if alias_key in normalized:
            return normalized[alias_key]
    return None


def _extract_numeric_cost(raw_value: object) -> float | None:
    if raw_value is None:
        return None
    if isinstance(raw_value, (int, float)):
        return float(raw_value)

    text = str(raw_value).replace(",", "")
    matches = re.findall(r"\d+\.?\d*", text)
    if not matches:
        return None
    return float(matches[0])


def _cost_to_budget(avg_cost: float) -> str:
    if avg_cost <= 500:
        return "low"
    if avg_cost <= 1500:
        return "medium"
    return "high"


def _standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map: Dict[str, str] = {}
    for target, aliases in SOURCE_COLUMN_ALIASES.items():
        source = _match_source_column(df.columns.tolist(), aliases)
        if source:
            rename_map[source] = target
    return df.rename(columns=rename_map)


def load_raw_dataset() -> pd.DataFrame:
    dataset = load_dataset(DATASET_NAME, split="train")
    # Take a healthy sample of 5,000 rows to prevent PyArrow OOM errors on local machines
    return dataset.select(range(min(5000, len(dataset)))).to_pandas()


def clean_and_preprocess(df: pd.DataFrame) -> pd.DataFrame:
    standardized = _standardize_columns(df)
    for required in ["name", "location", "cuisine", "avg_cost", "rating"]:
        if required not in standardized.columns:
            raise ValueError(f"Required column missing after mapping: {required}")

    processed = standardized.copy()
    processed["name"] = processed["name"].astype(str).str.strip()
    processed["location"] = processed["location"].astype(str).str.strip().str.lower()
    processed["cuisine"] = processed["cuisine"].astype(str).str.strip().str.lower()
    
    # Handle rating strings like '4.1/5' or 'NEW'
    processed["rating"] = processed["rating"].astype(str).str.split('/').str[0].str.strip()
    processed["rating"] = pd.to_numeric(processed["rating"], errors="coerce")
    
    processed["avg_cost"] = processed["avg_cost"].apply(_extract_numeric_cost)

    processed = processed.dropna(subset=["name", "location", "cuisine", "rating", "avg_cost"])
    processed = processed[processed["rating"].between(0, 5)]
    processed = processed[processed["avg_cost"] > 0]
    processed["rating"] = processed["rating"].round(1)
    processed["avg_cost"] = processed["avg_cost"].round(0).astype(int)
    processed["cost"] = processed["avg_cost"].apply(_cost_to_budget)

    return processed[REQUIRED_COLUMNS].drop_duplicates().reset_index(drop=True)


def save_processed_dataset(df: pd.DataFrame, path: str) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)


def load_processed_dataset(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def get_processed_restaurants(force_refresh: bool = False) -> pd.DataFrame:
    cache_path = Path(settings.DATA_CACHE_PATH)
    if cache_path.exists() and not force_refresh:
        return load_processed_dataset(str(cache_path))

    raw_df = load_raw_dataset()
    processed_df = clean_and_preprocess(raw_df)
    save_processed_dataset(processed_df, str(cache_path))
    return processed_df
