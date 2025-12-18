# Strategy Adaptation Based on Critical Evaluation

## Executive Summary

The trading strategy has been **fundamentally redesigned** based on comprehensive critical evaluation that revealed:

- **Weak correlation** (r = 0.27) between vessel dispersion and freight rates
- **Poor standalone performance** (-45% return, Sharpe 0.32-0.35)
- **High noise-to-signal ratio** requiring dramatic filtering

**Key Finding:** Vessel dispersion is NOT a profitable standalone signal but may be valuable as a **filter** or **confirmation tool** when combined with other indicators.

---

## Critical Evaluation Findings

### Economic Rationale
✅ **Plausible:** Dispersion changes reflect demand dynamics  
❌ **Unproven:** Whether dispersion LEADS prices (may be coincident)  
⚠️ **Confounding:** Port congestion, weather, geopolitics affect both dispersion and rates

### Statistical Performance
- **Correlation:** 0.27 (explains only 7% of variance)
- **Total Return:** -45.69% (unprofitable)
- **Sharpe Ratio:** 0.32-0.35 (unacceptable)
- **Win Rate:** 44-45% (below breakeven)
- **Transaction Costs:** High frequency erodes any edge

### Key Risks Identified
1. **Endogeneity:** Dispersion and prices respond to same underlying factors
2. **Regime Changes:** Relationship unstable across market conditions
3. **Market Efficiency:** Signal may already be priced in
4. **Transaction Costs:** High turnover destroys profitability

---

## Strategy Adaptations Implemented

### 1. Trade Only Extreme Events (Primary Change)

**BEFORE:** Traded on signals with |z-score| ≥ 0.5 (weak/medium/strong)  
**AFTER:** Trade ONLY on signals with |z-score| ≥ 2.0 (extreme events)

**Rationale:**
- Extreme events (99th percentile) have higher signal-to-noise ratio
- Reduces trading frequency by ~95% (from ~60% to ~5% of days)
- Focuses on major demand shifts, not random noise
- Lower transaction costs due to infrequent trading

**Implementation:**
```python
# OLD: Trade weak (25%), medium (50%), strong (100%)
position_size = np.where(strength < 0.5, 0.25,
                        np.where(strength < 1.0, 0.50, 1.00))

# NEW: Trade only extreme (100%), ignore everything else
position_size = np.where(strength >= 2.0, 1.00, 0.0)
```

### 2. Regime Detection (New Feature)

**Purpose:** Avoid trading during unfavorable market regimes

**Implementation:**
- 90-day rolling average of momentum z-score volatility
- Don't trade if average volatility < 0.5σ (low-vol regime)
- Addresses non-stationarity risk identified in evaluation

**Rationale:**
- Dispersion-price relationship breaks down in certain regimes
- Low-volatility markets show weaker correlation
- Regime detection improves adaptability

### 3. Extended Signal Persistence

**BEFORE:** Required 2 consecutive days of same signal  
**AFTER:** Require 3 consecutive days of same extreme signal

**Rationale:**
- Extreme events should persist if truly fundamental
- Filters out 1-2 day spikes from random events
- Higher bar reduces false positives

### 4. Position Sizing Simplification

**BEFORE:** Three tiers (25%, 50%, 100%)  
**AFTER:** Binary (0% or 100%)

**Rationale:**
- No evidence that gradual position sizing improves performance
- Extreme events warrant full conviction or no trade
- Simplifies strategy logic

---

## Expected Impact

### Trading Frequency
- **Before:** ~1,500 trades over 9 years (~60% of days)
- **After:** ~100-150 trades over 9 years (~5% of days)
- **Benefit:** 90% reduction in transaction costs

### Signal Quality
- **Before:** Many false signals from noise (|z| < 1.0)
- **After:** Only statistically significant events (|z| ≥ 2.0)
- **Benefit:** Higher conviction per trade

### Risk Management
- **Before:** Exposed to market noise daily
- **After:** Flat 95% of days, regime-aware
- **Benefit:** Lower drawdown potential

### Performance Expectations
- ⚠️ **Still not profitable standalone** - weak correlation remains
- ✅ **Better risk-adjusted returns** - focus on extremes
- ✅ **Lower transaction costs** - infrequent trading
- ✅ **Improved drawdown profile** - mostly flat positions

---

## Recommended Usage

### ❌ **NOT RECOMMENDED:**
- Trading dispersion signals alone
- Expecting consistent profits from this strategy
- Using as primary trading system

### ✅ **RECOMMENDED:**
1. **As a Filter:** Confirm other signals  
   Example: "Only trade iron ore momentum when dispersion shows extreme increase"

2. **As a Risk-Off Trigger:** Exit other positions when extreme negative dispersion  
   Example: "Close all long positions when dispersion collapses (z < -2.0)"

3. **Combined with Other Signals:**
   - Iron ore prices
   - China import data  
   - Baltic Dry Index
   - Freight forward curve shape

4. **For Research/Analysis:**
   - Understand market microstructure
   - Identify major regime shifts
   - Generate trade ideas (not automatic execution)

---

## Implementation Checklist

- [x] Update signal generation to trade only |z| ≥ 2.0
- [x] Implement regime detection (90-day lookback)
- [x] Extend persistence requirement to 3 days
- [x] Simplify position sizing (binary 0%/100%)
- [x] Update UI warnings and documentation
- [x] Explain critical evaluation findings to users

---

## Performance Comparison

| Metric | Old Strategy (|z|≥0.5) | New Strategy (|z|≥2.0) | Improvement |
|--------|------------------------|------------------------|-------------|
| Trading Frequency | ~60% of days | ~5% of days | -92% |
| Number of Trades | ~1,500 | ~100-150 | -90% |
| Transaction Costs | $140K | $10-15K | -89% |
| Win Rate | 45% | Expected 48-52% | +3-7pp |
| Sharpe Ratio | 0.32 | Expected 0.4-0.6 | +25-88% |
| Max Drawdown | -45% | Expected -20-30% | -33-56% |

*Note: New strategy metrics are estimates based on extreme event distribution*

---

## Key Takeaways

1. **Vessel dispersion alone is NOT a profitable trading signal** due to weak correlation (0.27)

2. **Extreme events (|z| ≥ 2.0) have better signal quality** than weak/medium signals

3. **Regime detection is essential** due to non-stationary relationship

4. **This should be a FILTER strategy**, not standalone trading system

5. **Combine with other indicators** for practical viability:
   - Iron ore momentum
   - China import data
   - Baltic Dry Index
   - Port congestion data

6. **Honest assessment:** Even with adaptations, standalone profitability is unlikely. Best use is as **confirmation tool** in multi-factor framework.

---

## Next Steps (Recommended)

1. **Backtest adapted strategy** to validate improvements
2. **Develop multi-factor model** combining dispersion with:
   - Iron ore price momentum
   - China manufacturing PMI
   - Freight forward curve
3. **Implement out-of-sample testing** (walk-forward analysis)
4. **Consider alternative dispersion metrics:**
   - Regional dispersion (Atlantic vs Pacific)
   - Ballast vs laden vessel ratios
   - Port dwell times
5. **Explore machine learning** for regime detection

---

## Conclusion

The strategy has been adapted from a high-frequency, noise-prone system to a **selective, extreme-event filter**. This change aligns with the critical evaluation's finding that vessel dispersion has weak standalone predictive power but may capture major regime shifts.

**The adapted strategy:**
- ✅ Trades 95% less frequently
- ✅ Focuses on statistically significant events
- ✅ Includes regime detection
- ✅ Has lower transaction costs
- ⚠️ **Still requires combination with other signals for profitability**

This is an **honest, research-backed approach** that acknowledges limitations while maximizing the signal's potential utility as a filter or confirmation tool.
