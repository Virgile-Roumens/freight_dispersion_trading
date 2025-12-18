"""
DataManager Class - Data Loading and Validation

Responsibilities:
- Load 5TC front-month prices (cape_front_month.csv)
- Load Capesize + VLOC fleet dispersion (dispersion_case_study.csv)
- Merge datasets
- Validate data quality
- Provide clean DataFrame

Economic Context:
High dispersion = well-distributed vessels = better supply/demand matching
Low dispersion = concentrated vessels = potential congestion
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Optional
from datetime import datetime


class DataManager:
    """
    Manages loading and validation of trading data.
    
    Attributes:
        price_data (pd.DataFrame): Raw 5TC front-month data
        dispersion_data (pd.DataFrame): Raw dispersion data (Capesize + VLOC)
        merged_data (pd.DataFrame): Merged and clean data
        data_quality_report (dict): Data quality report
    """
    
    def __init__(self, price_csv: str, dispersion_csv: str):
        """
        Initialize DataManager and load both datasets.
        
        Args:
            price_csv: Path to cape_front_month.csv
            dispersion_csv: Path to dispersion_case_study.csv
        """
        self.price_data = None
        self.dispersion_data = None
        self.merged_data = None
        self.data_quality_report = {}
        
        # Load both datasets
        self._load_price_data(price_csv)
        self._load_dispersion_data(dispersion_csv)
        
        # Merge and prepare
        if self.price_data is not None and self.dispersion_data is not None:
            self._merge_datasets()
            self._add_basic_features()
    
    def _load_price_data(self, filepath: str) -> None:
        """
        Load 5TC front-month prices.
        
        Expected columns: date, value
        Extracts: date, value (renamed to price_5tc)
        """
        try:
            df = pd.read_csv(filepath)
            df['date'] = pd.to_datetime(df['date'])
            
            # Keep necessary columns
            self.price_data = df[['date', 'value']].copy()
            self.price_data.rename(columns={'value': 'price_5tc'}, inplace=True)
            
            # Remove duplicates
            self.price_data = self.price_data.drop_duplicates(
                subset=['date'], 
                keep='first'
            )
            self.price_data = self.price_data.sort_values('date').reset_index(drop=True)
        except Exception as e:
            print(f"✗ Error loading prices: {e}")
            self.data_quality_report['price_load_error'] = str(e)
    
    def _load_dispersion_data(self, filepath: str) -> None:
        """
        Load fleet dispersion data (Capesize and VLOC).
        
        Expected columns: date, VesselClass, VesselCount, Dispersion
        Separates Capesize and VLOC, then calculates weighted average.
        """
        try:
            df = pd.read_csv(filepath)
            df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
            
            # Separate Capesize and VLOC
            df_cape = df[df['VesselClass'] == 'Capesize'][
                ['date', 'VesselCount', 'Dispersion']
            ].copy()
            df_vloc = df[df['VesselClass'] == 'VLOC'][
                ['date', 'VesselCount', 'Dispersion']
            ].copy()
            
            # Rename for clarity
            df_cape.rename(columns={
                'VesselCount': 'cape_vessel_count',
                'Dispersion': 'cape_dispersion'
            }, inplace=True)
            
            df_vloc.rename(columns={
                'VesselCount': 'vloc_vessel_count',
                'Dispersion': 'vloc_dispersion'
            }, inplace=True)
            
            # Merge on date
            self.dispersion_data = df_cape.merge(df_vloc, on='date', how='outer')
            
            # Clean and sort
            self.dispersion_data = self.dispersion_data.drop_duplicates(
                subset=['date'], 
                keep='first'
            )
            self.dispersion_data = self.dispersion_data.sort_values(
                'date'
            ).reset_index(drop=True)
            
            # Calculate combined metrics
            self.dispersion_data['total_vessel_count'] = (
                self.dispersion_data['cape_vessel_count'].fillna(0) +
                self.dispersion_data['vloc_vessel_count'].fillna(0)
            )
            
            # Weighted average by count
            self.dispersion_data['avg_dispersion'] = (
                (self.dispersion_data['cape_dispersion'] * 
                 self.dispersion_data['cape_vessel_count'].fillna(0) +
                 self.dispersion_data['vloc_dispersion'] * 
                 self.dispersion_data['vloc_vessel_count'].fillna(0)) /
                self.dispersion_data['total_vessel_count'].replace(0, np.nan)
            )
        except Exception as e:
            print(f"✗ Error loading dispersion: {e}")
            self.data_quality_report['dispersion_load_error'] = str(e)
    
    def _merge_datasets(self) -> None:
        """Merge price and dispersion on date."""
        try:
            # Inner merge
            merged = self.price_data.merge(
                self.dispersion_data,
                on='date',
                how='inner'
            ).sort_values('date').reset_index(drop=True)
            
            # Check NaN
            missing_count = merged.isna().sum().sum()
            if missing_count > 0:
                merged = merged.dropna()
                self.data_quality_report['rows_dropped_nan'] = missing_count
            
            self.merged_data = merged
        except Exception as e:
            print(f"✗ Merge error: {e}")
            self.data_quality_report['merge_error'] = str(e)
    
    def _add_basic_features(self) -> None:
        """Add basic features (returns, changes)."""
        try:
            # Price returns
            self.merged_data['log_return_1d'] = np.log(
                self.merged_data['price_5tc'] / 
                self.merged_data['price_5tc'].shift(1)
            )
            
            self.merged_data['return_5d'] = (
                (self.merged_data['price_5tc'] - 
                 self.merged_data['price_5tc'].shift(5)) /
                self.merged_data['price_5tc'].shift(5)
            )
            
            # Dispersion changes
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
        except Exception as e:
            print(f"✗ Features error: {e}")
            self.data_quality_report['feature_error'] = str(e)
    
    def get_clean_data(self, drop_na: bool = True) -> pd.DataFrame:
        """
        Return clean dataset.
        
        Args:
            drop_na: If True, remove rows with NaN
            
        Returns:
            DataFrame ready for SignalGenerator
        """
        if self.merged_data is None:
            raise ValueError("No merged data available")
        
        df = self.merged_data.copy()
        
        if drop_na:
            df = df.dropna()
        
        return df
    
    def get_data_summary(self) -> Dict:
        """Return statistical summary."""
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
        """Validate data quality."""
        if self.merged_data is None:
            return {'status': 'error', 'message': 'No merged data'}
        
        df = self.get_clean_data(drop_na=True)
        
        report = {'status': 'ok', 'checks': {}}
        
        # Price outliers (5 std devs)
        price_mean = df['price_5tc'].mean()
        price_std = df['price_5tc'].std()
        outliers = ((df['price_5tc'] - price_mean).abs() > 5 * price_std).sum()
        report['checks']['price_outliers'] = {
            'count': outliers,
            'status': 'ok' if outliers == 0 else 'warning'
        }
        
        # Gaps in date continuity
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
