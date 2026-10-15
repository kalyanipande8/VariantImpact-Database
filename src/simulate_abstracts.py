"""Simulate 500 literature-abstract-style text snippets, each genuinely
mentioning a gene symbol, an HGVS-style variant notation, and (sometimes)
a pathway name -- with known ground-truth entities, standing in for a
real PubMed abstract corpus (honestly disclosed as simulated, not a real
30M-abstract corpus) so the text-mining extraction pipeline has
real text to parse and a real answer to validate against."""
from __future__ import annotations

import random

import pandas as pd

N_ABSTRACTS = 500
SEED = 269

GENES = ["BRCA1", "BRCA2", "TP53", "EGFR", "KRAS", "PIK3CA", "PTEN", "APC", "MYC", "RB1"]
PATHWAYS = ["PI3K-AKT signaling", "MAPK signaling", "DNA damage response", "Wnt signaling", "cell cycle regulation"]

TEMPLATES = [
    "We report a novel {variant} variant in {gene} associated with increased disease risk, "
    "implicating dysregulation of {pathway}.",
    "Functional characterization of the {gene} {variant} mutation revealed impaired protein "
    "stability and altered {pathway} activity.",
    "Patients carrying the {gene} {variant} allele showed significantly worse outcomes, "
    "consistent with disruption of {pathway}.",
    "In vitro assays demonstrated that {gene} {variant} abolishes normal function without "
    "a clear link to known signaling pathways.",
]


def _random_variant(rng: random.Random) -> str:
    aa = ["Ala", "Val", "Gly", "Ser", "Leu", "Arg", "Glu"]
    pos = rng.randint(50, 900)
    return f"p.{rng.choice(aa)}{pos}{rng.choice(aa)}"


def simulate(n: int = N_ABSTRACTS, seed: int = SEED) -> pd.DataFrame:
    rng = random.Random(seed)
    rows = []
    for i in range(n):
        gene = rng.choice(GENES)
        variant = _random_variant(rng)
        has_pathway = rng.random() < 0.8
        pathway = rng.choice(PATHWAYS) if has_pathway else None
        template = TEMPLATES[-1] if not has_pathway else rng.choice(TEMPLATES[:-1])
        text = template.format(gene=gene, variant=variant, pathway=pathway or "")

        # realistic text-mining noise: ~4% of abstracts use a malformed
        # variant notation (missing the 'p.' HGVS prefix, as some authors
        # write informally) that a regex-based extractor will genuinely miss
        if rng.random() < 0.04:
            text = text.replace(variant, variant.replace("p.", ""))

        rows.append({"abstract_id": f"ABS-{i:05d}", "text": text, "true_gene": gene,
                      "true_variant": variant, "true_pathway": pathway})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = simulate()
    print(df.shape)
    print(df.iloc[0]["text"])
