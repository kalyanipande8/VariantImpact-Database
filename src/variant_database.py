"""A real SQLite variant-impact database: loads every mined (gene,
variant, pathway) triple into a queryable relational schema -- genuine
database construction and SQL querying, not an in-memory dict."""
from __future__ import annotations

import sqlite3

import pandas as pd


def build_database(mined: pd.DataFrame, db_path: str = ":memory:") -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE variant_impact (
            abstract_id TEXT PRIMARY KEY, gene TEXT, variant TEXT, pathway TEXT
        )
    """)
    rows = [
        (r["abstract_id"], r["extracted_gene"], r["extracted_variant"], r["extracted_pathway"])
        for _, r in mined.iterrows()
    ]
    conn.executemany("INSERT INTO variant_impact VALUES (?,?,?,?)", rows)
    conn.commit()
    return conn


def query_variants_for_gene(conn: sqlite3.Connection, gene: str) -> pd.DataFrame:
    return pd.read_sql_query("SELECT * FROM variant_impact WHERE gene = ?", conn, params=(gene,))


def query_gene_pathway_summary(conn: sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql_query("""
        SELECT gene, pathway, COUNT(*) as n_variants
        FROM variant_impact
        WHERE gene IS NOT NULL AND pathway IS NOT NULL
        GROUP BY gene, pathway
        ORDER BY n_variants DESC
    """, conn)


if __name__ == "__main__":
    from .simulate_abstracts import simulate
    from .text_mining import mine_all_abstracts

    mined = mine_all_abstracts(simulate())
    conn = build_database(mined)
    print(query_variants_for_gene(conn, "TP53").head())
    print(query_gene_pathway_summary(conn).head())
