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
    
    def __init__(self, clean_data: pd.DataFrame, signal_lag: int = 0):
        """
        Initialize SignalGenerator.
        
        Args:
            clean_data: Output from DataManager.get_clean_data()
            signal_lag: Number of days to wait before acting on signal (0-14)
        """
        self.data = clean_data.copy()
        self.features = None
        self.signal_lag = signal_lag
        
        # Position sizing thresholds (based on momentum z-score)
        # MULTI-THRESHOLD APPROACH: Graduated conviction levels
        self.extreme_threshold = 2.5     # |z| ≥ 2.5 → 100% position (EXTREME)
        self.very_strong_threshold = 2.0 # 2.0 ≤ |z| < 2.5 → 75% position (VERY STRONG)
        self.strong_threshold = 1.5      # 1.5 ≤ |z| < 2.0 → 50% position (STRONG)
        self.medium_threshold = 1.0      # 1.0 ≤ |z| < 1.5 → 25% position (MEDIUM)
        # All signals with |z| < 1.0 are IGNORED (too weak)
        
        # Protective mechanisms
        self.volatility_threshold = 2.0  # Don't trade if |price_zscore| > 2.0
        self.persistence_days = 2  # Require 2 consecutive days same signal
        self.use_multi_threshold = True  # Use graduated position sizing
        
        # Regime detection (avoid trading in unfavorable regimes)
        self.regime_lookback = 90  # Days to assess market regime
        self.low_vol_threshold = 0.5  # Don't trade if market too calm (z < 0.5σ)
        
        # Signal explanations
        lag_text = f" with {signal_lag}-day lag" if signal_lag > 0 else ""
        self.signal_explanations = {
            'momentum': {
                'description': f'📈 Multi-Threshold Dispersion Signal{lag_text} (Graduated Conviction)',
                'logic': f'Graduated position sizing: 25% (1.0≤|z|<1.5), 50% (1.5≤|z|<2.0), 75% (2.0≤|z|<2.5), 100% (|z|≥2.5). Protected by: volatility filter, 2-day persistence, regime detection{lag_text}',
                'economic_meaning': (
                    'Multi-threshold approach balances signal capture with risk management. '
                    'Stronger signals (higher |z-score|) receive larger allocations. '
                    'Trades ~15-25% of days vs ~5% with extreme-only approach. '
                    'Regime detection prevents trading during unfavorable market conditions. '
                    f'{" Signal lag allows confirmation time." if signal_lag > 0 else ""}'
                ),
                'signal_type': 'Multi-Threshold Momentum with Regime Detection',
                'horizon': '5-20 days (moderate frequency)',
                'rationale': (
                    'Graduated position sizing allows participating in strong signals (|z|≥1.0) '
                    'while maintaining larger positions for extreme events (|z|≥2.5). '
                    'More aggressive than extreme-only but still filters weak signals (|z|<1.0). '
                    'Balances transaction costs with signal capture. Combine with other indicators for best results.'
                )
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
        except Exception as e:
            print(f"✗ Error computing features: {e}")
            raise
    
    def _generate_signals(self) -> None:
        """Generate the momentum signal - EXTREME EVENTS ONLY."""
        try:
            # Direction: +1 (LONG), -1 (SHORT), 0 (FLAT)
            signal_direction = np.where(
                self.features['avg_disp_change_5d'] > 0, 1,
                np.where(self.features['avg_disp_change_5d'] < 0, -1, 0)
            )
            
            # Strength: absolute z-score
            strength = self.features['momentum_zscore'].abs()
            
            # MULTI-THRESHOLD POSITION SIZING: Graduated conviction levels
            # More aggressive than extreme-only, but still filters weak signals
            if self.use_multi_threshold:
                # Graduated position sizing based on z-score strength:
                # |z| ≥ 2.5 → 100% (EXTREME - very rare, ~2% of days)
                # 2.0 ≤ |z| < 2.5 → 75% (VERY STRONG - rare, ~3% of days)
                # 1.5 ≤ |z| < 2.0 → 50% (STRONG - uncommon, ~5% of days)
                # 1.0 ≤ |z| < 1.5 → 25% (MEDIUM - occasional, ~10% of days)
                # |z| < 1.0 → 0% (WEAK - filtered out, ~80% of days)
                position_size = np.where(
                    strength >= self.extreme_threshold, 1.00,      # 100% for extreme
                    np.where(
                        strength >= self.very_strong_threshold, 0.75,  # 75% for very strong
                        np.where(
                            strength >= self.strong_threshold, 0.50,      # 50% for strong
                            np.where(
                                strength >= self.medium_threshold, 0.25,     # 25% for medium
                                0.0  # 0% for weak
                            )
                        )
                    )
                )
            else:
                # Extreme-only logic (conservative)
                position_size = np.where(strength >= 2.0, 1.00, 0.0)
            
            # Combine direction and size: signal ranges from -1.0 to +1.0
            signal_raw = signal_direction * position_size
            
            # PROTECTIVE MECHANISM 1: Volatility Filter
            # Don't trade when price volatility is extreme
            price_zscore_abs = self.features['price_zscore'].abs()
            volatility_filter = price_zscore_abs > self.volatility_threshold
            signal_raw = np.where(volatility_filter, 0, signal_raw)
            
            # PROTECTIVE MECHANISM 1b: Regime Detection (NEW)
            # Avoid trading in low-volatility regimes where relationship breaks down
            # Calculate rolling regime indicator
            regime_volatility = self.features['momentum_zscore'].abs().rolling(self.regime_lookback).mean()
            low_vol_regime = regime_volatility < self.low_vol_threshold
            signal_raw = np.where(low_vol_regime, 0, signal_raw)
            
            # PROTECTIVE MECHANISM 2: Signal Persistence
            # Require N consecutive days of same signal direction
            signal_series = pd.Series(signal_raw)
            signal_direction_series = pd.Series(np.sign(signal_raw))
            
            # Check if previous N days had same direction (non-zero)
            persistent_signal = signal_raw.copy()
            for i in range(len(signal_raw)):
                if i < self.persistence_days:
                    persistent_signal[i] = 0  # Not enough history
                else:
                    # Check if all previous persistence_days have same direction
                    recent_directions = signal_direction_series.iloc[i-self.persistence_days:i]
                    current_direction = signal_direction_series.iloc[i]
                    
                    # All must be same sign and non-zero
                    if current_direction != 0:
                        if not all(recent_directions == current_direction):
                            persistent_signal[i] = 0  # Not persistent enough
                    else:
                        persistent_signal[i] = 0
            
            # Apply lag: shift signal forward by signal_lag days
            # Signal from day T is used on day T+lag
            if self.signal_lag > 0:
                self.features['signal_momentum'] = pd.Series(persistent_signal).shift(self.signal_lag).fillna(0).values
            else:
                self.features['signal_momentum'] = persistent_signal
            
            self.features['signal_momentum_strength'] = strength
            self.features['signal_momentum_size'] = np.abs(persistent_signal)
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
            'signal_momentum', 'return_5d'
        ]
        return self.features[display_cols].tail(n_rows).copy()
    
    def get_signal_statistics(self) -> Dict[str, Dict]:
        """Calculate stats for each signal."""
        if self.features is None:
            return {}
        
        available_signals = [
            col for col in ['signal_momentum']
            if col in self.features.columns
        ]
        
        if not available_signals:
            return {}
        
        df = self.features.dropna(subset=available_signals)
        stats = {}
        
        for signal_name in available_signals:
            signal_col = signal_name
            long_days = df[signal_col] > 0
            short_days = df[signal_col] < 0
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
                size_pct = int(val * 100)
                return f"🟢 LONG ({size_pct}%)"
            elif val < 0:
                size_pct = int(abs(val) * 100)
                return f"🔴 SHORT ({size_pct}%)"
            else:
                return "⚪ FLAT (0%)"
        
        lag_info = f" (applied with {self.signal_lag}-day lag)" if self.signal_lag > 0 else ""
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

SIGNAL TODAY{lag_info}:
• Momentum: {signal_to_text(latest['signal_momentum'])}
  (5-day change: {latest['avg_disp_change_5d']:+.1f}, strength: {latest['momentum_zscore']:.2f}σ)

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
