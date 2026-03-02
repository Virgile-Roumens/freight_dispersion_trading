# ⚓ Freight Analytics Platform

**Capesize Dispersion Intelligence & 5TC Price Prediction Engine**

A professional-grade quantitative trading tool for freight market analysis. This platform combines vessel positioning data with forward freight pricing to generate economically-grounded trading signals with institutional-quality performance metrics.

---

## 🎯 Overview

The Freight Analytics Platform analyzes the relationship between Capesize vessel dispersion patterns and 5TC Forward Freight Agreement (FFA) prices. Using advanced statistical methods and quantitative backtesting, it provides:

- **Dual trading signals** — Inverted Momentum + Mean Reversion (accordion effect)
- **Economic logic** — HIGH dispersion = BEARISH, LOW dispersion = BULLISH
- **Lead-lag cross-correlation analysis** — Is dispersion a leading or lagging indicator?
- **Institutional-grade performance metrics** (Sharpe ratio with dynamic risk-free rate, annualized returns)
- **Comprehensive market intelligence** (correlation analysis, Granger causality tests, regime detection)
- **Interactive optimization tools** (lag testing, fee sensitivity, parameter tuning)
- **Side-by-side strategy comparison** with overlaid equity curves
- **Professional interface design** (navy #132c68, gold #f4c430, teal #5eb8e8)

---

## 💡 Economic Logic (Expert-Validated)

| Dispersion State | Fleet Positioning | Supply Dynamics | Price Impact |
|---|---|---|---|
| **HIGH** (rising) | Fleet well spread globally | Efficient supply, cargo easily matched | **BEARISH** — prices fall |
| **LOW** (falling) | Fleet concentrated regionally | Scarcity in key loading areas | **BULLISH** — prices rise |


---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip package manager
- Internet connection (for FRED API)

### Installation

1. **Clone or download the repository**

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Verify data files are in place**
```
freight_project/
├── data/
│   ├── cape_front_month.csv
│   └── dispersion_case_study.csv
```

4. **Launch the application**
```bash
streamlit run streamlit_app.py
```

The app will open automatically in your browser at `http://localhost:8501`

---

## 📊 Key Features

### 1. **Data Overview & Market Intelligence** (📊 Tab)
- Dataset profiling and quality validation
- Distribution analysis (5TC prices, dispersion metrics)
- Rolling correlation dynamics
- **Granger causality testing** — Does dispersion predict prices?
- Regime analysis by dispersion quartiles

### 2. **Signal Explorer** (🎯 Tab)
- **Two complementary signals**:
  - **Inverted Momentum** — Trades short-term directional changes (60-day z-score window)
  - **Mean Reversion** — Fades extreme deviations from 120-day equilibrium (accordion effect)
- Toggle to overlay both signals on the price chart
- Signal statistics and latest values for both strategies
- Detailed economic explanations for each signal

### 3. **Backtest Results** (🏬 Tab)
- **Strategy selector**: Inverted Momentum / Mean Reversion / Compare Both
- **Multi-threshold position sizing** (25%, 50%, 75%, 100%)
- Persistence filters (2-day confirmation) and volatility filters
- **Side-by-side comparison** table and overlaid equity curves
- **Dynamic risk-free rate** from FRED API (US 10Y Treasury)
- Trade-level P&L analysis and fee sensitivity
- Export-ready results (Excel/CSV)

### 4. **Economic Analysis** (📈 Tab)
- Dispersion quartile regime analysis
- Distribution plots and Granger causality tests
- Parameter tuning recommendations

### 5. **Lead-Lag Analysis** (🔬 Tab) — *NEW*
- **Cross-correlation bar chart** (lag = −20 to +20 days)
- Toggle between series pairs: `avg_dispersion` vs `price_5tc`, `avg_disp_change_5d` vs `return_5d`
- Peak correlation highlighted with automatic interpretation
- Answers: *"Does dispersion lead, lag, or move contemporaneously with prices?"*

---

## 📁 Project Structure

```
freight_project/
│
├── data/                           # Data files
│   ├── cape_front_month.csv        # 5TC FFA prices (daily)
│   └── dispersion_case_study.csv   # Vessel dispersion data
│
├── assets/                         # Visual assets
│
├── export/                         # Backtest exports (auto-created)
│
├── streamlit_app.py                # Main dashboard interface
├── data_manager.py                 # Data loading & validation
├── signal_generator.py             # Trading signal logic
├── backtest_engine.py              # Portfolio simulation engine
│
├── requirements.txt                # Python dependencies
├── README.md                       # This file
```

---

## ⚙️ Configuration

### Adjustable Parameters

**Sidebar Controls:**
- **Signal Lag** (0-20 days): Test if dispersion leads prices by N days
- **Mean-Reversion Threshold** (0.5σ–2.5σ, step 0.25): Minimum z-score deviation from 120-day mean to trigger mean-reversion signal
- **Strategy to Backtest**: Inverted Momentum / Mean Reversion / Compare Both
- **Initial Capital** ($100k–$10M): Portfolio size for backtesting
- **Transaction Fees** (0-50 bps): Round-trip trading costs

### FRED API Integration

The platform fetches dynamic risk-free rates from the Federal Reserve Economic Data (FRED) API:

- **API Key**: Embedded in `backtest_engine.py` (dddf15f3c59a3d9c5c331ecabed8a160)
- **Data Series**: DGS10 (10-Year Treasury Constant Maturity Rate)
- **Purpose**: Accurate Sharpe ratio calculation
- **Fallback**: 2% if API unavailable

---

## 📈 Performance Metrics

### Key Indicators

| Metric | Description |
|--------|-------------|
| **Total Return** | Cumulative P&L over backtest period |
| **Annualized Return** | Geometric mean annual return (252 trading days) |
| **Sharpe Ratio** | Risk-adjusted return using dynamic RF rate |
| **Max Drawdown** | Worst peak-to-trough decline |
| **Win Rate** | % of profitable trades |

### Trading Signal Logic

#### Signal 1 — Inverted Momentum
```python
# Direction: INVERTED from naive interpretation
if avg_disp_change_5d < 0:  signal = LONG   # Falling dispersion → bullish
if avg_disp_change_5d > 0:  signal = SHORT  # Rising dispersion  → bearish

# Multi-threshold position sizing (based on |momentum_zscore|)
if |z| >= 2.5: position = ±100%   # Extreme
if |z| >= 2.0: position = ±75%    # Very Strong
if |z| >= 1.5: position = ±50%    # Strong
if |z| >= 1.0: position = ±25%    # Medium
else:          position = 0%      # Flat (signal too weak)

# Filters: 2-day persistence, |price_zscore| < 2.0, 90-day regime detection
# Rolling window: 60 days
```

#### Signal 2 — Mean Reversion (Accordion Effect)
```python
# Z-score vs 120-day rolling mean
avg_disp_mr_zscore = (avg_dispersion - rolling_mean_120d) / rolling_std_120d

# Direction: FADE THE EXTREMES
if avg_disp_mr_zscore > +threshold:  signal = LONG   # Above mean → expect concentration → bullish
if avg_disp_mr_zscore < -threshold:  signal = SHORT  # Below mean → expect dispersion  → bearish

# Same graduated sizing, persistence filter, and volatility filter as momentum
# Threshold configurable via sidebar (default: 1.0σ)
# Rolling window: 120 days
```

#### Economic Rationale (Expert-Validated)
- **HIGH/rising dispersion** = fleet well-positioned globally = efficient supply = **BEARISH** for rates
- **LOW/falling dispersion** = fleet concentrated = regional scarcity = **BULLISH** for rates
- **Accordion effect**: extreme dispersion reverts to equilibrium — fade the extremes


## 📊 Data Sources

### 1. Cape Front-Month (C+1MON)
- **Source**: Forward Freight Agreement contracts
- **Frequency**: Daily
- **Unit**: USD per day
- **Routes**: Capesize vessel routes (primarily iron ore)

### 2. Vessel Dispersion
- **Calculation**: Weighted average by vessel count
  ```
  avg_dispersion = (Cape_Disp × Cape_Count + VLOC_Disp × VLOC_Count) / Total_Count
  ```
- **Vessels**: Capesize (100-180k DWT) + VLOC (200-400k DWT)
- **Meaning**: Geographic spread of vessel positions globally

---

## 🔧 Technical Details

### Dependencies

```
pandas>=2.0.0          # Data manipulation
numpy>=1.24.0          # Numerical computing
streamlit>=1.28.0      # Web dashboard
plotly>=5.17.0         # Interactive charts
scipy>=1.10.0          # Statistical functions
statsmodels>=0.14.0    # Granger causality tests
fredapi>=0.5.0         # Federal Reserve data
openpyxl>=3.1.0        # Excel export
```

### Architecture

**3-Layer Design:**
1. **Data Layer** (`data_manager.py`) — Loading, validation, quality checks
2. **Signal Layer** (`signal_generator.py`) — Dual signal generation (inverted momentum + mean reversion), lead-lag cross-correlation analysis
3. **Execution Layer** (`backtest_engine.py`) — Position sizing, P&L tracking, metrics (supports any `signal_*` column)

**Performance:**
- Data cached with `@st.cache_resource` for fast reloads
- Vectorized pandas operations
- Lazy evaluation for optimization loops

---

## 📤 Export Functionality

Export complete backtest results in Excel or CSV format:

**Included Sheets/Files:**
1. **Summary** - All performance metrics, configuration
2. **Trade Log** - Trade-by-trade breakdown with P&L
3. **Equity Curve** - Daily portfolio values

**Export Location:** `export/` folder (auto-created)

---

## 🧪 Testing & Validation

### Data Quality Checks

The platform automatically validates:
- ✅ No missing values (NaN detection)
- ✅ Outlier detection (>5σ flagged)
- ✅ Date continuity (gap analysis)
- ✅ Sufficient variance (non-constant series)

### Statistical Tests

- **Granger Causality**: Tests if dispersion predicts prices
- **Rolling Correlation**: Identifies regime changes
- **Quartile Analysis**: Economic validation of dispersion impact
- **Lead-Lag Cross-Correlation**: Measures whether dispersion leads, lags, or is contemporaneous with price movements across ±20 day lags

---

## 💡 Usage Tips

### For Traders

1. **Start with Data Overview** - Understand correlations before trading
2. **Check Granger tests** - Verify predictive power at different lags
3. **Test fee sensitivity** - Ensure strategy survives realistic costs
4. **Optimize lag parameter** - Find best predictive horizon
5. **Monitor regime changes** - Relationship may not be stable

### For Analysts

1. **Rolling correlation** — Identify periods when strategy works/fails
2. **Quartile analysis** — Validate economic intuition (high disp = *lower* rates)
3. **Lead-lag tab** — Check if dispersion is a leading or lagging indicator for your chosen series pair
4. **Compare Both strategies** — Evaluate momentum vs mean reversion side-by-side
5. **Trade log analysis** — Understand win/loss patterns
6. **Export for R/Python** — Further analysis in your preferred tools

### For Risk Managers

1. **Max drawdown tracking** - Understand worst-case scenarios
2. **Win rate analysis** - Balance frequency vs magnitude
3. **Fee sensitivity** - Stress test with higher transaction costs
4. **Sharpe ratio validation** - Compare to benchmarks (>1.0 = excellent)

---

## 🚧 Known Limitations

### Data Limitations
- Historical data only (2016-2025)
- Daily frequency (no intraday)
- No cargo data or fundamentals
- Limited to Capesize/VLOC vessels

### Strategy Limitations
- **Non-stationary relationship** — Correlation changes over time
- **Low R²** (~7%) — Most price variance unexplained by dispersion alone
- **Transaction costs matter** — Edge is thin, especially for momentum
- **No risk controls** — No stop-loss, max position limits
- **Single-factor model** — Both signals derive from dispersion; diversify with other factors

### Technical Limitations
- Requires internet for FRED API
- Single-factor model (dispersion only)
- No execution slippage modeling
- Assumes perfect liquidity

---

## 🔮 Future Enhancements

### Potential Improvements

1. **Multi-factor signals** — Add freight fundamentals (iron ore, PMI), sentiment, macro data
2. **Ensemble strategy** — Combine inverted momentum + mean reversion into a single weighted signal
3. **Portfolio construction** — Extend to other freight routes (Panamax, Supramax, Handysize)
4. **Risk management** — Position limits, stop-losses, volatility targeting, max drawdown circuit breakers
5. **Real-time data** — Live AIS feeds, automatic signal generation
6. **Alert system** — Email/SMS notifications for strong signals
7. **Out-of-sample validation** — Walk-forward backtesting to combat in-sample overfitting

---

## 📚 Documentation

- **README.md** - This file (overview, installation, usage)
- **PERFORMANCE_METRICS_UPGRADE.md** - FRED API integration details
- **ARCHITECTURE_QUICK_REF.py** - Code architecture reference

---

## 🤝 Support

For questions, issues, or feature requests:

- **Primary Contact**: Virgile ROUMENS
