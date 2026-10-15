"""End-to-end: simulate abstracts, mine entities, build the variant
database, query it, and validate annotation accuracy."""
import json
import os

from src.simulate_abstracts import simulate
from src.text_mining import mine_all_abstracts
from src.variant_database import build_database, query_variants_for_gene, query_gene_pathway_summary
from src.validation import compute_accuracy

os.makedirs("data", exist_ok=True)
os.makedirs("results", exist_ok=True)

print("=== Simulating 500 literature abstracts ===")
abstracts = simulate()
abstracts.to_csv("data/abstracts.csv", index=False)
print(abstracts.shape)

print("\n=== Mining entities (gene, variant, pathway) ===")
mined = mine_all_abstracts(abstracts)
mined.to_csv("data/mined_entities.csv", index=False)

print("\n=== Building variant-impact SQLite database ===")
conn = build_database(mined)
summary_table = query_gene_pathway_summary(conn)
print(summary_table.head(10))
summary_table.to_csv("results/gene_pathway_summary.csv", index=False)

print("\n=== Validating annotation accuracy ===")
accuracy = compute_accuracy(mined)
print(accuracy)

summary = {
    "n_abstracts": accuracy["n_abstracts"],
    "n_gene_pathway_pairs": len(summary_table),
    "gene_accuracy_pct": accuracy["gene_accuracy_pct"],
    "variant_accuracy_pct": accuracy["variant_accuracy_pct"],
    "pathway_accuracy_pct": accuracy["pathway_accuracy_pct"],
    "overall_accuracy_pct": accuracy["overall_accuracy_pct"],
}
with open("results/summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print("\n=== Summary ===")
print(json.dumps(summary, indent=2))
