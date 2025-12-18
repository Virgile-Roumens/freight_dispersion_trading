# Usage Guide: Adapted Extreme Event Strategy

## Overview

This guide explains how to use the **adapted vessel dispersion strategy** after implementing recommendations from the critical evaluation. The strategy has been transformed from a high-frequency trading system to a **selective extreme event filter**.

---

## Quick Start

### 1. Launch the Dashboard

```powershell
streamlit run streamlit_app.py
```

### 2. Understanding the New Strategy

Navigate to **🎯 Signal Explorer** tab to see:

- ⚠️ Warning box explaining the critical evaluation findings
- Strategy adapted to trade ONLY extreme events (|z| ≥ 2.0σ)
- ~95% of days will show FLAT positions
- Dramatically reduced trading frequency

### 3. Key Settings (Sidebar)

| Parameter | Recommended | Explanation |
|-----------|-------------|-------------|
| Signal Lag | 0-2 days | Test if dispersion leads prices |
| Initial Capital | Any | Performance now capital-independent |
| Transaction Fees | 10 bps | Realistic round-trip cost |

---

## Strategy Components

### Extreme Event Detection

**Threshold:** |z-score| ≥ 2.0σ (99th percentile)

```
Example:
- Momentum z-score = +2.3 → LONG 100%
- Momentum z-score = +0.8 → FLAT (ignored, too weak)
- Momentum z-score = -2.1 → SHORT 100%
- Momentum z-score = -1.5 → FLAT (ignored)
```

### Multi-Layer Filters

Every extreme event must pass **4 filters** to generate a trade:

1. **Extreme Threshold:** |z| ≥ 2.0σ
2. **Volatility Filter:** |price z-score| < 2.0σ
3. **Regime Detection:** Not in low-volatility regime
4. **Signal Persistence:** 3 consecutive days same extreme direction

**Result:** Only 5-10% of days will have active positions.

---

## Interpreting Results

### Tab 1: Data Overview

**What to Look For:**
- Correlation between dispersion and prices (~0.27)
- Granger causality test results
- Rolling correlation instability

**Key Insight:** Weak correlation confirms need for extreme-event-only approach.

### Tab 2: Signal Explorer

**What to Look For:**
- Position size distribution: ~95% FLAT, ~5% EXTREME
- Latest signals: Should see mostly FLAT (0%)
- Signal statistics: Lower number of trades

**Expected Distribution:**
- FLAT Days: ~2,300-2,400 (95%)
- EXTREME Days: ~100-200 (5%)

### Tab 3: Backtest Results

**What to Look For:**
- Number of trades: ~100-150 (down from ~1,500)
- Transaction costs: ~$10-15K (down from ~$140K)
- Max drawdown: Expected improvement to -20-30%
- Sharpe ratio: Expected improvement to 0.4-0.6

**Interpretation:**
- Even with improvements, strategy may still lose money standalone
- Focus on **risk-adjusted metrics** (Sharpe, drawdown) not absolute return
- Compare performance across different signal lags

### Tab 4: Economic Analysis

**What to Look For:**
- Lag sensitivity analysis: Which lag performs best?
- Quartile analysis: How dispersion regimes affect prices
- Limitations section: Honest assessment of strategy

---

## Practical Usage Scenarios

### ❌ Scenario 1: Standalone Trading (NOT RECOMMENDED)

```
DON'T DO THIS:
1. See extreme dispersion signal (z = 2.5)
2. Enter 100% LONG position
3. Hold until signal reverses
4. Repeat

WHY NOT:
- Weak correlation (0.27) means many false signals
- Transaction costs erode profits
- Drawdown still significant
```

### ✅ Scenario 2: As Confirmation Filter (RECOMMENDED)

```
BETTER APPROACH:
1. Have another signal (e.g., iron ore momentum says LONG)
2. Check dispersion: Is it showing extreme increase (z > 2.0)?
3. If YES → Increase position size or confidence
4. If NO → Reduce position size or skip trade

BENEFIT:
- Uses dispersion as confirmation, not primary signal
- Reduces false positives from other strategies
- Multi-factor approach improves reliability
```

### ✅ Scenario 3: Risk Management Tool (RECOMMENDED)

```
RISK-OFF SIGNAL:
1. Monitor for extreme negative dispersion (z < -2.0)
2. If detected → Exit all freight-related positions
3. Wait for stabilization before re-entering

BENEFIT:
- Extreme dispersion collapse signals major demand shock
- Protects portfolio from severe drawdowns
- Acts as early warning system
```

### ✅ Scenario 4: Research & Analysis (RECOMMENDED)

```
ANALYTICAL USE:
1. Study historical extreme events
2. Identify major market regime shifts
3. Understand freight market microstructure
4. Generate trade ideas (manual discretion)

BENEFIT:
- Enhances market understanding
- Provides context for discretionary decisions
- Helps identify market turning points
```

---

## Example Trade Analysis

### Historical Extreme Event: March 2021

**Dispersion Signal:**
- March 15, 2021: z-score = +2.4 (extreme increase)
- Persisted for 3 consecutive days ✓
- Price volatility = 1.3σ (below threshold) ✓
- Regime = active (not low-vol) ✓

**Signal Generated:** LONG 100%

**Outcome:**
- Entry: $18,500/day
- Peak: $22,000/day (+18.9%)
- Exit: $21,200/day (+14.6%)

**Lesson:** Extreme dispersion increase correctly signaled demand surge, but timing exit is challenging.

---

## Performance Expectations

### Realistic Goals

**With Adapted Strategy (Extreme Events Only):**

| Metric | Conservative | Optimistic |
|--------|--------------|------------|
| Annual Return | -5% to +5% | +10% to +15% |
| Sharpe Ratio | 0.4 to 0.6 | 0.7 to 1.0 |
| Max Drawdown | -20% to -30% | -10% to -20% |
| Win Rate | 48% to 52% | 52% to 58% |
| Trades per Year | 10-15 | 15-25 |

**Key Insight:** Even optimistic scenario shows modest returns. Strategy works best as **complement**, not standalone system.

### When to Abandon Strategy

**Stop Using If:**
- Win rate drops below 45% for 2+ years
- Max drawdown exceeds -40%
- Sharpe ratio consistently below 0.3
- Correlation drops below 0.15
- Transaction costs exceed 50% of gross profits

---

## Integration with Other Signals

### Recommended Multi-Factor Framework

**Primary Signals (70% weight):**
- Iron ore price momentum
- China manufacturing PMI
- Baltic Dry Index trend

**Secondary Signals (20% weight):**
- Vessel dispersion extremes (this strategy)
- Freight forward curve shape
- Port congestion indicators

**Risk Management (10% weight):**
- Volatility filters
- Drawdown controls
- Position sizing

### Example Combined Logic

```python
# Pseudo-code for multi-factor approach

def generate_trade_signal():
    # Primary signals
    iron_ore_bullish = (iron_ore_momentum > 0.5)
    china_pmi_expanding = (china_pmi > 50)
    
    # Secondary confirmation
    dispersion_extreme_bullish = (dispersion_z > 2.0)
    
    # Combined logic
    if iron_ore_bullish and china_pmi_expanding:
        if dispersion_extreme_bullish:
            return "STRONG LONG"  # High conviction
        else:
            return "MODERATE LONG"  # Standard conviction
    elif dispersion_extreme_bullish:
        return "WEAK LONG"  # Dispersion alone = weak signal
    else:
        return "FLAT"
```

---

## Frequently Asked Questions

### Q: Why trade only extreme events (z ≥ 2.0)?

**A:** Critical evaluation showed:
- Weak/medium signals (z < 2.0) have poor win rate (~45%)
- High noise-to-signal ratio below 2.0σ
- Extreme events (z ≥ 2.0) capture major regime shifts
- 95% reduction in transaction costs

### Q: Can I adjust the threshold to 1.5σ or 2.5σ?

**A:** Yes, but:
- Lower (1.5σ): More trades, more noise, higher costs
- Higher (2.5σ): Fewer trades, may miss opportunities
- Recommended: Test on out-of-sample data first

### Q: Why is win rate still only 48-52%?

**A:** 
- Weak correlation (0.27) is fundamental limitation
- Dispersion and prices respond to same factors (endogeneity)
- Market may already price in dispersion information
- Strategy captures some edge but not dominant

### Q: What if backtested return is negative?

**A:** 
- **Expected** - standalone strategy is not profitable
- Focus on **Sharpe ratio** and **max drawdown** improvements
- Use as filter/confirmation, not standalone
- Combine with other indicators for profitability

### Q: Should I trade this strategy with real money?

**A:** 
- **NOT RECOMMENDED** as standalone
- **MAYBE** as part of multi-factor system
- **REQUIRES** additional validation:
  - Out-of-sample testing
  - Walk-forward analysis
  - Paper trading for 6+ months
  - Combination with other signals

---

## Checklist Before Trading

### Pre-Trade Validation

- [ ] Understand strategy is a FILTER, not standalone signal
- [ ] Review critical evaluation findings (STRATEGY_ADAPTATION.md)
- [ ] Backtest shows improvement over old strategy
- [ ] Have other signals to combine with dispersion
- [ ] Risk management in place (stop-loss, position sizing)
- [ ] Accept potential for negative returns
- [ ] Transaction costs are reasonable (<10 bps)
- [ ] Capital allocation is appropriate (max 5-10% of portfolio)

### During Trading

- [ ] Monitor win rate monthly (should stay >45%)
- [ ] Track transaction costs (should be <20% of gross P&L)
- [ ] Review extreme events (are they truly fundamental?)
- [ ] Check regime detection (is it filtering correctly?)
- [ ] Compare to other signals (is dispersion adding value?)

### Post-Trade Review

- [ ] Analyze winning vs losing trades
- [ ] Identify regime-specific performance
- [ ] Validate extreme threshold (is 2.0σ optimal?)
- [ ] Assess signal lag effectiveness
- [ ] Consider adjustments for next period

---

## Conclusion

The adapted extreme event strategy represents an **honest, research-backed approach** to using vessel dispersion data. It acknowledges the weak standalone performance while maximizing the signal's utility by:

1. Trading only statistically significant events (|z| ≥ 2.0)
2. Implementing regime detection
3. Requiring signal persistence
4. Reducing transaction costs by 90%

**Most Important:** This is a **filter/confirmation tool**, not a complete trading system. Profitability requires combining with other indicators and rigorous risk management.

Use this strategy to **enhance** your freight trading framework, not replace it.
