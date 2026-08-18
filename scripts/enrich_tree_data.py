"""Example data-enrichment utility for tree datasets."""
from pathlib import Path

import pandas as pd
from sklearn.impute import SimpleImputer


def enrich(input_path: str, output_path: str) -> None:
    df = pd.read_csv(input_path)

    for column in ["family", "genus", "species"]:
        if column in df:
            df[column] = df[column].ffill().bfill()

    if {"latitude", "longitude"}.issubset(df.columns):
        df["latitude"] = df["latitude"].fillna(df["latitude"].mean())
        df["longitude"] = df["longitude"].fillna(df["longitude"].mean())

    numeric = df.select_dtypes(include="number").columns
    if len(numeric):
        imputer = SimpleImputer(strategy="mean")
        df[numeric] = imputer.fit_transform(df[numeric])

    df.to_csv(output_path, index=False)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    enrich(str(root / "data" / "trees.csv"), str(root / "data" / "enriched_trees.csv"))
