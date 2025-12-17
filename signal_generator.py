"""
SignalGenerator Class - Feature Engineering and Trading Signals

Responsibilities:
- Normalize data (z-scores)
- Classify into regimes (quartiles)
- Generate 2 simple and economically justified signals
- Provide explanations for each signal

Economic Context:
Signal 1 (Momentum): Short-term dispersion changes
Signal 2 (Regime): Structural market state (quartiles)
"""

import pandas as pd
import numpy as np
from typing import Dict, List


class SignalGenerator:
    """
    Generates trading signals from clean data.
    
    Attributes:
        data (pd.DataFrame): Clean data from DataManager
        features (pd.DataFrame): Calculated features + signals
        signal_explanations (dict): Economic explanations of signals
    """
    
    def __init__(self, clean_data: pd.DataFrame, verbose: bool = True):
        """
        Initialize SignalGenerator.
        
        Args:
            clean_data: Output from DataManager.get_clean_data()
            verbose: Display logs
        """
        self.data = clean_data.copy()
        self.features = None
        self.verbose = verbose
        
        # Signal explanations
        self.signal_explanations = {
            'momentum': {
                'description': '📈 Dispersion Momentum Signal',
                'logic': 'LONG if 5-day change > 0; SHORT if < 0; FLAT otherwise',
                'economic_meaning': (
                    'Increasing dispersion suggests better vessel distribution '
                    '= rising demand = potentially higher prices. '
                    'The opposite indicates consolidation = weakening demand.'
                ),
                'signal_type': 'Technical/Behavioral',
                'horizon': '5-20 days',
                'rationale': 'Dispersion changes precede price movements'
            },
            'regime': {
                'description': '🎯 Regime Signal (Quartiles)',
                'logic': 'LONG in Q3-Q4 (high); SHORT in Q1 (low); FLAT in Q2',
                'economic_meaning': (
                    'High dispersion periods (Q3-Q4) reflect a structurally '
                    'healthy market with ~41% premium vs Q1. '
                    'This captures structural state, not fine timing.'
                ),
                'signal_type': 'Structural/Fundamental',
                'horizon': 'Multi-week',
                'rationale': 'Captures global supply/demand equilibrium state'
            }
        }
        
        # Calculate
        self._compute_features()
        self._generate_signals()
    
    def _compute_features(self) -> None:
        """Calculate all features (z-scores, quartiles, momentum)."""
        try:
            self.features = self.data.copy()
            window = 60  # Rolling window
            
            # Average dispersion z-scores
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
            
            # Price z-scores
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
            
            # Dispersion quartiles (regimes)
            self.features['disp_quartile'] = pd.qcut(
                self.features['avg_dispersion'],
                q=4,
                labels=['Q1_Low', 'Q2_Medium_Low', 'Q3_Medium_High', 'Q4_High'],
                duplicates='drop'
            )
            
            # Normalized momentum
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
                print("✓ Features calculated (z-scores, quartiles, momentum)")
        except Exception as e:
            print(f"✗ Error computing features: {e}")
            raise
    
    def _generate_signals(self) -> None:
        """Generate the 2 simple signals."""
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
                self.features['disp_quartile'].isin(['Q3_Medium_High', 'Q4_High']),
                'signal_regime'
            ] = 1
            self.features.loc[
                self.features['disp_quartile'] == 'Q1_Low',
                'signal_regime'
            ] = -1
            
            self.features['signal_regime_strength'] = (
                self.features['avg_disp_zscore'].abs()
            )
            
            if self.verbose:
                print("✓ Signals generated (Momentum + Regime)")
        except Exception as e:
            print(f"✗ Error generating signals: {e}")
            raise
    
    def get_signals_dataframe(self) -> pd.DataFrame:
        """Return complete DataFrame with signals."""
        if self.features is None:
            raise ValueError("Features not calculated")
        return self.features.copy()
    
    def get_latest_signals(self, n_rows: int = 20) -> pd.DataFrame:
        """Return the last n signals."""
        if self.features is None:
            return pd.DataFrame()
        
        display_cols = [
            'date', 'price_5tc', 'avg_dispersion', 'cape_dispersion', 
            'vloc_dispersion', 'disp_quartile', 'avg_disp_change_5d', 
            'signal_momentum', 'signal_regime', 'return_5d'
        ]
        return self.features[display_cols].tail(n_rows).copy()
    
    def get_signal_statistics(self) -> Dict[str, Dict]:
        """Calculate stats for each signal."""
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
        """Return explanation for a signal."""
        return self.signal_explanations.get(signal_type, {})
    
    def get_all_explanations(self) -> Dict:
        """Return all explanations."""
        return self.signal_explanations
    
    def signal_summary(self) -> str:
        """Return text summary of latest signal."""
        if self.features is None or len(self.features) == 0:
            return "No signals available"
        
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
║                    CURRENT SIGNAL STATE                     ║
╚══════════════════════════════════════════════════════════════╝

Date: {latest['date'].strftime('%Y-%m-%d')}

MARKET CURRENTLY:
• 5TC Price: ${latest['price_5tc']:.0f}/day
• Average Dispersion: {latest['avg_dispersion']:.0f}
  (Capesize: {latest['cape_dispersion']:.0f}, VLOC: {latest['vloc_dispersion']:.0f})
• Regime: {latest['disp_quartile']}
• Dispersion Z-score: {latest['avg_disp_zscore']:.2f}

SIGNALS TODAY:
• Momentum: {signal_to_text(latest['signal_momentum'])}
  (5-day change: {latest['avg_disp_change_5d']:+.1f}, strength: {latest['momentum_zscore']:.2f}σ)
  
• Regime: {signal_to_text(latest['signal_regime'])}
  (Regime: {latest['disp_quartile']})

EXPECTED RETURN (5 days):
• Historical average on similar signals: {latest['return_5d']:+.1%}
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
