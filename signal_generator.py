"""
SignalGenerator Class - Feature Engineering and Trading Signals

Responsibilities:
- Normalize data (z-scores)
- Classify into regimes (quartiles)
- Generate trading signals with correct economic logic
- Provide explanations for each signal

Economic Context:
HIGH dispersion = fleet well spread = efficient supply = BEARISH for prices
LOW dispersion = fleet concentrated = regional scarcity = BULLISH for prices

Signal 1 (Momentum): Short-term dispersion changes (INVERTED LOGIC)
Signal 2 (Mean Reversion): Dispersion accordion effect (FADE EXTREMES)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


class SignalGenerator:
    """
    Generates trading signals from clean data.
    
    Attributes:
        data (pd.DataFrame): Clean data from DataManager
        features (pd.DataFrame): Calculated features + signals
        signal_explanations (dict): Economic explanations of signals
    """
    
    def __init__(self, clean_data: pd.DataFrame, signal_lag: int = 0, mr_threshold: float = 1.0):
        """
        Initialize SignalGenerator.
        
        Args:
            clean_data: Output from DataManager.get_clean_data()
            signal_lag: Number of days to wait before acting on signal (0-20)
            mr_threshold: Minimum |z-score| to trigger mean-reversion signal (0.5-2.5)
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
        
        # Mean reversion threshold (configurable via sidebar)
        self.mr_threshold = mr_threshold
        
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
                'description': f'📉 Inverted Dispersion Momentum{lag_text} (Correct Economic Logic)',
                'logic': f'HIGH dispersion (rising) → SHORT (bearish). LOW dispersion (falling) → LONG (bullish). Graduated sizing: 25%-100%{lag_text}',
                'economic_meaning': (
                    '✅ CORRECTED LOGIC: High dispersion = fleet well-positioned globally = efficient supply = BEARISH prices. '
                    'Low dispersion = fleet concentrated = regional scarcity = BULLISH prices. '
                    'Rising dispersion → fleet spreading → supply efficiency increasing → prices fall → SHORT. '
                    'Falling dispersion → fleet concentrating → supply tightening → prices rise → LONG. '
                    f'{" Signal lag allows confirmation time." if signal_lag > 0 else ""}'
                ),
                'signal_type': 'Inverted Momentum (High Disp = Bearish)',
                'horizon': '5-20 days (moderate frequency)',
                'rationale': (
                    'Inverted momentum captures the correct freight market dynamics: '
                    'when the fleet disperses globally, it signals abundant supply and efficient cargo pickup, '
                    'which is bearish for freight rates. Conversely, concentrated fleets indicate supply scarcity '
                    'and bullish pricing pressure. Graduated position sizing balances signal strength with risk.'
                )
            },
            'mean_reversion': {
                'description': f'🔄 Dispersion Mean Reversion{lag_text} (Accordion Effect)',
                'logic': (
                    f'Dispersion > long-run mean (+{self.mr_threshold}σ) → fleet will concentrate → prices rise → LONG. '
                    f'Dispersion < mean (-{self.mr_threshold}σ) → fleet will disperse → prices fall → SHORT{lag_text}'
                ),
                'economic_meaning': (
                    'Fleet dispersion behaves like an accordion: when vessels are highly dispersed, they tend to concentrate '
                    'back toward key loading regions. When concentrated, they disperse to seek cargo globally. '
                    'FADE THE EXTREMES: High dispersion is unsustainable → expect concentration → bullish for prices (LONG). '
                    'Low dispersion is temporary → expect dispersion → bearish for prices (SHORT). '
                    f'Uses 120-day rolling mean for long-run equilibrium. {" Signal lag allows confirmation." if signal_lag > 0 else ""}'
                ),
                'signal_type': 'Mean Reversion (Fade Extremes)',
                'horizon': '10-30 days (longer cycle)',
                'rationale': (
                    'Dispersion has a natural equilibrium driven by cargo flow patterns (Brazil/Australia → China). '
                    'Extreme deviations from this equilibrium are temporary and revert. '
                    'When dispersion is abnormally high, the fleet is "stretched thin" and will naturally concentrate '
                    'as vessels complete voyages and reposition. This concentration creates upward pricing pressure. '
                    'Conversely, abnormally low dispersion (fleet bunched up) is inefficient and unsustainable, '
                    'leading to dispersion and downward pricing pressure. This signal complements momentum by capturing '
                    'longer-term structural imbalances.'
                )
            }
        }
        
        # Calculate
        self._compute_features()
        self._generate_signals()
    
    # ========================================================================
    # FEATURES
    # ========================================================================
    
    def _compute_features(self) -> None:
        """Calculate all features (z-scores, quartiles, momentum, mean-reversion)."""
        try:
            self.features = self.data.copy()
            window_short = 60   # Rolling window for momentum z-scores
            window_long = 120   # Rolling window for mean-reversion z-scores
            
            # ------------------------------------------------------------------
            # Short-term dispersion z-scores (60d, used by momentum signal)
            # ------------------------------------------------------------------
            self.features['avg_disp_mean_60d'] = (
                self.features['avg_dispersion'].rolling(window_short).mean()
            )
            self.features['avg_disp_std_60d'] = (
                self.features['avg_dispersion'].rolling(window_short).std()
            )
            self.features['avg_disp_zscore'] = (
                (self.features['avg_dispersion'] - self.features['avg_disp_mean_60d'])
                / self.features['avg_disp_std_60d']
            )
            
            # ------------------------------------------------------------------
            # Long-term dispersion z-scores (120d, used by mean-reversion signal)
            # ------------------------------------------------------------------
            self.features['avg_disp_mean_120d'] = (
                self.features['avg_dispersion'].rolling(window_long).mean()
            )
            self.features['avg_disp_std_120d'] = (
                self.features['avg_dispersion'].rolling(window_long).std()
            )
            self.features['avg_disp_mr_zscore'] = (
                (self.features['avg_dispersion'] - self.features['avg_disp_mean_120d'])
                / self.features['avg_disp_std_120d']
            )
            
            # ------------------------------------------------------------------
            # Capesize-specific z-scores (60d)
            # ------------------------------------------------------------------
            self.features['cape_disp_zscore'] = (
                (self.features['cape_dispersion']
                 - self.features['cape_dispersion'].rolling(window_short).mean())
                / self.features['cape_dispersion'].rolling(window_short).std()
            )
            
            # ------------------------------------------------------------------
            # VLOC-specific z-scores (60d)
            # ------------------------------------------------------------------
            self.features['vloc_disp_zscore'] = (
                (self.features['vloc_dispersion']
                 - self.features['vloc_dispersion'].rolling(window_short).mean())
                / self.features['vloc_dispersion'].rolling(window_short).std()
            )
            
            # ------------------------------------------------------------------
            # Price z-scores (60d, used by volatility filter)
            # ------------------------------------------------------------------
            self.features['price_mean_60d'] = (
                self.features['price_5tc'].rolling(window_short).mean()
            )
            self.features['price_std_60d'] = (
                self.features['price_5tc'].rolling(window_short).std()
            )
            self.features['price_zscore'] = (
                (self.features['price_5tc'] - self.features['price_mean_60d'])
                / self.features['price_std_60d']
            )
            
            # ------------------------------------------------------------------
            # Dispersion quartiles (regime classification)
            # ------------------------------------------------------------------
            self.features['disp_quartile'] = pd.qcut(
                self.features['avg_dispersion'],
                q=4,
                labels=['Q1_Low', 'Q2_Medium_Low', 'Q3_Medium_High', 'Q4_High'],
                duplicates='drop'
            )
            
            # ------------------------------------------------------------------
            # Normalized momentum z-score (for inverted momentum signal)
            # ------------------------------------------------------------------
            disp_change_mean = (
                self.features['avg_disp_change_5d'].rolling(window_short).mean()
            )
            disp_change_std = (
                self.features['avg_disp_change_5d'].rolling(window_short).std()
            )
            self.features['momentum_zscore'] = (
                (self.features['avg_disp_change_5d'] - disp_change_mean)
                / disp_change_std
            )
            
        except Exception as e:
            print(f"✗ Error computing features: {e}")
            raise
    
    # ========================================================================
    # SIGNAL GENERATION
    # ========================================================================
    
    def _generate_signals(self) -> None:
        """Generate both momentum and mean-reversion signals."""
        self._generate_momentum_signal()
        self._generate_mean_reversion_signal()
    
    # ---------------- helpers shared by both signal generators ---------------
    
    def _apply_graduated_sizing(self, strength: np.ndarray) -> np.ndarray:
        """
        Map absolute z-score strength to graduated position sizes.
        
        Returns numpy array with values in {0.0, 0.25, 0.50, 0.75, 1.00}.
        """
        if self.use_multi_threshold:
            return np.where(
                strength >= self.extreme_threshold, 1.00,
                np.where(
                    strength >= self.very_strong_threshold, 0.75,
                    np.where(
                        strength >= self.strong_threshold, 0.50,
                        np.where(
                            strength >= self.medium_threshold, 0.25,
                            0.0
                        )
                    )
                )
            )
        else:
            return np.where(strength >= 2.0, 1.00, 0.0)
    
    def _apply_persistence_filter(self, signal_raw: np.ndarray) -> np.ndarray:
        """
        Require `self.persistence_days` consecutive days of the same direction
        before allowing a signal through. Otherwise set to 0.
        """
        direction_series = pd.Series(np.sign(signal_raw))
        persistent = signal_raw.copy()
        
        for i in range(len(signal_raw)):
            if i < self.persistence_days:
                persistent[i] = 0.0
            else:
                current_dir = direction_series.iloc[i]
                if current_dir != 0:
                    recent = direction_series.iloc[i - self.persistence_days : i]
                    if not (recent == current_dir).all():
                        persistent[i] = 0.0
                else:
                    persistent[i] = 0.0
        
        return persistent
    
    def _apply_volatility_filter(self, signal_raw: np.ndarray) -> np.ndarray:
        """Zero out signals when |price_zscore| exceeds volatility threshold."""
        price_z_abs = self.features['price_zscore'].abs().values
        return np.where(price_z_abs > self.volatility_threshold, 0.0, signal_raw)
    
    def _apply_lag(self, signal: np.ndarray) -> np.ndarray:
        """Shift signal forward by self.signal_lag days (fill with 0)."""
        if self.signal_lag > 0:
            return pd.Series(signal).shift(self.signal_lag).fillna(0.0).values
        return signal
    
    # ---------------- SIGNAL 1: Inverted Momentum ---------------------------
    
    def _generate_momentum_signal(self) -> None:
        """
        Generate the INVERTED momentum signal (CHANGE 1).
        
        ✅ CORRECTED ECONOMIC LOGIC:
        - Rising dispersion  (positive avg_disp_change_5d) → SHORT (bearish)
        - Falling dispersion (negative avg_disp_change_5d) → LONG  (bullish)
        """
        try:
            # ── direction: INVERTED relative to old code ──
            change = self.features['avg_disp_change_5d'].values
            signal_direction = np.where(
                change < 0,  1.0,           # Falling dispersion → LONG
                np.where(change > 0, -1.0,  # Rising dispersion  → SHORT
                         0.0)
            )
            
            # ── strength: absolute momentum z-score ──
            strength = self.features['momentum_zscore'].abs().values
            
            # ── graduated position sizing ──
            position_size = self._apply_graduated_sizing(strength)
            
            # ── raw signal: direction × size  →  range [-1.0 … +1.0] ──
            signal_raw = signal_direction * position_size
            
            # ── volatility filter ──
            signal_raw = self._apply_volatility_filter(signal_raw)
            
            # ── regime detection: suppress when market too calm ──
            regime_vol = (
                self.features['momentum_zscore']
                .abs()
                .rolling(self.regime_lookback)
                .mean()
                .values
            )
            signal_raw = np.where(regime_vol < self.low_vol_threshold, 0.0, signal_raw)
            
            # ── persistence filter ──
            persistent = self._apply_persistence_filter(signal_raw)
            
            # ── apply lag ──
            self.features['signal_momentum'] = self._apply_lag(persistent)
            self.features['signal_momentum_strength'] = strength
            self.features['signal_momentum_size'] = np.abs(persistent)
            
        except Exception as e:
            print(f"✗ Error generating momentum signal: {e}")
            raise
    
    # ---------------- SIGNAL 2: Mean Reversion (CHANGE 2) -------------------
    
    def _generate_mean_reversion_signal(self) -> None:
        """
        Generate mean-reversion signal based on 120-day dispersion equilibrium.
        
        ACCORDION EFFECT — FADE THE EXTREMES:
        - Dispersion ABOVE long-run mean (+threshold σ)
          → fleet will concentrate → prices rise → LONG
        - Dispersion BELOW long-run mean (-threshold σ)
          → fleet will disperse  → prices fall  → SHORT
        """
        try:
            mr_z = self.features['avg_disp_mr_zscore'].values
            
            # ── direction: fade extremes ──
            signal_direction = np.where(
                mr_z > 0,  1.0,            # Above mean → LONG  (expect concentration)
                np.where(mr_z < 0, -1.0,   # Below mean → SHORT (expect dispersion)
                         0.0)
            )
            
            # ── strength: absolute mr z-score ──
            strength = np.abs(mr_z)
            
            # ── graduated position sizing (same thresholds as momentum) ──
            position_size = self._apply_graduated_sizing(strength)
            
            # ── raw signal ──
            signal_raw = signal_direction * position_size
            
            # ── volatility filter (identical to momentum) ──
            signal_raw = self._apply_volatility_filter(signal_raw)
            
            # ── persistence filter (identical to momentum) ──
            persistent = self._apply_persistence_filter(signal_raw)
            
            # ── apply lag ──
            self.features['signal_mean_reversion'] = self._apply_lag(persistent)
            self.features['signal_mean_reversion_strength'] = strength
            self.features['signal_mean_reversion_size'] = np.abs(persistent)
            
        except Exception as e:
            print(f"✗ Error generating mean-reversion signal: {e}")
            raise
    
    # ========================================================================
    # LEAD-LAG CROSS-CORRELATION (CHANGE 3)
    # ========================================================================
    
    def compute_lead_lag_crosscorr(
        self,
        series_x: str = 'avg_dispersion',
        series_y: str = 'price_5tc',
        max_lag: int = 20
    ) -> pd.DataFrame:
        """
        Compute lead-lag cross-correlation between two time series.
        
        Interpretation guide:
        • Positive lag k  → series_x at t correlates with series_y at t+k
          ⇒ series_x LEADS series_y by k days  (predictor!)
        • Lag 0           → contemporaneous (no predictive power)
        • Negative lag k  → series_y at t correlates with series_x at t+|k|
          ⇒ series_x LAGS series_y (signal is late)
        
        If peak absolute correlation is at positive lag, dispersion leads price
        (potential predictor).  If at lag 0 or negative, the momentum signal is
        likely lagging behind actual price moves.
        
        Args:
            series_x: Column name for the "predictor" series
                      (e.g. 'avg_dispersion', 'avg_disp_change_5d')
            series_y: Column name for the "target" series
                      (e.g. 'price_5tc', 'return_5d')
            max_lag:  Maximum lag (in days) to compute in both directions
        
        Returns:
            DataFrame with columns: lag, correlation, series_x, series_y
        """
        if self.features is None:
            raise ValueError("Features not computed yet.")
        
        for col in (series_x, series_y):
            if col not in self.features.columns:
                raise ValueError(f"Column '{col}' not found in features.")
        
        df = self.features[[series_x, series_y]].dropna()
        x = df[series_x].values
        y = df[series_y].values
        n = len(x)
        
        rows: List[Dict] = []
        for lag in range(-max_lag, max_lag + 1):
            if lag == 0:
                corr = np.corrcoef(x, y)[0, 1]
            elif lag > 0:
                # x at t  vs  y at t+lag  →  x leads y
                corr = np.corrcoef(x[:n - lag], y[lag:])[0, 1]
            else:
                # y at t  vs  x at t+|lag|  →  x lags y
                abs_lag = abs(lag)
                corr = np.corrcoef(x[abs_lag:], y[:n - abs_lag])[0, 1]
            
            rows.append({
                'lag': lag,
                'correlation': corr,
                'series_x': series_x,
                'series_y': series_y
            })
        
        return pd.DataFrame(rows)
    
    # ========================================================================
    # PUBLIC ACCESSORS
    # ========================================================================
    
    def get_signals_dataframe(self) -> pd.DataFrame:
        """Return complete DataFrame with all features and signals."""
        if self.features is None:
            raise ValueError("Features not calculated")
        return self.features.copy()
    
    def get_latest_signals(self, n_rows: int = 20) -> pd.DataFrame:
        """Return the last *n_rows* of key signal columns."""
        if self.features is None:
            return pd.DataFrame()
        
        display_cols = [
            'date', 'price_5tc', 'avg_dispersion',
            'cape_dispersion', 'vloc_dispersion',
            'disp_quartile', 'avg_disp_change_5d',
            'momentum_zscore', 'avg_disp_mr_zscore',
            'signal_momentum', 'signal_mean_reversion',
            'return_5d',
        ]
        available = [c for c in display_cols if c in self.features.columns]
        return self.features[available].tail(n_rows).copy()
    
    def get_signal_statistics(self) -> Dict[str, Dict]:
        """Calculate descriptive stats for each signal column."""
        if self.features is None:
            return {}
        
        signal_cols = [
            c for c in ('signal_momentum', 'signal_mean_reversion')
            if c in self.features.columns
        ]
        if not signal_cols:
            return {}
        
        df = self.features.dropna(subset=signal_cols)
        stats: Dict[str, Dict] = {}
        
        for sig in signal_cols:
            long_mask  = df[sig] > 0
            short_mask = df[sig] < 0
            flat_mask  = df[sig] == 0
            
            stats[sig] = {
                'total_signals':    len(df),
                'long_signals':     int(long_mask.sum()),
                'short_signals':    int(short_mask.sum()),
                'flat_signals':     int(flat_mask.sum()),
                'avg_return_on_long': (
                    df.loc[long_mask, 'return_5d'].mean()
                    if long_mask.sum() > 0 else np.nan
                ),
                'avg_return_on_short': (
                    df.loc[short_mask, 'return_5d'].mean()
                    if short_mask.sum() > 0 else np.nan
                ),
                'win_rate_long': (
                    (df.loc[long_mask, 'return_5d'] > 0).sum() / long_mask.sum()
                    if long_mask.sum() > 0 else np.nan
                ),
                'win_rate_short': (
                    (df.loc[short_mask, 'return_5d'] < 0).sum() / short_mask.sum()
                    if short_mask.sum() > 0 else np.nan
                ),
            }
        
        return stats
    
    def get_signal_explanation(self, signal_type: str) -> Dict:
        """Return explanation dict for *signal_type* ('momentum' or 'mean_reversion')."""
        return self.signal_explanations.get(signal_type, {})
    
    def get_all_explanations(self) -> Dict:
        """Return all signal explanations."""
        return self.signal_explanations
    
    def signal_summary(self) -> str:
        """Human-readable summary of the latest signal state."""
        if self.features is None or len(self.features) == 0:
            return "No signals available."
        
        latest = self.features.iloc[-1]
        
        def _txt(val: float) -> str:
            if val > 0:
                return f"🟢 LONG ({int(val * 100)}%)"
            elif val < 0:
                return f"🔴 SHORT ({int(abs(val) * 100)}%)"
            return "⚪ FLAT (0%)"
        
        lag_info = f" (applied with {self.signal_lag}-day lag)" if self.signal_lag > 0 else ""
        mom  = latest.get('signal_momentum', 0)
        mr   = latest.get('signal_mean_reversion', 0)
        mr_z = latest.get('avg_disp_mr_zscore', np.nan)
        
        return (
            f"\n{'═'*62}\n"
            f"  CURRENT SIGNAL STATE\n"
            f"{'═'*62}\n\n"
            f"Date: {latest['date'].strftime('%Y-%m-%d')}\n\n"
            f"MARKET:\n"
            f"  • 5TC Price:          ${latest['price_5tc']:,.0f}/day\n"
            f"  • Avg Dispersion:     {latest['avg_dispersion']:.0f}\n"
            f"    (Cape: {latest['cape_dispersion']:.0f}  |  VLOC: {latest['vloc_dispersion']:.0f})\n"
            f"  • Regime:             {latest['disp_quartile']}\n"
            f"  • Disp Z-score 60d:  {latest['avg_disp_zscore']:.2f}\n"
            f"  • Disp Z-score 120d: {mr_z:.2f}\n\n"
            f"SIGNALS TODAY{lag_info}:\n"
            f"  • Inverted Momentum:  {_txt(mom)}\n"
            f"    (5d Δ: {latest['avg_disp_change_5d']:+.1f}, mom z: {latest['momentum_zscore']:.2f}σ)\n"
            f"  • Mean Reversion:     {_txt(mr)}\n"
            f"    (vs 120d mean, mr z: {mr_z:.2f}σ)\n\n"
            f"✅ CORRECTED LOGIC: High/rising disp = SHORT · Low/falling disp = LONG\n"
        )
    
    @staticmethod
    def _signal_to_text(val: float) -> str:
        if val > 0:
            return "🟢 LONG"
        elif val < 0:
            return "🔴 SHORT"
        return "⚪ FLAT"