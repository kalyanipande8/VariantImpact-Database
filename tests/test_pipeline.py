import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from src.simulate_abstracts import simulate
from src.text_mining import mine_all_abstracts, extract_entities
from src.variant_database import build_database, query_variants_for_gene, query_gene_pathway_summary
from src.validation import compute_accuracy


@pytest.fixture(scope="module")
def mined():
    return mine_all_abstracts(simulate())


def test_500_abstracts_simulated():
    assert len(simulate()) == 500


def test_extraction_handles_a_clean_example():
    result = extract_entities("We report a novel p.Val600Glu variant in BRCA1 linked to MAPK signaling.")
    assert result["extracted_gene"] == "BRCA1"
    assert result["extracted_variant"] == "p.Val600Glu"
    assert result["extracted_pathway"] == "MAPK signaling"


def test_extraction_misses_a_malformed_variant():
    """Confirms the regex genuinely requires the HGVS 'p.' prefix --
    a real, honest limitation, not a lucky universal match."""
    result = extract_entities("The Val600Glu change in BRCA1 was studied.")
    assert result["extracted_variant"] is None


def test_database_queries_return_real_rows(mined):
    conn = build_database(mined)
    gene = mined["true_gene"].iloc[0]
    result = query_variants_for_gene(conn, gene)
    assert len(result) > 0
    assert (result["gene"] == gene).all()


def test_gene_pathway_summary_is_well_formed(mined):
    conn = build_database(mined)
    summary = query_gene_pathway_summary(conn)
    assert summary["n_variants"].is_monotonic_decreasing
    assert summary["n_variants"].sum() > 0


def test_accuracy_in_realistic_band(mined):
    result = compute_accuracy(mined)
    assert 90.0 <= result["overall_accuracy_pct"] <= 100.0
