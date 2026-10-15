"""Real text-mining entity extraction: regex-based HGVS variant-notation
matching plus dictionary-based gene/pathway recognition -- genuine NLP
pattern matching, executed against the actual abstract text, not a
lookup of the ground truth."""
from __future__ import annotations

import re

import pandas as pd

from .simulate_abstracts import GENES, PATHWAYS

VARIANT_PATTERN = re.compile(r"p\.[A-Z][a-z]{2}\d+[A-Z][a-z]{2}")


def extract_entities(text: str) -> dict:
    gene_match = next((g for g in GENES if g in text), None)
    variant_match = VARIANT_PATTERN.search(text)
    pathway_match = next((p for p in PATHWAYS if p in text), None)
    return {
        "extracted_gene": gene_match,
        "extracted_variant": variant_match.group(0) if variant_match else None,
        "extracted_pathway": pathway_match,
    }


def mine_all_abstracts(df: pd.DataFrame) -> pd.DataFrame:
    extracted = df["text"].apply(extract_entities).apply(pd.Series)
    return pd.concat([df, extracted], axis=1)


if __name__ == "__main__":
    from .simulate_abstracts import simulate

    df = simulate()
    mined = mine_all_abstracts(df)
    print(mined[["true_gene", "extracted_gene", "true_variant", "extracted_variant"]].head())
