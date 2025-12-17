"""
DataManager Class - Chargement et Validation des Données

Responsabilités:
- Charger les prix 5TC front-month (cape_front_month.csv)
- Charger la dispersion flotte Capesize + VLOC (dispersion_case_study.csv)
- Fusionner les datasets
- Valider la qualité des données
- Fournir un DataFrame propre

Context Économique:
La dispersion élevée = bateaux bien répartis = meilleur matching offre/demande
La dispersion basse = bateaux concentrés = congestion potentielle
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Optional
from datetime import datetime


class DataManager:
    """
    Gère le chargement et la validation des données de trading.
    
    Attributes:
        price_data (pd.DataFrame): Données brutes 5TC front-month
        dispersion_data (pd.DataFrame): Données brutes dispersion (Capesize + VLOC)
        merged_data (pd.DataFrame): Données fusionnées et propres
        data_quality_report (dict): Rapport de qualité des données
    """
    
    def __init__(self, price_csv: str, dispersion_csv: str, verbose: bool = True):
        """
        Initialiser DataManager et charger les deux datasets.
        
        Args:
            price_csv: Chemin vers cape_front_month.csv
            dispersion_csv: Chemin vers dispersion_case_study.csv
            verbose: Afficher les logs de chargement
        """
        self.verbose = verbose
        self.price_data = None
        self.dispersion_data = None
        self.merged_data = None
        self.data_quality_report = {}
        
        # Charger les deux datasets
        self._load_price_data(price_csv)
        self._load_dispersion_data(dispersion_csv)
        
        # Fusionner et préparer
        if self.price_data is not None and self.dispersion_data is not None:
            self._merge_datasets()
            self._add_basic_features()
    
    def _load_price_data(self, filepath: str) -> None:
        """
        Charger les prix 5TC front-month.
        
        Colonnes attendues: date, value
        Extrait: date, value (renommé en price_5tc)
        """
        try:
            df = pd.read_csv(filepath)
            df['date'] = pd.to_datetime(df['date'])
            
            # Garder colonnes nécessaires
            self.price_data = df[['date', 'value']].copy()
            self.price_data.rename(columns={'value': 'price_5tc'}, inplace=True)
            
            # Supprimer doublons
            self.price_data = self.price_data.drop_duplicates(
                subset=['date'], 
                keep='first'
            )
            self.price_data = self.price_data.sort_values('date').reset_index(drop=True)
            
            if self.verbose:
                print(f"✓ Prix 5TC chargés: {len(self.price_data)} lignes")
                print(f"  Période: {self.price_data['date'].min().date()} "
                      f"à {self.price_data['date'].max().date()}")
        except Exception as e:
            print(f"✗ Erreur chargement prix: {e}")
            self.data_quality_report['price_load_error'] = str(e)
    
    def _load_dispersion_data(self, filepath: str) -> None:
        """
        Charger les données de dispersion flotte (Capesize et VLOC).
        
        Colonnes attendues: date, VesselClass, VesselCount, Dispersion
        Sépare Capesize et VLOC, puis calcule moyenne pondérée.
        """
        try:
            df = pd.read_csv(filepath)
            df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
            
            # Séparer Capesize et VLOC
            df_cape = df[df['VesselClass'] == 'Capesize'][
                ['date', 'VesselCount', 'Dispersion']
            ].copy()
            df_vloc = df[df['VesselClass'] == 'VLOC'][
                ['date', 'VesselCount', 'Dispersion']
            ].copy()
            
            # Renommer pour clarté
            df_cape.rename(columns={
                'VesselCount': 'cape_vessel_count',
                'Dispersion': 'cape_dispersion'
            }, inplace=True)
            
            df_vloc.rename(columns={
                'VesselCount': 'vloc_vessel_count',
                'Dispersion': 'vloc_dispersion'
            }, inplace=True)
            
            # Fusionner sur date
            self.dispersion_data = df_cape.merge(df_vloc, on='date', how='outer')
            
            # Nettoyer et trier
            self.dispersion_data = self.dispersion_data.drop_duplicates(
                subset=['date'], 
                keep='first'
            )
            self.dispersion_data = self.dispersion_data.sort_values(
                'date'
            ).reset_index(drop=True)
            
            # Calculer métriques combinées
            self.dispersion_data['total_vessel_count'] = (
                self.dispersion_data['cape_vessel_count'].fillna(0) +
                self.dispersion_data['vloc_vessel_count'].fillna(0)
            )
            
            # Moyenne pondérée par count
            self.dispersion_data['avg_dispersion'] = (
                (self.dispersion_data['cape_dispersion'] * 
                 self.dispersion_data['cape_vessel_count'].fillna(0) +
                 self.dispersion_data['vloc_dispersion'] * 
                 self.dispersion_data['vloc_vessel_count'].fillna(0)) /
                self.dispersion_data['total_vessel_count'].replace(0, np.nan)
            )
            
            if self.verbose:
                print(f"✓ Dispersion flotte chargée: {len(self.dispersion_data)} lignes")
                print(f"  Capesize: {self.dispersion_data['cape_vessel_count'].min():.0f} "
                      f"à {self.dispersion_data['cape_vessel_count'].max():.0f} bateaux")
                print(f"  VLOC: {self.dispersion_data['vloc_vessel_count'].min():.0f} "
                      f"à {self.dispersion_data['vloc_vessel_count'].max():.0f} bateaux")
        except Exception as e:
            print(f"✗ Erreur chargement dispersion: {e}")
            self.data_quality_report['dispersion_load_error'] = str(e)
    
    def _merge_datasets(self) -> None:
        """Fusionner prix et dispersion sur la date."""
        try:
            # Fusion interne
            merged = self.price_data.merge(
                self.dispersion_data,
                on='date',
                how='inner'
            ).sort_values('date').reset_index(drop=True)
            
            # Vérifier NaN
            missing_count = merged.isna().sum().sum()
            if missing_count > 0:
                merged = merged.dropna()
                self.data_quality_report['rows_dropped_nan'] = missing_count
            
            self.merged_data = merged
            
            if self.verbose:
                print(f"\n✓ Fusion complète: {len(self.merged_data)} lignes communes")
        except Exception as e:
            print(f"✗ Erreur fusion: {e}")
            self.data_quality_report['merge_error'] = str(e)
    
    def _add_basic_features(self) -> None:
        """Ajouter les features basiques (returns, changements)."""
        try:
            # Returns prix
            self.merged_data['log_return_1d'] = np.log(
                self.merged_data['price_5tc'] / 
                self.merged_data['price_5tc'].shift(1)
            )
            
            self.merged_data['return_5d'] = (
                (self.merged_data['price_5tc'] - 
                 self.merged_data['price_5tc'].shift(5)) /
                self.merged_data['price_5tc'].shift(5)
            )
            
            # Changements dispersion
            self.merged_data['cape_disp_change_1d'] = (
                self.merged_data['cape_dispersion'].diff()
            )
            self.merged_data['cape_disp_change_5d'] = (
                self.merged_data['cape_dispersion'].diff(5)
            )
            
            self.merged_data['vloc_disp_change_1d'] = (
                self.merged_data['vloc_dispersion'].diff()
            )
            self.merged_data['vloc_disp_change_5d'] = (
                self.merged_data['vloc_dispersion'].diff(5)
            )
            
            self.merged_data['avg_disp_change_1d'] = (
                self.merged_data['avg_dispersion'].diff()
            )
            self.merged_data['avg_disp_change_5d'] = (
                self.merged_data['avg_dispersion'].diff(5)
            )
            
            if self.verbose:
                print(f"✓ Features basiques ajoutées "
                      f"(returns, changements dispersion)")
        except Exception as e:
            print(f"✗ Erreur features: {e}")
            self.data_quality_report['feature_error'] = str(e)
    
    def get_clean_data(self, drop_na: bool = True) -> pd.DataFrame:
        """
        Retourner dataset propre.
        
        Args:
            drop_na: Si True, supprimer les lignes avec NaN
            
        Returns:
            DataFrame prêt pour SignalGenerator
        """
        if self.merged_data is None:
            raise ValueError("Pas de données fusionnées disponibles")
        
        df = self.merged_data.copy()
        
        if drop_na:
            initial_rows = len(df)
            df = df.dropna()
            rows_dropped = initial_rows - len(df)
            if self.verbose and rows_dropped > 0:
                print(f"  {rows_dropped} lignes avec NaN supprimées")
        
        return df
    
    def get_data_summary(self) -> Dict:
        """Retourner résumé statistique."""
        if self.merged_data is None:
            return {}
        
        df = self.get_clean_data(drop_na=True)
        
        return {
            'sample_size': len(df),
            'date_start': df['date'].min(),
            'date_end': df['date'].max(),
            'years_covered': (df['date'].max() - df['date'].min()).days / 365.25,
            'price_5tc': {
                'mean': df['price_5tc'].mean(),
                'std': df['price_5tc'].std(),
                'min': df['price_5tc'].min(),
                'max': df['price_5tc'].max(),
            },
            'cape_dispersion': {
                'mean': df['cape_dispersion'].mean(),
                'std': df['cape_dispersion'].std(),
                'min': df['cape_dispersion'].min(),
                'max': df['cape_dispersion'].max(),
            },
            'vloc_dispersion': {
                'mean': df['vloc_dispersion'].mean(),
                'std': df['vloc_dispersion'].std(),
                'min': df['vloc_dispersion'].min(),
                'max': df['vloc_dispersion'].max(),
            },
            'avg_dispersion': {
                'mean': df['avg_dispersion'].mean(),
                'std': df['avg_dispersion'].std(),
                'min': df['avg_dispersion'].min(),
                'max': df['avg_dispersion'].max(),
            },
            'correlation_cape': df['price_5tc'].corr(df['cape_dispersion']),
            'correlation_vloc': df['price_5tc'].corr(df['vloc_dispersion']),
            'correlation_avg': df['price_5tc'].corr(df['avg_dispersion']),
        }
    
    def validate_data(self) -> Dict:
        """Valider la qualité des données."""
        if self.merged_data is None:
            return {'status': 'error', 'message': 'Pas de données fusionnées'}
        
        df = self.get_clean_data(drop_na=True)
        
        report = {'status': 'ok', 'checks': {}}
        
        # Outliers prix (5 std devs)
        price_mean = df['price_5tc'].mean()
        price_std = df['price_5tc'].std()
        outliers = ((df['price_5tc'] - price_mean).abs() > 5 * price_std).sum()
        report['checks']['price_outliers'] = {
            'count': outliers,
            'status': 'ok' if outliers == 0 else 'warning'
        }
        
        # Gaps dans continuité des dates
        date_diffs = df['date'].diff().dt.days
        max_gap = date_diffs[1:].max()
        report['checks']['date_continuity'] = {
            'max_gap_days': int(max_gap),
            'status': 'ok' if max_gap <= 5 else 'warning'
        }
        
        # Variance
        report['checks']['price_variance'] = {
            'std': price_std,
            'status': 'ok' if price_std > 0 else 'error'
        }
        
        report['checks']['cape_disp_variance'] = {
            'std': df['cape_dispersion'].std(),
            'status': 'ok' if df['cape_dispersion'].std() > 0 else 'error'
        }
        
        report['checks']['vloc_disp_variance'] = {
            'std': df['vloc_dispersion'].std(),
            'status': 'ok' if df['vloc_dispersion'].std() > 0 else 'error'
        }
        
        return report
