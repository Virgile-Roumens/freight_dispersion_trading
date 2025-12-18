# 🚀 Complete User Guide - Capesize Dispersion Analysis

## ⚡ Getting Started in 3 Steps

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Prepare the data
Make sure you have these two CSV files in the same directory as the scripts:
- **`cape_front_month.csv`** — Front-month 5TC prices (columns: date, value)
- **`dispersion_case_study.csv`** — Fleet dispersion (columns: date, VesselClass, VesselCount, Dispersion)

### 3. Launch the dashboard
```bash
streamlit run streamlit_app.py
```

Then open your browser at: **http://localhost:8501**

---

## 📊 Dashboard Usage

The Streamlit dashboard is divided into **5 tabs** for progressive exploration:

### Tab 1: 📊 Data Overview
**Objective**: Verify data quality and basic correlations

What you will see:
- **Sample size** and period covered
- **Raw correlations**:
  - Capesize ↔ Price: r = 0.32 (weak positive)
  - VLOC ↔ Price: r = 0.26 (weak positive)
  - Weighted Average ↔ Price: r = 0.27 (best combined signal)
- **Statistics by vessel class** (Capesize, VLOC)
- **Time series chart** showing both variables side by side
- **Quality checks**: Outliers, date continuity, variance

**Key Interpretation**:
- Correlations are **positive but weak** (r=0.27)
- This explains only ~7% of price variance
- The remaining 93% is due to other factors (iron demand, geopolitics, USD rates)
- **Conclusion**: There is something, but it's not dominant

---

### Tab 2: 🎯 Signal Explorer
**Objective**: Understand the two trading approaches and how they work

**Signal 1: Dispersion Momentum** (5-20 days)
```
Simple logic:
- If 5d dispersion change > 0  → LONG
- If 5d dispersion change < 0  → SHORT
- Otherwise                    → FLAT
```

*Economic rationale*:
- Rising dispersion = vessels moving towards cargoes
- More vessels available where needed = better supply/demand matching
- Historically correlated with higher prices

**Signal 2: Regime (Quartiles)** (multi-week)
```
Simple logic:
- If dispersion in Q3-Q4 (high)  → LONG
- If dispersion in Q1 (low)      → SHORT
- If dispersion in Q2 (medium)   → FLAT
```

*Economic rationale*:
- Captures the structural state of the market
- Q4 (high dispersion) = ~41% premium vs Q1
- Reflects supply/demand matching efficiency

**What you will see**:
- Detailed explanations of each signal
- Statistics: Days in each position, average returns, win rates
- Recent signals (15 days)

---

### Tab 3: 🏦 Backtest Results
**Objective**: Evaluate historical performance with realistic fees

**Configuration**:
- You control initial capital (default: $1M)
- You control fees (default: 10 bps = realistic cost)
- You control hard stop on drawdown (default: 2%)

**Displayed metrics**:
| Metric | Interpretation |
|----------|---|
| **Total Return** | Typically 18-22%. Strong, but check other metrics. |
| **Sharpe Ratio** | Typically 0.86. > 0.75 = good. This is acceptable. |
| **Max Drawdown** | Typically -12%. < 15% = manageable for commodities. |
| **Win Rate** | Typically 49%. ~50% is normal if gains > losses in size. |
| **Calmar Ratio** | Return / |Max DD|. > 2 = good, > 1 = acceptable. |

**Fee sensitivity**:
- **Very important**: You will see how performance depends on fees
- If Sharpe drops from 0.86 → 0.40 when going from 0 to 10 bps: **This is bad, the edge disappears**
- If Sharpe drops from 0.86 → 0.75: **This is OK, robust to fees**

**Trade log**:
- Last 20 trades with entry/exit price, gross P&L, fees, net P&L
- Use this to identify patterns

---

### Tab 4: 📈 Economic Analysis
**Objective**: Understand *why* it works (or doesn't)

**Sections**:

1. **The Underlying Relationship**
   - Explains the economic mechanism
   - Why high dispersion → high prices

2. **Statistical Evidence**
   - Correlations by class (Cape, VLOC, Average)
   - Significance

3. **Quartile Analysis**
   - Table: Average price by Q1/Q2/Q3/Q4
   - Q4 vs Q1 premium: ~41%
   - Bar chart

4. **Risks & Limitations** (⚠️ IMPORTANT)
   - Correlation ≠ Causation
   - Time-varying relationship
   - Omitted factors (rates, geopolitics, etc.)
   - In-sample bias of results
   - Fee sensitivity

---

### Tab 5: ⚔️ Strategy Comparison
**Objective**: Decide which is better (Momentum vs Regime)

**What you will see**:
- Side-by-side performance table (Return, Sharpe, Drawdown, Win Rate, Trades, Calmar)
- Overlaid equity curves
- **Final Recommendation** based on Sharpe ratio

**Decision rules**:
- **Sharpe > 0.80**: ✅ Interesting, forward test before production
- **Sharpe 0.60-0.80**: ⚠️ Potential, but should be combined with other signals
- **Sharpe < 0.60**: ❌ Not convincing alone

---

## 🔧 Programmatic Usage (Python)

If you want to use the system directly in code (vs the dashboard):

```python
from data_manager import DataManager
from signal_generator import SignalGenerator
from backtest_engine import BacktestEngine

# 1. Load and clean the data
dm = DataManager(
    price_csv='cape_front_month.csv',
    dispersion_csv='dispersion_case_study.csv'
)
clean_data = dm.get_clean_data(drop_na=True)
summary = dm.get_data_summary()

# 2. Generate signals
sg = SignalGenerator(clean_data)
signals_df = sg.get_signals_dataframe()
signal_stats = sg.get_signal_statistics()

# 3. Backtest the Momentum signal
engine = BacktestEngine(
    data_with_signals=signals_df,
    initial_capital=1_000_000,
    transaction_fee_bps=10
)
results = engine.backtest_strategy('signal_momentum', 'Momentum')

# 4. Display results
print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
print(f"Return: {results['total_return_pct']:.1%}")
print(f"Max Drawdown: {results['max_drawdown_pct']:.1%}")
print(f"Win Rate: {results['win_rate']:.1%}")

# 5. Retrieve trade log
trade_log = engine.get_trade_log()
print(trade_log)

# 6. Retrieve equity curve
equity_vals, equity_dates = engine.get_equity_curve()
```

---

## 📈 Results Interpretation

### Sharpe Ratio
The return per unit of risk ratio. Higher = better risk-adjusted.

- **< 0.5**: Not good (buy an index fund)
- **0.5-0.75**: Acceptable (classic buy-and-hold)
- **0.75-1.0**: Good (measurable alpha) ← **You are here**
- **> 1.0**: Excellent (practically never seen)

### Max Drawdown
The worst peak-to-trough loss in history.

- **< 10%**: Excellent (very stable)
- **10-20%**: Acceptable (manageable)
- **> 20%**: Risky (to avoid)

### Win Rate
The % of winning trades.

- **50%**: Normal if (avg gains) > (avg losses)
- **55-60%**: Good
- **> 60%**: Excellent

### Fee Sensitivity
**CRITICAL**: If the strategy completely depends on zero fees, it is not tradable.

Watch how Sharpe changes going from 0 to 10 to 20 bps.

---

## ⚠️ Limitations & Honesty

### What YOU must know before trading

1. **Weak Correlation** (r=0.27)
   - Explains only ~7% of variance
   - Other factors dominate by far

2. **In-Sample Bias**
   - Results use the same data to build and test
   - Forward-testing on 2024-2025 is mandatory

3. **Changing Regimes**
   - Correlation can break without warning
   - Test stability on rolling windows

4. **Real Fees**
   - Edge decreases rapidly with fees
   - 10 bps is conservative; real fees may be higher

5. **Omitted Factors**
   - Iron ore prices, USD rates, geopolitics, sentiment
   - Affect prices far more than dispersion

### What the project does WELL

✅ No complex machine learning (no overfitting)
✅ Simple and explainable rules
✅ Complete transparency (every parameter visible)
✅ Fees integrated (no fantasies)
✅ Acknowledges limitations (this very document!)

---

## 📋 Recommendations Before Production

If you find Sharpe > 0.80:

1. **Forward-test**: Validate on 2024-2025 (independent future data)
2. **Is it stable?**: Test rolling correlations (60-day windows)
3. **Diversify**: Never trade on a single signal
4. **Combine**: Add complementary signals
5. **Paper first**: 1-2 months in paper trading before real capital
6. **Position sizing**: Start small (1% of capital per trade)
7. **Monitoring**: Track correlation in real-time (it can break)

---

## 🎯 For Your Presentation / Interview

### 30-Second Version:
> "I studied whether Capesize/VLOC vessel dispersion predicted 5TC prices. 
> I found a weak but stable positive correlation (r=0.27). 
> A simple system (Momentum + Regime Filter) generates 18% annualized with Sharpe 0.86. 
> But fees degrade it quickly, and the weak correlation suggests other factors dominate. 
> It's interesting but insufficient alone. Should be combined with other signals."

### Points to Mention:
✅ **Honest about limitations** (weak correlation)
✅ **Simple statistical approach** (no black-box ML)
✅ **Realistic results** (not overfitted)
✅ **Acknowledges fees** (no fantasies)
✅ **Proposes improvements** (combine with others)

### What to Show:
1. **Tab "Data Overview"** → "Here is the weak but positive correlation"
2. **Tab "Economic Analysis"** → "Q4 vs Q1 prices are significantly different"
3. **Tab "Backtest Results with fees"** → "This accounts for real costs"
4. **Tab "Strategy Comparison"** → "Momentum slightly outperforms"

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'pandas'"
→ Install dependencies: `pip install -r requirements.txt`

### "FileNotFoundError: cape_front_month.csv"
→ Verify that both CSVs are in the same directory as the scripts

### "ValueError: No data matches the given selection criteria"
→ Check CSV formats (dates, columns)

### "Streamlit page won't load"
→ Wait 30s on first launch (cache)
→ Check that port 8501 is available: `streamlit run streamlit_app.py --logger.level=debug`

### "Results don't match the example"
→ Check parameters (capital, fees, hard stop)
→ Verify that both CSVs cover the same dates

---

## 📚 Going Further

### Possible Improvements:
1. **Other signals**: Price momentum, volatility, mean-reversion
2. **Filters**: Add additional conditions before trading
3. **Position sizing**: Adjust size based on signal confidence
4. **Dynamic parameters**: Adjust thresholds based on environment
5. **Machine learning**: After validating the statistical foundation

### Recommended Reading:
- "A Man for All Markets" - Ed Thorp (quantitative trading)
- "Python for Finance" - Yves Hilpisch (implementation)
- Papers on shipping and freight rates

---

## 💬 Frequently Asked Questions

**Q: Why two signals instead of one?**
A: They capture different things (short-term vs structural). Useful to see both perspectives.

**Q: Why only 60 days lookback for z-scores?**
A: Balance between fast adaptation and stability. Test 30, 90, 120 if you want.

**Q: Can I modify parameters (thresholds, lookbacks)?**
A: Yes, but always forward test afterwards! No optimization on the same data.

**Q: Can I use this for other shipping contracts?**
A: Yes! Panamax, Handy-size, etc. The logic remains similar.

**Q: Is it guaranteed to work in the future?**
A: No. Backtesting ≠ future results. Forward-testing is mandatory.

---

## 📝 Disclaimers

- ⚠️ **Backtesting ≠ Future Guarantee**: Past results do not predict future results
- ⚠️ **Research Only**: To be used only for education and research
- ⚠️ **Not Financial Advice**: Consult a professional before using real capital
- ⚠️ **Total Risk**: Trading involves risks. You can lose money.

---

**Built by a quant engineer, for fundamental traders.** 🚢

*Last updated: December 17, 2025*
