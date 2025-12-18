# ⚓ Engelhart Freight Analytics Platform

**Capesize Dispersion Intelligence & 5TC Price Prediction Engine**

A professional-grade quantitative trading tool for freight market analysis, built for Engelhart Commodities Trading's freight desk. This platform combines vessel positioning data with forward freight pricing to generate momentum-based trading signals with institutional-quality performance metrics.

---

## 🎯 Overview

The Engelhart Freight Analytics Platform analyzes the relationship between Capesize vessel dispersion patterns and 5TC Forward Freight Agreement (FFA) prices. Using advanced statistical methods and quantitative backtesting, it provides:

- **Multi-threshold momentum signals** based on vessel positioning
- **Institutional-grade performance metrics** (Sharpe ratio with dynamic risk-free rate, annualized returns)
- **Comprehensive market intelligence** (correlation analysis, Granger causality tests, regime detection)
- **Interactive optimization tools** (lag testing, fee sensitivity, parameter tuning)
- **Professional Engelhart branding** (navy #132c68, gold #f4c430, teal #5eb8e8)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip package manager
- Internet connection (for FRED API)

### Installation

1. **Clone or download the repository**
```bash
cd c:\Users\Virgile ROUMENS\Desktop\Engelhart\freight_project
```

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
├── assets/
│   └── engelhart_logo.png
```

4. **Launch the application**
```bash
streamlit run streamlit_app.py
```

The app will open automatically in your browser at `http://localhost:8501`

---

## 📊 Key Features

### 1. **Data Overview & Market Intelligence**
- Dataset profiling and quality validation
- Distribution analysis (5TC prices, dispersion metrics)
- Rolling correlation dynamics
- **Granger causality testing** - Does dispersion predict prices?
- Regime analysis by dispersion quartiles

### 2. **Strategy Engine & Performance**
- **Multi-threshold position sizing** (25%, 50%, 75%, 100%)
- Persistence filters (2-day confirmation)
- Volatility filters (blocks extreme markets)
- **Dynamic risk-free rate** from FRED API (US 10Y Treasury)
- **Annualized returns** for benchmarking
- Trade-level P&L analysis
- Fee sensitivity analysis

### 3. **Optimization & Analysis**
- **Signal lag optimization** (0-20 days)
- Economic regime analysis
- Parameter tuning recommendations
- Export-ready results (Excel/CSV)

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
│   └── engelhart_logo.png          # Company logo
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
├── ENGELHART_DESIGN_SYSTEM.md      # Brand guidelines
└── PERFORMANCE_METRICS_UPGRADE.md  # Metrics documentation
```

---

## ⚙️ Configuration

### Adjustable Parameters

**Sidebar Controls:**
- **Signal Lag** (0-20 days): Test if dispersion leads prices by N days
- **Initial Capital** ($100k-$10M): Portfolio size for backtesting
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

**Momentum Strategy:**
```python
# Calculate z-score of dispersion change
z_score = (dispersion_change - mean) / std

# Multi-threshold position sizing
if |z_score| >= 2.5: position = ±100%  # Extreme
if |z_score| >= 2.0: position = ±75%   # Very Strong
if |z_score| >= 1.5: position = ±50%   # Strong
if |z_score| >= 1.0: position = ±25%   # Medium
else: position = 0%  # Flat

# Filters
- 2-day persistence required
- No trading when |price_z_score| > 2.0
- 90-day lookback for regime detection
```

**Rationale:** High dispersion = vessels well-positioned globally → bullish freight rates

---

## 🎨 Engelhart Brand Identity

### Color Palette

- **Primary Navy**: #132c68 (RGB: 19, 44, 104) - Headers, primary elements
- **Gold**: #f4c430 (RGB: 244, 196, 48) - Accents, highlights
- **Teal**: #5eb8e8 (RGB: 94, 184, 232) - Secondary data, info boxes

### Brand Values

- **Be Bold** - Confident analysis, strong visual identity
- **Be Collaborative** - Transparent data, clear communication
- **Be Proactive** - Actionable insights, forward-looking analytics

### Design Philosophy

Professional trading desk aesthetic inspired by Bloomberg Terminal, with:
- Gradient backgrounds
- Professional shadows and depth
- Clear visual hierarchy
- Institutional typography

---

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
1. **Data Layer** (`data_manager.py`) - Loading, validation, quality checks
2. **Signal Layer** (`signal_generator.py`) - Momentum calculation, filters
3. **Execution Layer** (`backtest_engine.py`) - Position sizing, P&L tracking, metrics

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

---

## 💡 Usage Tips

### For Traders

1. **Start with Data Overview** - Understand correlations before trading
2. **Check Granger tests** - Verify predictive power at different lags
3. **Test fee sensitivity** - Ensure strategy survives realistic costs
4. **Optimize lag parameter** - Find best predictive horizon
5. **Monitor regime changes** - Relationship may not be stable

### For Analysts

1. **Rolling correlation** - Identify periods when strategy works/fails
2. **Quartile analysis** - Validate economic intuition (high disp = high rates)
3. **Trade log analysis** - Understand win/loss patterns
4. **Export for R/Python** - Further analysis in your preferred tools

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
- **Non-stationary relationship** - Correlation changes over time
- **Low R²** (~7%) - Most price variance unexplained
- **Transaction costs matter** - Edge is thin
- **No risk controls** - No stop-loss, max position limits

### Technical Limitations
- Requires internet for FRED API
- Single-factor model (dispersion only)
- No execution slippage modeling
- Assumes perfect liquidity

---

## 🔮 Future Enhancements

### Potential Improvements

1. **Multi-factor signals** - Add freight fundamentals, sentiment, macro data
2. **Machine learning** - Random forests, gradient boosting for non-linear patterns
3. **Portfolio construction** - Combine with other freight routes (Panamax, Supramax)
4. **Risk management** - Position limits, stop-losses, volatility targeting
5. **Real-time data** - Live feeds, automatic signal generation
6. **Alert system** - Email/SMS notifications for strong signals

---

## 📚 Documentation

- **README.md** - This file (overview, installation, usage)
- **ENGELHART_DESIGN_SYSTEM.md** - Complete brand guidelines (6,000+ words)
- **PERFORMANCE_METRICS_UPGRADE.md** - FRED API integration details
- **ARCHITECTURE_QUICK_REF.py** - Code architecture reference

---

## 🤝 Support

For questions, issues, or feature requests:

- **Primary Contact**: Virgile ROUMENS
- **Organization**: Engelhart Commodities Trading
- **Department**: Freight Trading Desk

---

## 📄 License

**Proprietary - Engelhart Commodities Trading**

This software is the property of Engelhart Commodities Trading and is intended for internal use only. Unauthorized distribution, modification, or commercial use is prohibited.

---

## 🏆 Credits

**Developed for Engelhart Commodities Trading**

- **Strategy Design**: Freight Trading Desk
- **Quantitative Analysis**: Advanced statistical methods, institutional metrics
- **Brand Integration**: Engelhart Design System
- **Data Sources**: FFA market data, vessel positioning intelligence

---

<div align="center">

**⚓ ENGELHART COMMODITIES TRADING**

*Where the Future Trades*

🌊 **Be Bold • Be Collaborative • Be Proactive** 🌊

</div>
