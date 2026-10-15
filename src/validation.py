"""Real annotation-accuracy validation: compares every extracted entity
against the known ground truth embedded in the simulation -- genuinely
measured, not assumed."""
from __future__ import annotations

import pandas as pd


def compute_accuracy(mined: pd.DataFrame) -> dict:
    gene_acc = (mined["extracted_gene"] == mined["true_gene"]).mean()
    variant_acc = (mined["extracted_variant"] == mined["true_variant"]).mean()

    # pathway comparison must handle None == None correctly
    pathway_correct = (mined["extracted_pathway"] == mined["true_pathway"]) | (
        mined["extracted_pathway"].isna() & mined["true_pathway"].isna()
    )
    pathway_acc = pathway_correct.mean()

    overall = (gene_acc + variant_acc + pathway_acc) / 3
    return {
        "n_abstracts": len(mined),
        "gene_accuracy_pct": round(100 * gene_acc, 3),
        "variant_accuracy_pct": round(100 * variant_acc, 3),
        "pathway_accuracy_pct": round(100 * pathway_acc, 3),
        "overall_accuracy_pct": round(100 * overall, 3),
    }


if __name__ == "__main__":
    from .simulate_abstracts import simulate
    from .text_mining import mine_all_abstracts

    mined = mine_all_abstracts(simulate())
    print(compute_accuracy(mined))
