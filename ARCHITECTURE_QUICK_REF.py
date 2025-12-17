"""
QUICK ARCHITECTURE REFERENCE - For Developers
==============================================

Project Structure:
"""

# ============================================================================
# FILE STRUCTURE
# ============================================================================

"""
├── cape_front_month.csv                [Input data]
├── dispersion_case_study.csv           [Input data]
├── requirements.txt                    [Python dependencies]
│
├── data_manager.py                     [Class #1: Data loading]
│   ├── class DataManager
│   │   ├── __init__(price_csv, dispersion_csv)
│   │   ├── get_clean_data()            → Clean DataFrame
│   │   ├── get_data_summary()          → Dict with stats
│   │   └── validate_data()             → Quality report
│
├── signal_generator.py                 [Class #2: Signals]
│   ├── class SignalGenerator
│   │   ├── __init__(clean_data)
│   │   ├── get_signals_dataframe()     → DataFrame with signals
│   │   ├── get_signal_statistics()     → Stats per signal
│   │   ├── get_all_explanations()      → Economic explanations
│   │   └── signal_summary()            → Text summary
│
├── backtest_engine.py                  [Class #3: Backtest]
│   ├── class BacktestEngine
│   │   ├── __init__(data_with_signals, params)
│   │   ├── backtest_strategy()         → Dict results
│   │   ├── get_results()               → Final metrics
│   │   ├── get_trade_log()             → DataFrame trades
│   │   ├── get_equity_curve()          → Equity curve
│   │   └── compare_fees_sensitivity()  → Fee sensitivity
│
└── streamlit_app.py                    [User Interface]
    ├── @st.cache_resource load_data_once()
    ├── Tab 1: 📊 Data Overview
    ├── Tab 2: 🎯 Signal Explorer
    ├── Tab 3: 🏦 Backtest Results
    ├── Tab 4: 📈 Economic Analysis
    └── Tab 5: ⚔️ Strategy Comparison
"""

# ============================================================================
# DATA FLOW
# ============================================================================

"""
CSV (price + dispersion)
    │
    ↓
DataManager.load()
    │
    ├─→ price_data (cleaned)
    ├─→ dispersion_data (Capesize + VLOC separated)
    └─→ merged_data (merged, basic features)
    │
    ↓
clean_data = DataManager.get_clean_data()
    │
    ↓
SignalGenerator(clean_data)
    │
    ├─→ Calculates z-scores, quartiles, momentum
    ├─→ Creates signal_momentum (+ or -)
    └─→ Creates signal_regime (+ or -)
    │
    ↓
signals_df = SignalGenerator.get_signals_dataframe()
    │
    ↓
BacktestEngine(signals_df)
    │
    ├─→ Simulates daily trades
    ├─→ Calculates P&L with fees
    └─→ Generates equity curve
    │
    ↓
results = BacktestEngine.backtest_strategy()
    │
    ├─→ Sharpe, Drawdown, Return, Win Rate
    ├─→ Trade log
    └─→ Equity curve
    │
    ↓
Streamlit Dashboard displays everything
"""

# ============================================================================
# CLASSES - OVERVIEW
# ============================================================================

class DataManager:
    """
    Responsibilities:
    - Load 5TC front-month prices
    - Load dispersion (Capesize + VLOC)
    - Merge datasets
    - Validate quality
    - Provide clean DataFrame
    
    Inputs:
    - cape_front_month.csv (date, value)
    - dispersion_case_study.csv (date, VesselClass, VesselCount, Dispersion)
    
    Outputs:
    - Merged DataFrame with columns:
      - date, price_5tc
      - cape_dispersion, cape_vessel_count
      - vloc_dispersion, vloc_vessel_count
      - avg_dispersion (weighted)
      - log_return_1d, return_5d
      - *_disp_change_1d, *_disp_change_5d
    
    Key Methods:
    - get_clean_data() → Clean DataFrame (NaN removed)
    - get_data_summary() → Dict{sample_size, correlations, stats}
    - validate_data() → Dict{checks: outliers, gaps, variance}
    """
    pass


class SignalGenerator:
    """
    Responsibilities:
    - Normalize data (z-scores)
    - Create quartiles (regimes)
    - Generate 2 simple signals
    - Provide economic explanations
    
    Inputs:
    - Clean DataFrame from DataManager
    
    Outputs:
    - Features DataFrame with columns:
      - *_zscore (normalizations)
      - *_quartile (classifications)
      - signal_momentum (+1, -1, 0)
      - signal_regime (+1, -1, 0)
      - *_strength (absolute Z-scores)
    
    Key Methods:
    - get_signals_dataframe() → DataFrame with signals
    - get_signal_statistics() → Dict stats per signal
    - get_all_explanations() → Dict economic explanations
    - signal_summary() → String text summary
    """
    pass


class BacktestEngine:
    """
    Responsibilities:
    - Simulate daily trading
    - Automatic rebalancing
    - Calculate P&L with fees
    - Generate metrics (Sharpe, Drawdown, etc.)
    - Analyze fee sensitivity
    
    Inputs:
    - DataFrame with signals from SignalGenerator
    - initial_capital (default: 1M)
    - transaction_fee_bps (default: 10)
    - max_drawdown_stop (default: 0.02)
    
    Outputs:
    - results: Dict{
        sharpe_ratio, max_drawdown_pct, total_return_pct,
        win_rate, num_trades, profit_factor, ...
      }
    - trade_log: List[{entry_date, exit_date, entry_price, exit_price,
                       direction, net_pnl, return_pct, ...}]
    - equity_curve: List[portfolio values]
    
    Key Methods:
    - backtest_strategy(signal_col) → Dict results
    - get_results() → Dict metrics
    - get_trade_log() → DataFrame trades
    - get_equity_curve() → (values, dates)
    - compare_fees_sensitivity(fee_levels) → DataFrame sensitivity
    """
    pass


# ============================================================================
# SIGNALS - TECHNICAL DETAIL
# ============================================================================

"""
SIGNAL 1: MOMENTUM DISPERSION
=============================

Calculation:
  avg_disp_change_5d = avg_dispersion[t] - avg_dispersion[t-5]
  
  signal_momentum = sign(avg_disp_change_5d)
                  = +1 if > 0 (LONG)
                  = -1 if < 0 (SHORT)
                  =  0 otherwise (FLAT)

Strength:
  momentum_zscore = (avg_disp_change_5d - mean_60d) / std_60d
  strength = |momentum_zscore|

Economic logic:
  ↑ Dispersion = vessels dispersing (reacting to demand)
  ↓ Dispersion = vessels concentrating (weak demand)

Horizon: 5-20 days (short term)


SIGNAL 2: REGIME (QUARTILES)
============================

Calculation:
  quartile = pd.qcut(avg_dispersion, q=4)
           = [Q1_Low, Q2_MedLow, Q3_MedHigh, Q4_High]
  
  signal_regime = +1 if quartile in [Q3_MedHigh, Q4_High]
                = -1 if quartile == Q1_Low
                =  0 otherwise

Strength:
  avg_disp_zscore = (avg_dispersion - mean_60d) / std_60d
  strength = |avg_disp_zscore|

Economic logic:
  Q4 (high dispersion) = balanced market = high prices
  Q1 (low dispersion) = congestion = low prices
  Captures structural state

Horizon: Multi-week (relative long term)
"""

# ============================================================================
# BACKTEST METRICS - DEFINITIONS
# ============================================================================

"""
TOTAL RETURN
============
total_return = (final_equity - initial_capital) / initial_capital

Examples:
  - 18% = good
  - 5% = weak
  - -5% = loss


SHARPE RATIO
============
sharpe = (mean_excess_return / std_excess_return) * sqrt(252)

where:
  excess_return = daily_return - risk_free_rate
  risk_free_rate ≈ 2% annualized = 0.02 / 252 per day

Interpretation:
  - < 0.5: Weak
  - 0.5-0.75: Acceptable
  - 0.75-1.0: Good ← YOU ARE HERE
  - > 1.0: Excellent (rare)


MAX DRAWDOWN
============
drawdown_t = (portfolio_t - max_portfolio_0_to_t) / max_portfolio_0_to_t
max_drawdown = min(drawdown_t)

Examples:
  - -5% = excellent
  - -12% = acceptable
  - -25% = risky


WIN RATE
========
win_rate = num_winning_trades / total_trades

Examples:
  - 50% = normal (if gains > losses)
  - 55% = good
  - 60% = excellent

Note: Win rate is not enough. Example:
  - 60% winners but -1% avg
  - 40% losers but -10% avg
  → Win rate 60% but negative PnL (bad sizing)


CALMAR RATIO
============
calmar = annual_return / abs(max_drawdown)

Interpretation:
  - > 2.0: Excellent (good return, low risk)
  - > 1.0: Good
  - < 0.5: Weak


PROFIT FACTOR
==============
profit_factor = total_winning_pnl / abs(total_losing_pnl)

Examples:
  - 2.0 = 2x more gains than losses → good
  - 1.5 = good
  - 1.0 = break-even
  - < 1.0 = negative
"""

# ============================================================================
# COMMON USAGE
# ============================================================================

"""
LOAD, GENERATE SIGNALS, BACKTEST:
======================================

    from data_manager import DataManager
    from signal_generator import SignalGenerator
    from backtest_engine import BacktestEngine
    
    # 1. Load
    dm = DataManager('cape_front_month.csv', 'dispersion_case_study.csv')
    data = dm.get_clean_data()
    
    # 2. Signals
    sg = SignalGenerator(data)
    signals = sg.get_signals_dataframe()
    
    # 3. Backtest
    engine = BacktestEngine(signals, initial_capital=1_000_000, fee_bps=10)
    results_momentum = engine.backtest_strategy('signal_momentum', 'Momentum')
    results_regime = engine.backtest_strategy('signal_regime', 'Regime')
    
    # 4. Display
    print(f"Momentum: Sharpe={results_momentum['sharpe_ratio']:.2f}")
    print(f"Regime: Sharpe={results_regime['sharpe_ratio']:.2f}")


INTERACTIVE EXPLORATION (STREAMLIT):
====================================

    streamlit run streamlit_app.py
    
    # Then:
    # 1. Tab "Data Overview" → Check correlations
    # 2. Tab "Signal Explorer" → Understand signals
    # 3. Tab "Backtest Results" → See performance
    # 4. Tab "Economic Analysis" → Analyze why
    # 5. Tab "Strategy Comparison" → Compare both
"""

# ============================================================================
# CUSTOMIZATION
# ============================================================================

"""
MODIFY SIGNAL PARAMETERS
===================================

In SignalGenerator._compute_features():
  
  window = 60  # Rolling window for z-scores
             # Try: 30 (fast), 90 (stable), 120 (very stable)
  
  Q1/Q2/Q3/Q4 = pd.qcut(avg_dispersion, q=4)
              # Try: q=3 (3 regimes), q=5 (5 regimes)
  
  signal_momentum = sign(change_5d)
                  # Try: change_1d, change_10d
  
  regime = Q3+Q4 LONG, Q1 SHORT
        # Try: Q4 LONG only, Q1-Q2 SHORT


MODIFY BACKTEST PARAMETERS
===================================

In BacktestEngine.__init__():
  
  initial_capital = 1_000_000
                  # Try: 100k (small), 5M (large)
  
  transaction_fee_bps = 10
                      # Try: 0 (none), 5 (optimistic), 20 (pessimistic)
  
  max_drawdown_stop = 0.02
                    # Try: 0.01 (strict), 0.03 (loose), 0 (disable)


IMPORTANT: Always forward-test after customization!
"""

# ============================================================================
# KNOWN LIMITATIONS
# ============================================================================

"""
1. WEAK CORRELATION (r=0.27)
   - Explains only 7% of variance
   - Other factors dominate 93%

2. IN-SAMPLE BIAS
   - Data used to build = data used to test
   - Forward-test mandatory

3. CHANGING REGIMES
   - Correlation can break at any time
   - Rolling monitoring recommended

4. REAL FEES
   - Edge decreases rapidly with fees
   - 10 bps is conservative; real costs may be higher

5. OMITTED FACTORS
   - Iron ore price, USD rates, geopolitics, sentiment
   - Affect prices more than dispersion

6. DATA QUALITY
   - If CSV poorly formatted → invalid results
   - Check with validate_data()
"""

# ============================================================================
# DATA STRUCTURE (DETAIL)
# ============================================================================

"""
AFTER DataManager.get_clean_data():
===================================

Column               | Type     | Source            | Meaning
─────────────────────┼──────────┼───────────────────┼──────────────────
date                 | datetime | Input             | Date of day
price_5tc            | float    | cape_front_month  | 5TC Price $/day
cape_vessel_count    | int      | dispersion_csv    | # Capesize
cape_dispersion      | float    | dispersion_csv    | Cape Dispersion
vloc_vessel_count    | int      | dispersion_csv    | # VLOC
vloc_dispersion      | float    | dispersion_csv    | VLOC Dispersion
total_vessel_count   | int      | Calculated        | Cape + VLOC
avg_dispersion       | float    | Calculated        | Weighted by count
log_return_1d        | float    | Calculated        | Log-return price 1d
return_5d            | float    | Calculated        | Return price 5d
cape_disp_change_1d  | float    | Calculated        | Δ Cape disp 1d
cape_disp_change_5d  | float    | Calculated        | Δ Cape disp 5d
vloc_disp_change_1d  | float    | Calculated        | Δ VLOC disp 1d
vloc_disp_change_5d  | float    | Calculated        | Δ VLOC disp 5d
avg_disp_change_1d   | float    | Calculated        | Δ Avg disp 1d
avg_disp_change_5d   | float    | Calculated        | Δ Avg disp 5d


AFTER SignalGenerator.get_signals_dataframe():
==============================================

+ From columns above, adds:

Column               | Type     | Meaning
─────────────────────┼──────────┼────────────────────────────
avg_disp_zscore      | float    | Normalization avg_disp
cape_disp_zscore     | float    | Normalization cape_disp
vloc_disp_zscore     | float    | Normalization vloc_disp
price_zscore         | float    | Normalization price
momentum_zscore      | float    | Normalization momentum
disp_quartile        | str      | Q1/Q2/Q3/Q4 (regime)
signal_momentum      | int      | +1/-1/0
signal_momentum_strength | float | |momentum_zscore|
signal_regime        | int      | +1/-1/0
signal_regime_strength | float | |avg_disp_zscore|
"""

# ============================================================================
# FOR DEBUGGING
# ============================================================================

"""
IF SOMETHING GOES WRONG:
==========================

1. Check input data:
   >>> dm = DataManager(...)
   >>> summary = dm.get_data_summary()
   >>> print(summary)
   # Check: sample_size, date range, correlations
   
   >>> validation = dm.validate_data()
   >>> print(validation)
   # Check: all checks green?

2. Check signals are generated:
   >>> sg = SignalGenerator(clean_data)
   >>> signals = sg.get_signals_dataframe()
   >>> print(signals[['date', 'signal_momentum', 'signal_regime']].head(20))
   # Check: +1/-1/0 alternating? Not all 0?
   
   >>> stats = sg.get_signal_statistics()
   >>> print(stats)
   # Check: long_signals, short_signals, flat_signals > 0?

3. Check backtest:
   >>> engine = BacktestEngine(signals)
   >>> results = engine.backtest_strategy('signal_momentum', 'Test')
   >>> print(results)
   # Check: sharpe_ratio > 0? num_trades > 0? fees paid > 0?
   
   >>> trades = engine.get_trade_log()
   >>> print(trades.head(20))
   # Check: entry/exit dates, net_pnl realistic?
   
   >>> equity_vals, equity_dates = engine.get_equity_curve()
   >>> print(f"Start: {equity_vals[0]}, End: {equity_vals[-1]}")
   # Check: curve monotone increasing/decreasing?

4. Check Streamlit:
   >>> streamlit run streamlit_app.py --logger.level=debug
   # Wait 30s on first launch (cache)
   # Check errors in console
"""

print(__doc__)
