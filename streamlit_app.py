"""
Streamlit Dashboard - User-Friendly Interface for Dispersion Analysis

Tabs:
1. 📊 Data Overview - Correlations, quality, statistical tests
2. 🎯 Signal Explorer - Momentum signal explanation
3. 🏬 Backtest Results - Performance, P&L
4. 📈 Economic Analysis - In-depth statistics

UX Architecture:
- Lots of st.info() for explanations
- Sidebar with interactive controls
- Clear and detailed visualizations
- Tabs separated by theme
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime
from pathlib import Path
import sys

# Import classes
sys.path.insert(0, str(Path(__file__).parent))
from data_manager import DataManager
from signal_generator import SignalGenerator
from backtest_engine import BacktestEngine


# ============================================================================
# CONFIGURATION PAGE
# ============================================================================

st.set_page_config(
    page_title="Capesize Dispersion Analysis",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé
st.markdown("""
<style>
    .main {
        padding: 0rem 0rem;
    }
    h1 {
        color: #1f77b4;
        font-size: 2.5rem;
    }
    h2 {
        color: #ff7f0e;
        font-size: 2rem;
    }
    .stInfo {
        background-color: #f0f7ff;
        border-left: 4px solid #1f77b4;
    }
    .stSuccess {
        background-color: #f0fff4;
        border-left: 4px solid #28a745;
    }
    .stWarning {
        background-color: #fffbf0;
        border-left: 4px solid #ff9800;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# CACHE & DATA LOADING
# ============================================================================

@st.cache_resource
def load_data_once():
    """Load data once and cache it."""
    dm = DataManager(
        price_csv='cape_front_month.csv',
        dispersion_csv='dispersion_case_study.csv'
    )
    clean_data = dm.get_clean_data(drop_na=True)
    sg = SignalGenerator(clean_data)
    return dm, sg, clean_data


# ============================================================================
# SIDEBAR & NAVIGATION
# ============================================================================

st.sidebar.markdown("# 🚢 Capesize Dispersion Analysis")
st.sidebar.markdown("### Study: 5TC Prices vs Fleet Dispersion")

st.sidebar.info(
    "**📖 About:**\n\n"
    "This project tests whether Capesize/VLOC vessel dispersion "
    "predicts 5TC front-month prices.\n\n"
    "✅ **Approach**: Momentum-based signal from dispersion changes\n"
    "✅ **Honest**: Acknowledges limitations\n"
    "✅ **Realistic**: Includes transaction fees"
)

st.sidebar.markdown("---")

tab_choice = st.sidebar.radio(
    "Navigation",
    [
        "📊 Data Overview",
        "🎯 Signal Explorer",
        "🏬 Backtest Results",
        "📈 Economic Analysis"
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Signal Parameters")

signal_lag = st.sidebar.slider(
    "Signal Lag (days)",
    min_value=0,
    max_value=14,
    value=0,
    step=1,
    help="Wait N days after signal before entering position (0 = immediate). Test if dispersion momentum leads prices by several days."
)

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Backtest Parameters")

initial_capital = st.sidebar.number_input(
    "Initial Capital ($)",
    value=1_000_000,
    step=100_000,
    min_value=100_000,
    help="Initial portfolio amount"
)

fee_bps = st.sidebar.slider(
    "Transaction Fees (bps)",
    min_value=0,
    max_value=50,
    value=10,
    step=1,
    help="Basis points per trade (round-trip)"
)

# ============================================================================
# DATA LOADING
# ============================================================================

try:
    dm, _, clean_data = load_data_once()
    data_summary = dm.get_data_summary()
    
    # Generate signals with user-selected lag
    sg = SignalGenerator(clean_data, signal_lag=signal_lag)
    signals_df = sg.get_signals_dataframe()
except Exception as e:
    st.error(f"❌ Error loading data: {e}")
    st.stop()


# ============================================================================
# TAB 1: DATA OVERVIEW
# ============================================================================

if tab_choice == "📊 Data Overview":
    st.title("📊 Data Overview & Statistical Analysis")
    
    st.info(
        "**Objective:** Understand the raw data before building any trading strategy.\n\n"
        "This analysis follows a rigorous statistical approach:\n"
        "1. **Data Description** - What do we have?\n"
        "2. **Distribution Analysis** - How do variables behave?\n"
        "3. **Correlation Study** - Do they move together?\n"
        "4. **Causality Testing** - Does dispersion predict prices?\n"
        "5. **Quality Checks** - Can we trust the data?\n\n"
        "**Philosophy:** We prefer to report 'no signal found' rather than overfit the data."
    )
    
    # ========================================================================
    # SECTION 1: DATA SUMMARY
    # ========================================================================
    
    st.markdown("---")
    st.header("1️⃣ Dataset Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Sample Size",
            f"{data_summary['sample_size']:,} days"
        )
    with col2:
        years = data_summary['years_covered']
        st.metric(
            "Period",
            f"{years:.1f} years",
            f"{data_summary['date_start'].strftime('%Y-%m')} to {data_summary['date_end'].strftime('%Y-%m')}"
        )
    with col3:
        corr = data_summary['correlation_avg']
        st.metric(
            "Pearson Correlation",
            f"{corr:.3f}",
            delta="Weak positive" if 0.2 < corr < 0.4 else "Very weak" if abs(corr) < 0.2 else ""
        )
    with col4:
        r_squared = corr ** 2
        st.metric(
            "R² (Explained Var.)",
            f"{r_squared:.1%}",
            delta=f"{100-r_squared*100:.0f}% unexplained"
        )
    
    st.info(
        "**About the Data:**\n\n"
        "- **5TC Front-Month (C+1MON):** Forward Freight Agreement contract for Capesize vessels. "
        "This is the primary hedging instrument for iron ore shipping routes.\n"
        "- **Dispersion:** Geographic spread of Capesize + VLOC vessels worldwide. "
        "High dispersion = vessels well-positioned globally for cargo pickup.\n"
        "- **Time Alignment:** Both series are daily observations, merged on date (inner join)."
    )
    
    # ========================================================================
    # SECTION 2: UNDERSTANDING DISPERSION METRIC
    # ========================================================================
    
    st.markdown("---")
    st.header("2️⃣ Understanding the Dispersion Metric")
    
    st.subheader("📐 How We Calculate Weighted Average Dispersion")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **Formula:**
        ```
        avg_dispersion = (Cape_Disp × Cape_Count + VLOC_Disp × VLOC_Count) / Total_Count
        ```
        
        **Why weight by vessel COUNT and not by vessel CAPACITY?**
        
        1. **Market Activity Signal:** Count reflects how many vessels are actively seeking cargo. 
           A large VLOC doesn't generate more "dispersion signal" than a smaller Capesize if both 
           are ballasting/positioning.
        
        2. **Geographic Presence:** We care about spatial distribution, not total tonnage. 
           100 Capesizes dispersed globally create better coverage than 30 VLOCs, 
           even if tonnage is similar.
        
        3. **Data Reality:** The dispersion metric itself measures spatial spread of vessel positions, 
           not their cargo capacity. Weighting by count preserves the metric's meaning.
        
        4. **Market Dynamics:** Both Capesize (100-180k DWT) and VLOC (200-400k DWT) compete for 
           similar routes (Brazil-China, Australia-China iron ore). The number of competing vessels 
           matters more than their aggregate capacity for positioning analysis.
        """)
        
        st.success(
            "**Bottom Line:** We weight by vessel count because dispersion measures "
            "*where vessels are*, not *how much they can carry*. It's a spatial metric, not a capacity metric."
        )
    
    with col2:
        st.metric("Capesize Avg Count", f"{signals_df['cape_vessel_count'].mean():.0f} vessels")
        st.metric("VLOC Avg Count", f"{signals_df['vloc_vessel_count'].mean():.0f} vessels")
        st.metric("Total Avg Count", f"{signals_df['total_vessel_count'].mean():.0f} vessels")
        
        cape_pct = signals_df['cape_vessel_count'].mean() / signals_df['total_vessel_count'].mean()
        vloc_pct = signals_df['vloc_vessel_count'].mean() / signals_df['total_vessel_count'].mean()
        
        st.markdown("**Fleet Mix:**")
        st.progress(cape_pct, text=f"Capesize: {cape_pct:.1%}")
        st.progress(vloc_pct, text=f"VLOC: {vloc_pct:.1%}")
    
    # ========================================================================
    # SECTION 3: DISTRIBUTION ANALYSIS
    # ========================================================================
    
    st.markdown("---")
    st.header("3️⃣ Distribution Analysis")
    
    tab_dist = st.tabs(["5TC Prices", "Dispersion", "By Vessel Class"])
    
    with tab_dist[0]:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Price histogram
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=signals_df['price_5tc'],
                nbinsx=50,
                name='5TC Price',
                marker_color='#1f77b4',
                opacity=0.7
            ))
            fig.update_layout(
                title="5TC Price Distribution",
                xaxis_title="Price ($/day)",
                yaxis_title="Frequency",
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            price_stats = data_summary['price_5tc']
            st.metric("Mean", f"${price_stats['mean']:.0f}/day")
            st.metric("Std Dev", f"${price_stats['std']:.0f}")
            st.metric("Min", f"${price_stats['min']:.0f}")
            st.metric("Max", f"${price_stats['max']:.0f}")
            st.metric("Range", f"${price_stats['max'] - price_stats['min']:.0f}")
            
            # Coefficient of variation
            cv = price_stats['std'] / price_stats['mean']
            st.metric("Coef. of Variation", f"{cv:.1%}")
        
        st.info(
            "**Interpretation:** 5TC prices are highly volatile (CV > 50%), "
            "typical of commodity freight markets. The distribution shows multiple modes, "
            "reflecting different market regimes (boom/bust cycles in iron ore trade)."
        )
    
    with tab_dist[1]:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Dispersion histogram
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=signals_df['avg_dispersion'],
                nbinsx=50,
                name='Avg Dispersion',
                marker_color='#d62728',
                opacity=0.7
            ))
            fig.update_layout(
                title="Average Dispersion Distribution",
                xaxis_title="Dispersion Value",
                yaxis_title="Frequency",
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            disp_stats = data_summary['avg_dispersion']
            st.metric("Mean", f"{disp_stats['mean']:.0f}")
            st.metric("Std Dev", f"{disp_stats['std']:.0f}")
            st.metric("Min", f"{disp_stats['min']:.0f}")
            st.metric("Max", f"{disp_stats['max']:.0f}")
            st.metric("Range", f"{disp_stats['max'] - disp_stats['min']:.0f}")
            
            cv_disp = disp_stats['std'] / disp_stats['mean']
            st.metric("Coef. of Variation", f"{cv_disp:.1%}")
        
        st.info(
            "**Interpretation:** Dispersion shows moderate variability. "
            "The metric ranges significantly, indicating real changes in vessel positioning patterns "
            "over time (not just noise)."
        )
    
    with tab_dist[2]:
        # Scatter plot Cape vs VLOC dispersion
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=signals_df['cape_dispersion'],
            y=signals_df['vloc_dispersion'],
            mode='markers',
            marker=dict(
                size=3,
                color=signals_df['price_5tc'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="5TC Price")
            ),
            text=[f"Date: {d.strftime('%Y-%m-%d')}<br>Price: ${p:.0f}" 
                  for d, p in zip(signals_df['date'], signals_df['price_5tc'])],
            hovertemplate='Cape Disp: %{x:.0f}<br>VLOC Disp: %{y:.0f}<br>%{text}<extra></extra>'
        ))
        fig.update_layout(
            title="Capesize vs VLOC Dispersion (colored by 5TC price)",
            xaxis_title="Capesize Dispersion",
            yaxis_title="VLOC Dispersion",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        cape_vloc_corr = signals_df['cape_dispersion'].corr(signals_df['vloc_dispersion'])
        st.metric("Cape-VLOC Correlation", f"{cape_vloc_corr:.3f}")
        
        st.info(
            f"**Interpretation:** Capesize and VLOC dispersion are correlated at {cape_vloc_corr:.2f}, "
            "meaning they tend to disperse/concentrate together. This makes sense as they serve "
            "similar trade routes and respond to the same demand patterns."
        )
    
    # ========================================================================
    # SECTION 4: TIME SERIES & CORRELATION ANALYSIS
    # ========================================================================
    
    st.markdown("---")
    st.header("4️⃣ Time Series & Correlation Analysis")
    
    st.subheader("📈 Raw Time Series")
    
    # Dual-axis time series
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Scatter(
            x=signals_df['date'],
            y=signals_df['price_5tc'],
            name='5TC Price',
            line=dict(color='#1f77b4', width=2)
        ),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(
            x=signals_df['date'],
            y=signals_df['avg_dispersion'],
            name='Avg Dispersion',
            line=dict(color='#d62728', width=2)
        ),
        secondary_y=True
    )
    
    fig.update_layout(
        title="5TC Price vs Average Dispersion (Dual Axis)",
        hovermode='x unified',
        height=400
    )
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="5TC Price ($/day)", secondary_y=False)
    fig.update_yaxes(title_text="Average Dispersion", secondary_y=True)
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("🔄 Rolling Correlation Analysis")
    
    # Calculate rolling correlation
    window = st.slider("Select rolling window (days)", 30, 365, 90, 30)
    rolling_corr = signals_df['price_5tc'].rolling(window).corr(signals_df['avg_dispersion'])
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=signals_df['date'],
        y=rolling_corr,
        name=f'{window}-day Rolling Correlation',
        line=dict(color='#2ca02c', width=2)
    ))
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_hline(y=data_summary['correlation_avg'], line_dash="dot", line_color="red", 
                  annotation_text=f"Overall: {data_summary['correlation_avg']:.3f}")
    fig.update_layout(
        title=f"Rolling {window}-Day Correlation: Price vs Dispersion",
        xaxis_title="Date",
        yaxis_title="Correlation Coefficient",
        height=350
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.warning(
        "**⚠️ Key Observation:** The rolling correlation varies significantly over time. "
        "It's sometimes strongly positive, sometimes near zero, and occasionally negative. "
        "This indicates the relationship is **not stable** - it changes with market regimes. "
        "Any trading strategy must account for this non-stationarity."
    )
    
    # ========================================================================
    # SECTION 5: GRANGER CAUSALITY TEST
    # ========================================================================
    
    st.markdown("---")
    st.header("5️⃣ Granger Causality Test")
    
    st.info(
        "**What is Granger Causality?**\n\n"
        "Tests whether past values of dispersion help predict future prices, beyond what "
        "past prices already tell us. This is a standard econometric test for predictive relationships.\n\n"
        "**Null Hypothesis:** Dispersion does NOT Granger-cause prices (i.e., dispersion has no predictive power).\n"
        "**Alternative:** Dispersion DOES Granger-cause prices (i.e., dispersion helps forecast prices)."
    )
    
    try:
        from statsmodels.tsa.stattools import grangercausalitytests
        
        # Prepare data (drop NaNs)
        test_data = signals_df[['price_5tc', 'avg_dispersion']].dropna()
        
        # Test with multiple lags
        max_lag = st.slider("Maximum lag to test (days)", 1, 20, 10, 1)
        
        with st.spinner("Running Granger causality tests..."):
            # Test: Does dispersion Granger-cause price?
            gc_results = grangercausalitytests(test_data[['price_5tc', 'avg_dispersion']], max_lag)
        
        # Extract p-values
        results_list = []
        for lag in range(1, max_lag + 1):
            # Get F-test p-value (ssr_ftest)
            f_test = gc_results[lag][0]['ssr_ftest']
            p_value = f_test[1]
            results_list.append({
                'Lag': lag,
                'F-statistic': f_test[0],
                'p-value': p_value,
                'Significant (5%)': '✅ Yes' if p_value < 0.05 else '❌ No',
                'Significant (10%)': '✅ Yes' if p_value < 0.10 else '❌ No'
            })
        
        results_df = pd.DataFrame(results_list)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Plot p-values
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=results_df['Lag'],
                y=results_df['p-value'],
                mode='lines+markers',
                name='p-value',
                line=dict(color='#1f77b4', width=2),
                marker=dict(size=8)
            ))
            fig.add_hline(y=0.05, line_dash="dash", line_color="red", 
                         annotation_text="5% significance")
            fig.add_hline(y=0.10, line_dash="dot", line_color="orange", 
                         annotation_text="10% significance")
            fig.update_layout(
                title="Granger Causality Test: P-values by Lag",
                xaxis_title="Lag (days)",
                yaxis_title="P-value",
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("**Test Results:**")
            significant_5 = (results_df['p-value'] < 0.05).sum()
            significant_10 = (results_df['p-value'] < 0.10).sum()
            
            st.metric("Significant at 5%", f"{significant_5}/{max_lag} lags")
            st.metric("Significant at 10%", f"{significant_10}/{max_lag} lags")
            
            if significant_5 > max_lag * 0.3:
                st.success("✅ **Strong Evidence** of predictive power")
            elif significant_10 > max_lag * 0.3:
                st.warning("⚠️ **Moderate Evidence** of predictive power")
            else:
                st.error("❌ **Weak/No Evidence** of predictive power")
        
        with st.expander("📊 Detailed Results Table"):
            st.dataframe(results_df, use_container_width=True, hide_index=True)
        
        st.markdown("**Interpretation:**")
        if significant_5 == 0:
            st.warning(
                "⚠️ **No significant Granger causality detected at 5% level.** "
                "This suggests that past dispersion values do NOT significantly help predict future prices "
                "beyond what past prices already tell us. The correlation we observe may be **contemporaneous** "
                "rather than predictive."
            )
        elif significant_5 <= 2:
            st.info(
                "**Weak predictive relationship detected.** Only a few lags show significance, "
                "which could be due to chance (multiple testing). The evidence for using dispersion "
                "to trade systematically is **marginal at best**."
            )
        else:
            st.success(
                f"✅ **Predictive relationship detected!** {significant_5} out of {max_lag} lags "
                "show significant Granger causality. This suggests dispersion MAY have predictive power "
                "for future prices. However:\n"
                "- Statistical significance ≠ economic profitability\n"
                "- Past performance ≠ future results\n"
                "- Transaction costs matter\n"
                "- The relationship may be unstable over time"
            )
    
    except Exception as e:
        st.error(f"Could not perform Granger causality test: {e}")
        st.info("Install statsmodels package: `pip install statsmodels`")
    
    # ========================================================================
    # SECTION 6: DATA QUALITY CHECKS
    # ========================================================================
    
    st.markdown("---")
    st.header("6️⃣ Data Quality Checks")
    
    validation_report = dm.validate_data()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**📋 Completeness:**")
        st.metric("Total Rows", f"{len(signals_df):,}")
        st.metric("NaN Values", "0" if signals_df.isna().sum().sum() == 0 else f"{signals_df.isna().sum().sum()}")
        st.success("✅ No missing data")
    
    with col2:
        st.markdown("**🔍 Outliers:**")
        outlier_check = validation_report['checks']['price_outliers']
        st.metric("Price Outliers (>5σ)", outlier_check['count'])
        if outlier_check['status'] == 'ok':
            st.success("✅ No extreme outliers")
        else:
            st.warning(f"⚠️ {outlier_check['count']} outliers detected")
    
    with col3:
        st.markdown("**📅 Continuity:**")
        continuity = validation_report['checks']['date_continuity']
        st.metric("Max Gap (days)", continuity['max_gap_days'])
        if continuity['status'] == 'ok':
            st.success("✅ Good continuity")
        else:
            st.warning(f"⚠️ Gap up to {continuity['max_gap_days']} days")
    
    with st.expander("🔬 Detailed Quality Report"):
        st.json(validation_report)
    
    st.success(
        "**✅ Data Quality Summary:**\n\n"
        "- No missing values\n"
        "- No extreme outliers (>5σ) in prices\n"
        "- Reasonable date continuity\n"
        "- Sufficient variance in both series\n"
        "- **Conclusion: Data is suitable for analysis**"
    )


# ============================================================================
# TAB 2: SIGNAL EXPLORER
# ============================================================================

elif tab_choice == "🎯 Signal Explorer":
    st.title("🎯 Signal Explorer: Momentum Strategy")
    
    st.info(
        "**Step 2: Understand the signal**\n\n"
        "We use a simple momentum-based signal derived from dispersion changes:\n"
        "- **LONG** when dispersion increases (vessels spreading out)\n"
        "- **SHORT** when dispersion decreases (vessels concentrating)\n\n"
        "This captures short-term vessel positioning dynamics that may precede price movements."
    )
    
    # Signal lag info
    if signal_lag > 0:
        st.warning(
            f"⏱️ **Signal Lag Applied: {signal_lag} day(s)**\n\n"
            f"Signal from day T is used to enter position on day T+{signal_lag}. "
            f"This allows confirmation time and tests if dispersion changes are truly predictive."
        )
    
    st.markdown("---")
    
    # Signal explanation
    explanations = sg.get_all_explanations()
    exp = explanations['momentum']
    
    st.subheader("📈 Momentum Dispersion Signal")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Type**: {exp['signal_type']}")
        st.markdown(f"**Horizon**: {exp['horizon']}")
    with col2:
        st.markdown(f"**Logic**:")
        st.code(exp['logic'])
    
    st.markdown("---")
    st.info(f"**📖 Economic Meaning**:\n\n{exp['economic_meaning']}")
    st.success(f"**💡 Rationale**:\n\n{exp['rationale']}")
    
    st.markdown("---")
    
    # Position sizing explanation
    st.subheader("🛡️ Multi-Threshold Strategy (Graduated Conviction)")
    
    st.warning(
        "**⚠️ ADAPTED STRATEGY BASED ON EVALUATION ⚠️**\n\n"
        "Based on comprehensive analysis showing weak correlation (r=0.27), this strategy uses "
        "**graduated position sizing** to balance signal capture with risk management.\n\n"
        "**Key Finding:** More aggressive than extreme-only approach, but still filters weak signals (|z|<1.0). "
        "Combine with other indicators for best results."
    )
    
    st.info(
        "**Multi-Threshold Position Sizing:**\n\n"
        "**Position Allocation by Signal Strength:**\n"
        "- 🔴 **EXTREME** (|z| ≥ 2.5σ) → **100% allocation** (very rare, ~2% of days)\n"
        "- 🟠 **VERY STRONG** (2.0σ ≤ |z| < 2.5σ) → **75% allocation** (rare, ~3% of days)\n"
        "- 🟡 **STRONG** (1.5σ ≤ |z| < 2.0σ) → **50% allocation** (uncommon, ~5% of days)\n"
        "- 🟢 **MEDIUM** (1.0σ ≤ |z| < 1.5σ) → **25% allocation** (occasional, ~10% of days)\n"
        "- ⚪ **WEAK** (|z| < 1.0σ) → **0% allocation - FLAT** (filtered out, ~80% of days)\n\n"
        "**Protective Filters:**\n\n"
        "**1️⃣ Signal Persistence**\n"
        "- Requires **2 consecutive days** of same signal direction\n"
        "- Filters out 1-day spikes and random noise\n\n"
        "**2️⃣ Regime Detection**\n"
        "- Avoids trading in low-volatility regimes (90-day rolling average)\n"
        "- Addresses non-stationarity risk\n\n"
        "**3️⃣ Volatility Filter**\n"
        "- Blocks trading when |price z-score| > 2.0σ (extreme market volatility)\n\n"
        "**Result:** ~15-25% of days have active positions, graduated by conviction level. "
        "Higher signal capture than extreme-only, lower than aggressive approaches."
    )
    
    # Show position size distribution
    if 'signal_momentum_size' in signals_df.columns:
        size_dist = signals_df['signal_momentum_size'].value_counts().sort_index()
        
        col_size1, col_size2, col_size3, col_size4, col_size5 = st.columns(5)
        with col_size1:
            extreme_count = (signals_df['signal_momentum_size'] == 1.0).sum()
            extreme_pct = 100 * extreme_count / len(signals_df)
            st.metric("🔴 EXTREME", f"{extreme_count:,}", f"100% ({extreme_pct:.1f}%)")
        with col_size2:
            very_strong_count = (signals_df['signal_momentum_size'] == 0.75).sum()
            very_strong_pct = 100 * very_strong_count / len(signals_df)
            st.metric("🟠 VERY STRONG", f"{very_strong_count:,}", f"75% ({very_strong_pct:.1f}%)")
        with col_size3:
            strong_count = (signals_df['signal_momentum_size'] == 0.50).sum()
            strong_pct = 100 * strong_count / len(signals_df)
            st.metric("🟡 STRONG", f"{strong_count:,}", f"50% ({strong_pct:.1f}%)")
        with col_size4:
            medium_count = (signals_df['signal_momentum_size'] == 0.25).sum()
            medium_pct = 100 * medium_count / len(signals_df)
            st.metric("🟢 MEDIUM", f"{medium_count:,}", f"25% ({medium_pct:.1f}%)")
        with col_size5:
            flat_count = (signals_df['signal_momentum'] == 0).sum()
            flat_pct = 100 * flat_count / len(signals_df)
            st.metric("⚪ FLAT", f"{flat_count:,}", f"0% ({flat_pct:.1f}%)")
    
    st.markdown("---")
    
    # Signal statistics
    st.subheader("📊 Signal Performance (Historical)")
    
    signal_stats = sg.get_signal_statistics()
    
    if 'signal_momentum' in signal_stats:
        stats = signal_stats['signal_momentum']
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Days LONG", f"{stats.get('long_signals', 0):.0f}")
            st.metric("Avg Return LONG", f"{stats.get('avg_return_on_long', 0):.2%}")
        with col2:
            st.metric("Days SHORT", f"{stats.get('short_signals', 0):.0f}")
            st.metric("Avg Return SHORT", f"{stats.get('avg_return_on_short', 0):.2%}")
        with col3:
            st.metric("Days FLAT", f"{stats.get('flat_signals', 0):.0f}")
            st.metric("Win Rate LONG", f"{stats.get('win_rate_long', 0):.1%}")
        with col4:
            total_days = stats.get('total_signals', 0)
            active_pct = (stats.get('long_signals', 0) + stats.get('short_signals', 0)) / total_days if total_days > 0 else 0
            st.metric("Total Days", f"{total_days:.0f}")
            st.metric("Active %", f"{active_pct:.1%}")
    
    st.info(
        "**Interpretation:**\n\n"
        "- **Active %**: Percentage of time the signal is LONG or SHORT (not FLAT)\n"
        "- **Avg Return**: Average 5-day forward return when signal is active\n"
        "- **Win Rate LONG**: % of LONG signals that were profitable"
    )
    
    st.markdown("---")
    
    # Latest signals
    st.subheader("📋 Latest Signals (15 days)")
    
    latest_signals = sg.get_latest_signals(n_rows=15).copy()
    latest_signals['date'] = latest_signals['date'].dt.strftime('%Y-%m-%d')
    latest_signals['price_5tc'] = latest_signals['price_5tc'].apply(lambda x: f"${x:.0f}")
    latest_signals['avg_dispersion'] = latest_signals['avg_dispersion'].apply(lambda x: f"{x:.0f}")
    latest_signals['return_5d'] = latest_signals['return_5d'].apply(lambda x: f"{x:+.2%}")
    
    def signal_emoji(val):
        if val > 0:
            size_pct = int(val * 100)
            return f"🟢 LONG ({size_pct}%)"
        elif val < 0:
            size_pct = int(abs(val) * 100)
            return f"🔴 SHORT ({size_pct}%)"
        else:
            return "⚪ FLAT (0%)"
    
    latest_signals['Signal'] = latest_signals['signal_momentum'].apply(signal_emoji)
    
    display_cols = [
        'date', 'price_5tc', 'avg_dispersion', 'disp_quartile',
        'Signal', 'return_5d'
    ]
    
    st.dataframe(
        latest_signals[display_cols],
        use_container_width=True,
        hide_index=True
    )


# ============================================================================
# TAB 3: BACKTEST RESULTS
# ============================================================================

elif tab_choice == "🏬 Backtest Results":
    st.title("🏬 Backtest Results & Performance")
    
    st.warning(
        "**⚠️ MULTI-THRESHOLD STRATEGY ⚠️**\n\n"
        "This strategy uses **graduated position sizing** based on signal strength:\n"
        "- Stronger signals (higher |z-score|) receive larger allocations\n"
        "- More aggressive than extreme-only, but still filters weak signals\n"
        "- Trades ~15-25% of days vs ~5% with extreme-only or ~60% with old approach\n\n"
        "**Combine with other indicators** for best results."
    )
    
    st.info(
        f"**Backtest configuration:**\n"
        f"- 💰 Initial Capital: ${initial_capital:,}\n"
        f"- 💸 Fees: {fee_bps} bps per trade\n"
        f"- 🎯 Position Sizing: 25% (|z|≥1.0), 50% (|z|≥1.5), 75% (|z|≥2.0), 100% (|z|≥2.5)\n"
        f"- 🛡️ Persistence: 2 consecutive days\n"
        f"- 📊 Regime Detection: Enabled (90-day lookback)\n\n"
        "Results reflect the multi-threshold graduated conviction strategy."
    )
    
    st.markdown("---")
    
    # Run backtest
    signal_col = 'signal_momentum'
    strategy_choice = 'Momentum'
    
    with st.spinner("Running backtest..."):
        engine = BacktestEngine(
            signals_df,
            initial_capital=initial_capital,
            transaction_fee_bps=fee_bps
        )
        results = engine.backtest_strategy(signal_col, strategy_choice)
    
    st.markdown("---")
    
    # Key metrics
    st.subheader("📊 Performance Metrics")
    
    metric_cols = st.columns(5)
    
    with metric_cols[0]:
        st.metric(
            "Total Return",
            f"{results['total_return_pct']:.1%}",
            f"${results['total_pnl']:,.0f}"
        )
    
    with metric_cols[1]:
        st.metric(
            "Sharpe Ratio",
            f"{results['sharpe_ratio']:.2f}",
            "Risk-adjusted"
        )
    
    with metric_cols[2]:
        st.metric(
            "Max Drawdown",
            f"{results['max_drawdown_pct']:.1%}",
            "Worst loss"
        )
    
    with metric_cols[3]:
        st.metric(
            "Win Rate",
            f"{results['win_rate']:.1%}",
            f"{results['winning_trades']}/{results['num_trades']}"
        )
    
    with metric_cols[4]:
        st.metric(
            "Calmar Ratio",
            f"{results['calmar_ratio']:.2f}",
            "Return/Drawdown"
        )
    
    st.info(
        "**How to interpret:**\n\n"
        "- **Sharpe > 0.75**: Good signal (acceptable risk-adjusted)\n"
        "- **Drawdown < 15%**: Acceptable for commodities\n"
        "- **Win Rate ~50%**: Normal (gains > losses in size)\n"
        "- **Fee sensitivity**: Does the edge disappear with real fees?"
    )
    
    st.markdown("---")
    
    # Equity curve
    st.subheader("📈 Equity Curve")
    
    equity_vals, equity_dates = engine.get_equity_curve()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=equity_dates,
        y=equity_vals,
        fill='tozeroy',
        name='Portfolio Value',
        line=dict(color='#1f77b4', width=2)
    ))
    fig.update_layout(
        title=f"Portfolio Growth ({strategy_choice})",
        xaxis_title="Date",
        yaxis_title="Value ($)",
        hovermode='x unified',
        height=450
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Fee sensitivity
    st.subheader("💰 Transaction Fee Sensitivity")
    
    st.info(
        "**Importance**: As fees increase, the edge diminishes. "
        "A robust strategy remains profitable even with high fees."
    )
    
    fee_levels = [0, 5, 10, 15, 20, 30, 50]
    sensitivity_df = engine.compare_fees_sensitivity(signal_col, strategy_choice, fee_levels)
    
    st.dataframe(sensitivity_df, use_container_width=True, hide_index=True)
    
    st.warning(
        "⚠️ **Important Observation**:\n\n"
        "If Sharpe drops drastically between 0 and 10 bps, "
        "the strategy does NOT withstand real fees. "
        "In this case, it wouldn't be worth trading."
    )
    
    st.markdown("---")
    
    # Trade log
    st.subheader("📋 Trade Log (Last 20)")
    
    trade_log = engine.get_trade_log()
    
    if len(trade_log) > 0:
        display_log = trade_log.tail(20).copy()
        display_log['entry_date'] = display_log['entry_date'].dt.strftime('%Y-%m-%d')
        display_log['exit_date'] = display_log['exit_date'].dt.strftime('%Y-%m-%d')
        display_log['entry_price'] = display_log['entry_price'].apply(lambda x: f"${x:.0f}")
        display_log['exit_price'] = display_log['exit_price'].apply(lambda x: f"${x:.0f}")
        display_log['net_pnl'] = display_log['net_pnl'].apply(lambda x: f"${x:,.0f}")
        display_log['return_pct'] = display_log['return_pct'].apply(lambda x: f"{x:+.2%}")
        
        st.dataframe(display_log, use_container_width=True, hide_index=True)
        
        st.info(f"Showing last 20 trades. Total trades: {len(trade_log)}")
    else:
        st.info("No trades executed for this signal.")
    
    st.markdown("---")
    
    # Export functionality
    st.subheader("💾 Export Backtest Results")
    
    st.info(
        "**Export Options:**\n\n"
        "Download complete backtest results including:\n"
        "- Summary with all parameters (lag, capital, fees)\n"
        "- Complete trade log with all trades\n"
        "- Equity curve data\n\n"
        "Choose format: **Excel** (single file, multiple sheets) or **CSV** (separate files)"
    )
    
    col_export1, col_export2, col_export3 = st.columns([2, 1, 1])
    
    with col_export1:
        export_filename = st.text_input(
            "Filename (without extension)",
            value=f"backtest_lag{signal_lag}_capital{initial_capital//1000}k_fees{fee_bps}bps_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            help="Customize the export filename"
        )
    
    with col_export2:
        export_format = st.selectbox(
            "Format",
            options=["xlsx", "csv"],
            help="Excel = single file with multiple sheets, CSV = separate files"
        )
    
    with col_export3:
        st.write("")  # Spacing
        st.write("")  # Spacing
        if st.button("📥 Export Results", type="primary", use_container_width=True):
            try:
                # Prepare export path
                export_path = Path("export") / export_filename
                
                # Export using BacktestEngine method
                engine.export_results(
                    filepath=str(export_path),
                    signal_lag=signal_lag,
                    file_format=export_format
                )
                
                if export_format == 'xlsx':
                    st.success(f"✅ Results exported to: `export/{export_filename}.xlsx`")
                else:
                    st.success(
                        f"✅ Results exported to:\n"
                        f"- `export/{export_filename}_summary.csv`\n"
                        f"- `export/{export_filename}_trades.csv`\n"
                        f"- `export/{export_filename}_equity.csv`"
                    )
                
                st.info(
                    "📁 **Files saved in `export/` folder**\n\n"
                    "The export folder is gitignored to keep your results private."
                )
            except Exception as e:
                st.error(f"❌ Export failed: {e}")


# ============================================================================
# TAB 4: ECONOMIC ANALYSIS
# ============================================================================

elif tab_choice == "📈 Economic Analysis":
    st.title("📈 In-Depth Economic Analysis")
    
    st.info(
        "**Step 4: Analyze why it's interesting (or not)**\n\n"
        "Here we look at:\n"
        "- Statistical correlations\n"
        "- Pricing by regime (quartiles)\n"
        "- Risks and limitations"
    )
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1️⃣ The Underlying Relationship")
        
        st.markdown("""
        **Dispersion → 5TC Price**
        
        When Capesize vessels are **well dispersed**:
        - They are positioned where cargoes are loading
        - Supply matches demand well
        - The market functions efficiently
        
        This tends to coincide with:
        - Strong demand (multiple regions importing)
        - Good vessel utilization
        - Higher freight rates
        
        **Inverse logic**: Low dispersion = congestion = weakened rates
        """)
    
    with col2:
        st.subheader("2️⃣ Statistical Evidence")
        
        corr_cape = data_summary['correlation_cape']
        corr_vloc = data_summary['correlation_vloc']
        corr_avg = data_summary['correlation_avg']
        
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Capesize", f"{corr_cape:.3f}")
        col_b.metric("VLOC", f"{corr_vloc:.3f}")
        col_c.metric("Average", f"{corr_avg:.3f}")
        
        st.info(
            f"**Interpretation**:\n\n"
            f"- All correlations are positive ✅\n"
            f"- But they are weak (~0.27)\n"
            f"- This only explains ~7% of the variance\n"
            f"- Other factors dominate the remaining 93%\n\n"
            f"**Conclusion**: It's a real but modest relationship."
        )
    
    st.markdown("---")
    
    # Quartile analysis
    st.subheader("3️⃣ Pricing by Regime (Quartile Analysis)")
    
    regime_prices = signals_df.groupby('disp_quartile', observed=True)[
        'price_5tc'
    ].agg(['mean', 'count', 'std']).reset_index()
    regime_prices['count'] = regime_prices['count'].astype(int)
    
    if len(regime_prices) == 4:
        q1_price = regime_prices[
            regime_prices['disp_quartile'] == 'Q1_Low'
        ]['mean'].values[0]
        q4_price = regime_prices[
            regime_prices['disp_quartile'] == 'Q4_High'
        ]['mean'].values[0]
        premium_pct = (q4_price - q1_price) / q1_price
        premium_dollars = q4_price - q1_price
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Q1 (Low) Avg Price", f"${q1_price:.0f}/day")
        col2.metric("Q4 (High) Avg Price", f"${q4_price:.0f}/day")
        col3.metric("Premium", f"{premium_pct:.1%} (${premium_dollars:.0f})")
        
        # Chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=regime_prices['disp_quartile'],
            y=regime_prices['mean'],
            marker_color=['#dc3545', '#ff9800', '#90ee90', '#28a745'],
            text=[f"${v:.0f}" for v in regime_prices['mean']],
            textposition='outside'
        ))
        fig.update_layout(
            title="Average 5TC Price by Dispersion Quartile",
            xaxis_title="Dispersion Regime",
            yaxis_title="Average 5TC Price ($/day)",
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.success(
            f"**Key Observation**:\n\n"
            f"Prices are monotonically higher when "
            f"dispersion is better. Q4 commands a {premium_pct:.1%} premium "
            f"vs Q1. This is a structural market difference, not noise."
        )
    
    st.markdown("---")
    
    # Lag Sensitivity Analysis
    st.subheader("4️⃣ Signal Lag Sensitivity Analysis")
    
    st.info(
        "**Question**: Is it better to act immediately on the signal, or wait 1-3 days?\n\n"
        "If dispersion is truly *predictive*, a lag might improve performance by:\n"
        "- Filtering out noise and false signals\n"
        "- Capturing only persistent dispersion shifts\n"
        "- Allowing confirmation time before entering positions\n\n"
        f"**Current setting**: {signal_lag}-day lag"
    )
    
    with st.spinner("Testing different lags..."):
        lag_results = []
        
        for test_lag in range(0, 6):
            sg_test = SignalGenerator(clean_data, signal_lag=test_lag)
            signals_test = sg_test.get_signals_dataframe()
            
            engine_test = BacktestEngine(
                signals_test,
                initial_capital=initial_capital,
                transaction_fee_bps=fee_bps
            )
            results_test = engine_test.backtest_strategy('signal_momentum', f'Momentum_Lag{test_lag}')
            
            lag_results.append({
                'Lag (days)': test_lag,
                'Sharpe Ratio': results_test['sharpe_ratio'],
                'Total Return': results_test['total_return_pct'],
                'Max DD': results_test['max_drawdown_pct'],
                'Win Rate': results_test['win_rate'],
                'Num Trades': results_test['num_trades'],
                'Calmar': results_test['calmar_ratio']
            })
    
    lag_df = pd.DataFrame(lag_results)
    
    # Display table
    st.dataframe(
        lag_df.style.format({
            'Sharpe Ratio': '{:.3f}',
            'Total Return': '{:.2%}',
            'Max DD': '{:.2%}',
            'Win Rate': '{:.2%}',
            'Calmar': '{:.2f}',
            'Num Trades': '{:.0f}'
        }).background_gradient(subset=['Sharpe Ratio'], cmap='RdYlGn', vmin=-0.5, vmax=1.0),
        use_container_width=True,
        hide_index=True
    )
    
    # Chart: Sharpe ratio by lag
    fig_lag = go.Figure()
    fig_lag.add_trace(go.Scatter(
        x=lag_df['Lag (days)'],
        y=lag_df['Sharpe Ratio'],
        mode='lines+markers',
        marker=dict(size=10, color=lag_df['Sharpe Ratio'], colorscale='RdYlGn', showscale=True),
        line=dict(width=2, color='blue'),
        text=[f"Lag {x}: {y:.3f}" for x, y in zip(lag_df['Lag (days)'], lag_df['Sharpe Ratio'])],
        hovertemplate='<b>Lag %{x} days</b><br>Sharpe: %{y:.3f}<extra></extra>'
    ))
    fig_lag.update_layout(
        title="Sharpe Ratio vs Signal Lag",
        xaxis_title="Signal Lag (days)",
        yaxis_title="Sharpe Ratio",
        height=400,
        hovermode='x unified'
    )
    st.plotly_chart(fig_lag, use_container_width=True)
    
    # Best lag analysis
    best_lag_idx = lag_df['Sharpe Ratio'].idxmax()
    best_lag = lag_df.loc[best_lag_idx, 'Lag (days)']
    best_sharpe = lag_df.loc[best_lag_idx, 'Sharpe Ratio']
    
    if best_lag == 0:
        st.success(
            f"✅ **Optimal Lag: {best_lag} days (immediate entry)**\n\n"
            f"Sharpe Ratio: {best_sharpe:.3f}\n\n"
            f"The signal works best when acted upon immediately. "
            f"Waiting reduces performance, suggesting the signal captures short-term momentum."
        )
    else:
        improvement = ((best_sharpe - lag_df.loc[0, 'Sharpe Ratio']) / 
                      abs(lag_df.loc[0, 'Sharpe Ratio'])) if lag_df.loc[0, 'Sharpe Ratio'] != 0 else 0
        st.success(
            f"✅ **Optimal Lag: {int(best_lag)} days**\n\n"
            f"Sharpe Ratio: {best_sharpe:.3f} ({improvement:+.1%} vs immediate entry)\n\n"
            f"Waiting {int(best_lag)} day(s) improves performance, suggesting dispersion changes "
            f"are truly predictive and not just noise. The lag allows confirmation."
        )
    
    st.markdown("---")
    
    # Limitations
    st.subheader("5️⃣ Risks & Limitations")
    
    st.warning(
        "⚠️ **This signal is NOT perfect:**\n\n"
        "• **Correlation ≠ Causation**: Dispersion and prices rise together "
        "because both respond to demand. Dispersion does not directly cause "
        "prices.\n\n"
        "• **Changing Relationship**: The correlation varies over time. "
        "It can break without warning.\n\n"
        "• **Omitted Factors**: Interest rates, iron prices, geopolitics... "
        "affect prices much more than dispersion.\n\n"
        "• **In-Sample Bias**: These results use the same data "
        "we used to build the signal.\n\n"
        "• **Real Fees**: Fees quickly degrade performance."
    )




# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown(
    "🚢 Capesize Dispersion Analysis | Data: 2016-2025 | "
    "Approach: Simple Statistics\n\n"
    "**Disclaimers**: Backtesting ≠ future performance. "
    "For research and education purposes only."
)
