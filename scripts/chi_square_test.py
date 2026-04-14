import pandas as pd
from scipy.stats import chisquare, chi2
import matplotlib.pyplot as plt
from typing import List, Dict, Any

class MigrationChiSquareTest:
    """
    Suite per eseguire il test del Chi Quadrato sui dati di migrazione.
    Confronta le frequenze osservate (ISTAT) con quelle attese (modello Eurostat).
    """
    def __init__(self, data_path: str = "../data/merged_migration_data.csv", alphas: List[float] = [0.05, 0.01, 0.001]):
        self.df = pd.read_csv(data_path)
        self.alphas = alphas
        
    def get_country_data(self, country_code: str) -> pd.DataFrame:
        """Ritorna i dati filtrati e ordinati per un singolo paese."""
        return self.df[self.df['DESTINATION_STATE'] == country_code].sort_values('YEAR')

    def perform_test(self, label: str, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Esegue il test del Chi Quadrato su un set di dati (paese o totale).
        """
        if data.empty:
            raise ValueError(f"Nessun dato trovato per: {label}")
            
        observed = data['ISTAT_DELETED'].values
        eurostat_totals = data['DEST_REGISTERED'].values
        
        # Frequenze Attese (E_i)
        eurostat_dist = eurostat_totals / eurostat_totals.sum()
        istat_total = observed.sum()
        expected = istat_total * eurostat_dist
        
        # Esecuzione del test
        chi2_stat, p_value = chisquare(f_obs=observed, f_exp=expected)
        
        # Gradi di libertà
        dof = len(observed) - 1
        
        # Decisioni per diversi livelli di alfa
        decisions = {}
        for a in self.alphas:
            critical_value = chi2.ppf(1 - a, dof)
            decisions[a] = chi2_stat > critical_value
        
        return {
            'label': label,
            'chi2_stat': chi2_stat,
            'p_value': p_value,
            'dof': dof,
            'decisions': decisions,
            'observed': observed.tolist(),
            'expected': expected.tolist(),
            'years': data['YEAR'].tolist()
        }

    def test_all_countries(self) -> List[Dict[str, Any]]:
        """Esegue il test per ogni paese."""
        countries = sorted(self.df['DESTINATION_STATE'].unique())
        results = []
        
        # Test per singolo paese
        for c in countries:
            results.append(self.perform_test(c, self.get_country_data(c)))
            
        return results

    def get_summary_df(self) -> pd.DataFrame:
        """Ritorna un DataFrame riassuntivo dei risultati."""
        results = self.test_all_countries()
        summary = []
        for r in results:
            row = {
                'Entità': r['label'],
                'Chi2 Stat': round(r['chi2_stat'], 3),
                'p-value': round(r['p_value'], 6),
            }
            # Aggiunge colonne per ogni alpha
            for a in self.alphas:
                row[f'Rifiuta H0 (α={a})'] = 'Sì' if r['decisions'][a] else 'No'
            summary.append(row)
        return pd.DataFrame(summary)

if __name__ == "__main__":
    import os
    # Path relativo corretto per esecuzione da scripts/
    path = os.path.join(os.path.dirname(__file__), "../data/merged_migration_data.csv")
    if not os.path.exists(path):
        print(f"Dataset non trovato: {path}. Eseguire prima make_dataset.py.")
    else:
        tester = MigrationChiSquareTest(path)
        print(tester.get_summary_df().to_string(index=False))
