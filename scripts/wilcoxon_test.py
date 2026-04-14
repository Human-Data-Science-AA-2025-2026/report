"""
wilcoxon_test.py
Test primario: il gap (Eurostat - ISTAT) è sistematicamente diverso da zero?
Usa il Wilcoxon signed-rank test (non parametrico, dati appaiati, no assunzione di normalità).

Input:  merged_migration_data.csv
Output: risultati a console + summary DataFrame
"""

import pandas as pd
from scipy.stats import wilcoxon, shapiro
from typing import List, Dict, Any


class MigrationWilcoxonTest:

    def __init__(
        self,
        data_path: str = "../data/merged_migration_data.csv",
        alphas: List[float] = [0.05, 0.01, 0.001],
    ):
        self.df = pd.read_csv(data_path)
        self.df["GAP"] = self.df["DEST_REGISTERED"] - self.df["ISTAT_DELETED"]
        self.alphas = alphas

    def test_global(self) -> Dict[str, Any]:
        """H0: il gap mediano = 0  vs  H1: il gap mediano != 0."""
        gaps = self.df["GAP"].values
        stat, p = wilcoxon(gaps, alternative="two-sided")

        return self._build_result("GLOBAL (tutte le coppie)", gaps, stat, p)

    def test_by_country(self) -> List[Dict[str, Any]]:
        """
        Alternativa robusta al lag: somma i flussi sui 5 anni per paese,
        cosi' lo sfasamento intra-annuale si cancella.
        """
        grouped = (
            self.df.groupby("DESTINATION_STATE")[["ISTAT_DELETED", "DEST_REGISTERED"]]
            .sum()
            .reset_index()
        )
        grouped["GAP"] = grouped["DEST_REGISTERED"] - grouped["ISTAT_DELETED"]
        gaps = grouped["GAP"].values
        stat, p = wilcoxon(gaps, alternative="two-sided")

        return [self._build_result("PER-COUNTRY (totali 5 anni)", gaps, stat, p)]

    def test_normality(self) -> Dict[str, Any]:
        """
        Se p < 0.05 -> i gap NON sono normali -> il t-test non e' appropriato
        -> conferma la scelta del Wilcoxon.
        """
        gaps = self.df["GAP"].values
        stat, p = shapiro(gaps)
        return {
            "test": "Shapiro-Wilk (normalita')",
            "stat": round(stat, 4),
            "p_value": round(p, 6),
            "normal": p >= 0.05,
            "interpretation": (
                "I gap seguono una distribuzione normale (p >= 0.05)"
                if p >= 0.05
                else "I gap NON sono normali (p < 0.05) -> Wilcoxon e' la scelta corretta"
            ),
        }

    def get_summary_df(self) -> pd.DataFrame:
        results = [self.test_global()] + self.test_by_country()
        rows = []
        for r in results:
            row = {
                "Test": r["label"],
                "N": r["n"],
                "Gap mediano": r["median_gap"],
                "W stat": r["stat"],
                "p-value": r["p_value"],
            }
            for a in self.alphas:
                row[f"Rifiuta H0 (a={a})"] = "Si'" if r["decisions"][a] else "No"
            rows.append(row)
        return pd.DataFrame(rows)

    def _build_result(self, label, gaps, stat, p) -> Dict[str, Any]:
        decisions = {a: p < a for a in self.alphas}
        return {
            "label": label,
            "n": len(gaps),
            "stat": round(stat, 3),
            "p_value": round(p, 8),
            "median_gap": round(float(pd.Series(gaps).median()), 1),
            "mean_gap": round(float(pd.Series(gaps).mean()), 1),
            "decisions": decisions,
        }


if __name__ == "__main__":
    import os

    path = os.path.join(os.path.dirname(__file__), "../data/merged_migration_data.csv")
    if not os.path.exists(path):
        print(f"Dataset non trovato: {path}. Eseguire prima make_dataset.py.")
    else:
        tester = MigrationWilcoxonTest(path)

        print("=" * 60)
        print("WILCOXON SIGNED-RANK TEST")
        print("H0: il gap (Eurostat - ISTAT) = 0")
        print("H1: il gap (Eurostat - ISTAT) != 0")
        print("=" * 60)
        print()
        print(tester.get_summary_df().to_string(index=False))
        print()

        norm = tester.test_normality()
        print(f"Shapiro-Wilk: W={norm['stat']}, p={norm['p_value']}")
        print(f"  -> {norm['interpretation']}")
        tester.get_summary_df().to_csv("../data/wilcoxon_results.csv")

