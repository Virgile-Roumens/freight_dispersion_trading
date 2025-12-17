"""
SignalGenerator Class - Feature Engineering et Signaux de Trading

Responsabilités:
- Normaliser les données (z-scores)
- Classifier en régimes (quartiles)
- Générer 2 signaux simples et économiquement justifiés
- Fournir explications pour chaque signal

Context Économique:
Signal 1 (Momentum): Changements à court terme de dispersion
Signal 2 (Regime): État structurel du marché (quartiles)
"""

import pandas as pd
import numpy as np
from typing import Dict, List


class SignalGenerator:
    """
    Génère les signaux de trading à partir des données propres.
    
    Attributes:
        data (pd.DataFrame): Données propres de DataManager
        features (pd.DataFrame): Features calculées + signaux
        signal_explanations (dict): Explications économiques des signaux
    """
    
    def __init__(self, clean_data: pd.DataFrame, verbose: bool = True):
        """
        Initialiser SignalGenerator.
        
        Args:
            clean_data: Sortie de DataManager.get_clean_data()
            verbose: Afficher les logs
        """
        self.data = clean_data.copy()
        self.features = None
        self.verbose = verbose
        
        # Explications des signaux
        self.signal_explanations = {
            'momentum': {
                'description': '📈 Signal de Momentum Dispersion',
                'logic': 'LONG si changement 5j > 0; SHORT si < 0; FLAT sinon',
                'economic_meaning': (
                    'La dispersion qui augmente suggère une meilleure répartition '
                    'des bateaux = demande en hausse = potentiellement prix plus hauts. '
                    'L\'inverse indique une consolidation = demande affaiblie.'
                ),
                'signal_type': 'Technique/Comportemental',
                'horizon': '5-20 jours',
                'rationale': 'Les changements de dispersion précèdent les mouvements de prix'
            },
            'regime': {
                'description': '🎯 Signal de Regime (Quartiles)',
                'logic': 'LONG en Q3-Q4 (haute); SHORT en Q1 (basse); FLAT en Q2',
                'economic_meaning': (
                    'Les périodes de haute dispersion (Q3-Q4) reflètent un marché '
                    'structurellement sain avec ~41% de prime vs Q1. '
                    'Cela capture l\'état structurel, pas un timing fin.'
                ),
                'signal_type': 'Structurel/Fondamental',
                'horizon': 'Multi-semaines',
                'rationale': 'Capture l\'état de l\'équilibre offre/demande global'
            }
        }
        
        # Calculer
        self._compute_features()
        self._generate_signals()
    
    def _compute_features(self) -> None:
        """Calculer toutes les features (z-scores, quartiles, momentum)."""
        try:
            self.features = self.data.copy()
            window = 60  # Fenêtre rolling
            
            # Z-scores dispersion moyenne
            self.features['avg_disp_mean_60d'] = (
                self.features['avg_dispersion'].rolling(window).mean()
            )
            self.features['avg_disp_std_60d'] = (
                self.features['avg_dispersion'].rolling(window).std()
            )
            self.features['avg_disp_zscore'] = (
                (self.features['avg_dispersion'] - 
                 self.features['avg_disp_mean_60d']) /
                self.features['avg_disp_std_60d']
            )
            
            # Z-scores Capesize
            self.features['cape_disp_zscore'] = (
                (self.features['cape_dispersion'] - 
                 self.features['cape_dispersion'].rolling(window).mean()) /
                self.features['cape_dispersion'].rolling(window).std()
            )
            
            # Z-scores VLOC
            self.features['vloc_disp_zscore'] = (
                (self.features['vloc_dispersion'] - 
                 self.features['vloc_dispersion'].rolling(window).mean()) /
                self.features['vloc_dispersion'].rolling(window).std()
            )
            
            # Z-scores prix
            self.features['price_mean_60d'] = (
                self.features['price_5tc'].rolling(window).mean()
            )
            self.features['price_std_60d'] = (
                self.features['price_5tc'].rolling(window).std()
            )
            self.features['price_zscore'] = (
                (self.features['price_5tc'] - 
                 self.features['price_mean_60d']) /
                self.features['price_std_60d']
            )
            
            # Quartiles de dispersion (régimes)
            self.features['disp_quartile'] = pd.qcut(
                self.features['avg_dispersion'],
                q=4,
                labels=['Q1_Bas', 'Q2_Moyen_Bas', 'Q3_Moyen_Haut', 'Q4_Haut'],
                duplicates='drop'
            )
            
            # Momentum normalisé
            disp_change_mean = (
                self.features['avg_disp_change_5d'].rolling(window).mean()
            )
            disp_change_std = (
                self.features['avg_disp_change_5d'].rolling(window).std()
            )
            self.features['momentum_zscore'] = (
                (self.features['avg_disp_change_5d'] - disp_change_mean) / 
                disp_change_std
            )
            
            if self.verbose:
                print("✓ Features calculées (z-scores, quartiles, momentum)")
        except Exception as e:
            print(f"✗ Erreur computation features: {e}")
            raise
    
    def _generate_signals(self) -> None:
        """Générer les 2 signaux simples."""
        try:
            # SIGNAL 1: Momentum
            self.features['signal_momentum'] = np.where(
                self.features['avg_disp_change_5d'] > 0, 1,
                np.where(self.features['avg_disp_change_5d'] < 0, -1, 0)
            )
            self.features['signal_momentum_strength'] = (
                self.features['momentum_zscore'].abs()
            )
            
            # SIGNAL 2: Regime
            self.features['signal_regime'] = 0
            self.features.loc[
                self.features['disp_quartile'].isin(['Q3_Moyen_Haut', 'Q4_Haut']),
                'signal_regime'
            ] = 1
            self.features.loc[
                self.features['disp_quartile'] == 'Q1_Bas',
                'signal_regime'
            ] = -1
            
            self.features['signal_regime_strength'] = (
                self.features['avg_disp_zscore'].abs()
            )
            
            if self.verbose:
                print("✓ Signaux générés (Momentum + Regime)")
        except Exception as e:
            print(f"✗ Erreur génération signaux: {e}")
            raise
    
    def get_signals_dataframe(self) -> pd.DataFrame:
        """Retourner le DataFrame complet avec signaux."""
        if self.features is None:
            raise ValueError("Features non calculées")
        return self.features.copy()
    
    def get_latest_signals(self, n_rows: int = 20) -> pd.DataFrame:
        """Retourner les derniers n signaux."""
        if self.features is None:
            return pd.DataFrame()
        
        display_cols = [
            'date', 'price_5tc', 'avg_dispersion', 'cape_dispersion', 
            'vloc_dispersion', 'disp_quartile', 'avg_disp_change_5d', 
            'signal_momentum', 'signal_regime', 'return_5d'
        ]
        return self.features[display_cols].tail(n_rows).copy()
    
    def get_signal_statistics(self) -> Dict[str, Dict]:
        """Calculer les stats pour chaque signal."""
        if self.features is None:
            return {}
        
        available_signals = [
            col for col in ['signal_momentum', 'signal_regime']
            if col in self.features.columns
        ]
        
        if not available_signals:
            return {}
        
        df = self.features.dropna(subset=available_signals)
        stats = {}
        
        for signal_name in available_signals:
            signal_col = signal_name
            long_days = df[signal_col] == 1
            short_days = df[signal_col] == -1
            flat_days = df[signal_col] == 0
            
            stats[signal_name] = {
                'total_signals': len(df),
                'long_signals': long_days.sum(),
                'short_signals': short_days.sum(),
                'flat_signals': flat_days.sum(),
                'avg_return_on_long': (
                    df.loc[long_days, 'return_5d'].mean() 
                    if long_days.sum() > 0 else np.nan
                ),
                'avg_return_on_short': (
                    df.loc[short_days, 'return_5d'].mean() 
                    if short_days.sum() > 0 else np.nan
                ),
                'win_rate_long': (
                    (df.loc[long_days, 'return_5d'] > 0).sum() / long_days.sum()
                    if long_days.sum() > 0 else np.nan
                ),
                'win_rate_short': (
                    (df.loc[short_days, 'return_5d'] < 0).sum() / short_days.sum()
                    if short_days.sum() > 0 else np.nan
                ),
            }
        
        return stats
    
    def get_signal_explanation(self, signal_type: str) -> Dict:
        """Retourner l'explication d'un signal."""
        return self.signal_explanations.get(signal_type, {})
    
    def get_all_explanations(self) -> Dict:
        """Retourner toutes les explications."""
        return self.signal_explanations
    
    def signal_summary(self) -> str:
        """Retourner un résumé texte du dernier signal."""
        if self.features is None or len(self.features) == 0:
            return "Pas de signaux disponibles"
        
        latest = self.features.iloc[-1]
        
        def signal_to_text(val):
            if val > 0:
                return "🟢 LONG"
            elif val < 0:
                return "🔴 SHORT"
            else:
                return "⚪ FLAT"
        
        summary = f"""
╔══════════════════════════════════════════════════════════════╗
║                    ÉTAT ACTUEL DES SIGNAUX                  ║
╚══════════════════════════════════════════════════════════════╝

Date: {latest['date'].strftime('%Y-%m-%d')}

MARCHÉ ACTUELLEMENT:
• Prix 5TC: ${latest['price_5tc']:.0f}/jour
• Dispersion Moyenne: {latest['avg_dispersion']:.0f}
  (Capesize: {latest['cape_dispersion']:.0f}, VLOC: {latest['vloc_dispersion']:.0f})
• Régime: {latest['disp_quartile']}
• Z-score Dispersion: {latest['avg_disp_zscore']:.2f}

SIGNAUX AUJOURD'HUI:
• Momentum: {signal_to_text(latest['signal_momentum'])}
  (Changement 5j: {latest['avg_disp_change_5d']:+.1f}, force: {latest['momentum_zscore']:.2f}σ)
  
• Regime: {signal_to_text(latest['signal_regime'])}
  (Régime: {latest['disp_quartile']})

RETOUR ATTENDU (5 jours):
• Moyenne historique sur signaux similaires: {latest['return_5d']:+.1%}
"""
        return summary
    
    @staticmethod
    def _signal_to_text(val: float) -> str:
        if val > 0:
            return "🟢 LONG"
        elif val < 0:
            return "🔴 SHORT"
        else:
            return "⚪ FLAT"
