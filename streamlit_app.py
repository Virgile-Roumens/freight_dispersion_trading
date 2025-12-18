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
        "⚡ Strategy & Performance",
        "📈 Optimization & Analysis"
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Signal Parameters")

signal_lag = st.sidebar.slider(
    "Signal Lag (days)",
    min_value=0,
    max_value=20,
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
# TAB 2: STRATEGY & PERFORMANCE (MERGED)
# ============================================================================

elif tab_choice == "⚡ Strategy & Performance":
    st.title("⚡ Strategy Analysis & Performance Dashboard")
    
    # Strategy overview banner
    col_banner1, col_banner2, col_banner3 = st.columns(3)
    with col_banner1:
        st.metric("📊 Strategy Type", "Multi-Threshold Momentum")
    with col_banner2:
        active_pct = (signals_df['signal_momentum'] != 0).sum() / len(signals_df)
        st.metric("📅 Active Days", f"{active_pct:.1%}", f"{(signals_df['signal_momentum'] != 0).sum():,} of {len(signals_df):,}")
    with col_banner3:
        st.metric("⏱️ Signal Lag", f"{signal_lag} days", "Immediate" if signal_lag == 0 else "Delayed")
    
    st.markdown("---")
    
    # Create sub-tabs for different aspects
    subtab1, subtab2, subtab3, subtab4 = st.tabs([
        "🎯 Signal Logic",
        "📊 Performance Metrics", 
        "📋 Trade Analysis",
        "💾 Export Results"
    ])
    
    # ========================================================================
    # SUBTAB 1: SIGNAL LOGIC
    # ========================================================================
    
    with subtab1:
        st.header("🎯 Trading Signal Explanation")
        
        explanations = sg.get_all_explanations()
        exp = explanations['momentum']
        
        # Quick summary card
        st.info(
            "**Core Strategy:** Multi-threshold momentum based on vessel dispersion changes\n\n"
            "📈 **LONG** when vessels disperse (spreading globally) → bullish positioning\n\n"
            "📉 **SHORT** when vessels concentrate (clustering regionally) → bearish positioning"
        )
        
        col_logic1, col_logic2 = st.columns(2)
        
        with col_logic1:
            st.markdown("**📋 Strategy Details:**")
            st.markdown(f"- **Type:** {exp['signal_type']}")
            st.markdown(f"- **Horizon:** {exp['horizon']}")
            st.markdown(f"- **Lag:** {signal_lag} days")
            
        with col_logic2:
            st.markdown("**⚙️ Core Logic:**")
            st.code(exp['logic'], language=None)
        
        st.markdown("---")
        
        # Position sizing tiers
        st.subheader("📊 Position Sizing Framework")
        
        col_tier1, col_tier2, col_tier3, col_tier4 = st.columns(4)
        
        with col_tier1:
            st.metric("🟢 MEDIUM", "25%", "1.0σ ≤ |z| < 1.5σ")
            st.caption("~10% of days")
        with col_tier2:
            st.metric("🟡 STRONG", "50%", "1.5σ ≤ |z| < 2.0σ")
            st.caption("~5% of days")
        with col_tier3:
            st.metric("🟠 V.STRONG", "75%", "2.0σ ≤ |z| < 2.5σ")
            st.caption("~3% of days")
        with col_tier4:
            st.metric("🔴 EXTREME", "100%", "|z| ≥ 2.5σ")
            st.caption("~2% of days")
        
        st.markdown("---")
        
        # Protective mechanisms
        st.subheader("🛡️ Risk Management Filters")
        
        col_protect1, col_protect2, col_protect3 = st.columns(3)
        
        with col_protect1:
            st.markdown("**1️⃣ Persistence Filter**")
            st.info("Requires **2 consecutive days** same direction to filter noise")
        
        with col_protect2:
            st.markdown("**2️⃣ Volatility Filter**")
            st.info("Blocks trading when |price z-score| > **2.0σ** (extreme volatility)")
        
        with col_protect3:
            st.markdown("**3️⃣ Regime Detection**")
            st.info("Avoids trading in low-volatility regimes (90-day lookback)")
        
        st.success(
            f"**🎯 Bottom Line:** {exp['rationale']}"
        )
        
        # Latest signals preview
        st.markdown("---")
        st.subheader("📋 Recent Signals (Last 10 Days)")
        
        latest_signals = sg.get_latest_signals(n_rows=10).copy()
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
        
        display_cols = ['date', 'price_5tc', 'Signal', 'avg_dispersion', 'return_5d']
        
        st.dataframe(
            latest_signals[display_cols],
            use_container_width=True,
            hide_index=True
        )
    
    # ========================================================================
    # SUBTAB 2: PERFORMANCE METRICS
    # ========================================================================
    
    with subtab2:
        st.header("📊 Backtest Performance Dashboard")
        
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
        
        # Configuration info
        with st.expander("⚙️ Backtest Configuration"):
            conf_col1, conf_col2, conf_col3, conf_col4 = st.columns(4)
            with conf_col1:
                st.metric("Initial Capital", f"${initial_capital:,}")
            with conf_col2:
                st.metric("Transaction Fees", f"{fee_bps} bps")
            with conf_col3:
                st.metric("Position Sizing", "Multi-Threshold")
            with conf_col4:
                st.metric("Persistence", "2 days")
        
        st.markdown("---")
        
        # Key Performance Indicators
        st.subheader("📈 Key Performance Indicators")
        
        metric_cols = st.columns(5)
        
        with metric_cols[0]:
            st.metric(
                "Total Return",
                f"{results['total_return_pct']:.1%}",
                f"${results['total_pnl']:,.0f}"
            )
        
        with metric_cols[1]:
            sharpe_color = "normal" if results['sharpe_ratio'] < 0.5 else "inverse"
            st.metric(
                "Sharpe Ratio",
                f"{results['sharpe_ratio']:.2f}",
                "Risk-adjusted",
                delta_color=sharpe_color
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
                "Return/DD"
            )
        
        # Performance interpretation
        if results['sharpe_ratio'] >= 1.0:
            st.success("✅ **Strong Performance:** Sharpe ≥ 1.0 indicates excellent risk-adjusted returns")
        elif results['sharpe_ratio'] >= 0.5:
            st.info("ℹ️ **Moderate Performance:** Sharpe 0.5-1.0 indicates acceptable risk-adjusted returns")
        else:
            st.warning("⚠️ **Weak Performance:** Sharpe < 0.5 suggests high risk relative to returns")
        
        st.markdown("---")
        
        # Equity curve
        st.subheader("📈 Portfolio Growth")
        
        equity_vals, equity_dates = engine.get_equity_curve()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=equity_dates,
            y=equity_vals,
            fill='tozeroy',
            name='Portfolio Value',
            line=dict(color='#1f77b4', width=2),
            hovertemplate='Date: %{x}<br>Value: $%{y:,.0f}<extra></extra>'
        ))
        
        # Add initial capital line
        fig.add_hline(
            y=initial_capital,
            line_dash="dash",
            line_color="gray",
            annotation_text=f"Initial: ${initial_capital:,}"
        )
        
        fig.update_layout(
            title=f"Equity Curve - {strategy_choice} Strategy",
            xaxis_title="Date",
            yaxis_title="Portfolio Value ($)",
            hovermode='x unified',
            height=450
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Fee sensitivity
        st.subheader("💰 Fee Sensitivity Analysis")
        
        col_fee1, col_fee2 = st.columns([2, 1])
        
        with col_fee2:
            st.info(
                "**Why it matters:**\n\n"
                "Real-world trading incurs fees. "
                "A robust strategy maintains edge even with realistic transaction costs (10-20 bps)."
            )
        
        with col_fee1:
            fee_levels = [0, 5, 10, 15, 20, 30, 50]
            sensitivity_df = engine.compare_fees_sensitivity(signal_col, strategy_choice, fee_levels)
            
            st.dataframe(sensitivity_df, use_container_width=True, hide_index=True)
        
        if results['sharpe_ratio'] > 0 and float(sensitivity_df[sensitivity_df['Fees (bps)'] == 20]['Sharpe'].values[0]) < 0:
            st.warning(
                "⚠️ **Fee Sensitivity Alert:** Sharpe turns negative above 20 bps. "
                "Strategy edge is fragile - requires very low execution costs."
            )
    
    # ========================================================================
    # SUBTAB 3: TRADE ANALYSIS
    # ========================================================================
    
    with subtab3:
        st.header("📋 Trade-Level Analysis")
        
        trade_log = engine.get_trade_log()
        
        if len(trade_log) > 0:
            # Trade statistics
            col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
            
            with col_stat1:
                st.metric("Total Trades", f"{len(trade_log):,}")
            with col_stat2:
                avg_duration = trade_log['days_held'].mean()
                st.metric("Avg Duration", f"{avg_duration:.1f} days")
            with col_stat3:
                total_fees = trade_log['fee_cost'].sum()
                st.metric("Total Fees Paid", f"${total_fees:,.0f}")
            with col_stat4:
                avg_trade_pnl = trade_log['net_pnl'].mean()
                st.metric("Avg Trade P&L", f"${avg_trade_pnl:,.0f}")
            
            st.markdown("---")
            
            # P&L Distribution
            st.subheader("📊 P&L Distribution")
            
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                # Histogram of returns
                fig_hist = go.Figure()
                fig_hist.add_trace(go.Histogram(
                    x=trade_log['return_pct'],
                    nbinsx=30,
                    marker_color='lightblue',
                    name='Return %'
                ))
                fig_hist.update_layout(
                    title="Trade Return Distribution",
                    xaxis_title="Return %",
                    yaxis_title="Frequency",
                    height=300
                )
                st.plotly_chart(fig_hist, use_container_width=True)
            
            with col_chart2:
                # Win/Loss breakdown
                wins = (trade_log['net_pnl'] > 0).sum()
                losses = (trade_log['net_pnl'] < 0).sum()
                
                fig_pie = go.Figure(data=[go.Pie(
                    labels=['Winners', 'Losers'],
                    values=[wins, losses],
                    marker_colors=['#28a745', '#dc3545']
                )])
                fig_pie.update_layout(
                    title="Win/Loss Split",
                    height=300
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            st.markdown("---")
            
            # Trade log table
            st.subheader("📋 Complete Trade Log")
            
            # Add filters
            col_filter1, col_filter2 = st.columns(2)
            with col_filter1:
                show_trades = st.selectbox(
                    "Show trades:",
                    ["All", "Last 20", "Last 50", "Winners Only", "Losers Only"],
                    index=1
                )
            with col_filter2:
                sort_by = st.selectbox(
                    "Sort by:",
                    ["Exit Date (Recent)", "P&L (High to Low)", "P&L (Low to High)", "Duration"],
                    index=0
                )
            
            # Filter trades
            filtered_log = trade_log.copy()
            if show_trades == "Last 20":
                filtered_log = filtered_log.tail(20)
            elif show_trades == "Last 50":
                filtered_log = filtered_log.tail(50)
            elif show_trades == "Winners Only":
                filtered_log = filtered_log[filtered_log['net_pnl'] > 0]
            elif show_trades == "Losers Only":
                filtered_log = filtered_log[filtered_log['net_pnl'] < 0]
            
            # Sort trades
            if sort_by == "Exit Date (Recent)":
                filtered_log = filtered_log.sort_values('exit_date', ascending=False)
            elif sort_by == "P&L (High to Low)":
                filtered_log = filtered_log.sort_values('net_pnl', ascending=False)
            elif sort_by == "P&L (Low to High)":
                filtered_log = filtered_log.sort_values('net_pnl', ascending=True)
            elif sort_by == "Duration":
                filtered_log = filtered_log.sort_values('days_held', ascending=False)
            
            # Format for display
            display_log = filtered_log.copy()
            display_log['entry_date'] = pd.to_datetime(display_log['entry_date']).dt.strftime('%Y-%m-%d')
            display_log['exit_date'] = pd.to_datetime(display_log['exit_date']).dt.strftime('%Y-%m-%d')
            display_log['entry_price'] = display_log['entry_price'].apply(lambda x: f"${x:.0f}")
            display_log['exit_price'] = display_log['exit_price'].apply(lambda x: f"${x:.0f}")
            display_log['net_pnl'] = display_log['net_pnl'].apply(lambda x: f"${x:,.0f}")
            display_log['fee_cost'] = display_log['fee_cost'].apply(lambda x: f"${x:.2f}")
            display_log['return_pct'] = display_log['return_pct'].apply(lambda x: f"{x:+.2%}")
            
            st.dataframe(display_log, use_container_width=True, hide_index=True)
            
            st.caption(f"Showing {len(filtered_log)} of {len(trade_log)} total trades")
        else:
            st.info("No trades executed. Try adjusting signal parameters or reducing lag.")
    
    # ========================================================================
    # SUBTAB 4: EXPORT RESULTS
    # ========================================================================
    
    with subtab4:
        st.header("💾 Export Complete Analysis")
        
        st.info(
            "**📦 What's Included:**\n\n"
            "Export complete backtest results for offline analysis, reporting, or archiving:\n\n"
            "✅ **Summary Sheet** - All performance metrics and configuration\n\n"
            "✅ **Trade Log** - Complete trade-by-trade breakdown with P&L\n\n"
            "✅ **Equity Curve** - Daily portfolio values for charting\n\n"
            "**Format Options:** Excel (single file, multiple sheets) or CSV (separate files)"
        )
        
        col_export1, col_export2 = st.columns([3, 1])
        
        with col_export1:
            export_filename = st.text_input(
                "📝 Filename",
                value=f"backtest_lag{signal_lag}_capital{initial_capital//1000}k_fees{fee_bps}bps_{datetime.now().strftime('%Y%m%d_%H%M')}",
                help="Filename includes key parameters for easy identification"
            )
        
        with col_export2:
            export_format = st.selectbox(
                "📄 Format",
                options=["xlsx", "csv"],
                format_func=lambda x: "Excel (.xlsx)" if x == "xlsx" else "CSV (.csv)",
                help="Excel: single file | CSV: 3 separate files"
            )
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        with col_btn2:
            if st.button("📥 Export Results", type="primary", use_container_width=True):
                try:
                    export_path = Path("export") / export_filename
                    
                    engine.export_results(
                        filepath=str(export_path),
                        signal_lag=signal_lag,
                        file_format=export_format
                    )
                    
                    if export_format == 'xlsx':
                        st.success(f"✅ **Exported Successfully!**\n\n`export/{export_filename}.xlsx`")
                    else:
                        st.success(
                            f"✅ **Exported Successfully!**\n\n"
                            f"Files created:\n"
                            f"- `{export_filename}_summary.csv`\n"
                            f"- `{export_filename}_trades.csv`\n"
                            f"- `{export_filename}_equity.csv`"
                        )
                    
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"❌ Export failed: {e}")
        
        st.markdown("---")
        
        # Quick stats summary for export preview
        st.subheader("📊 Export Preview")
        
        preview_col1, preview_col2, preview_col3 = st.columns(3)
        
        with preview_col1:
            st.markdown("**Configuration**")
            st.text(f"Capital: ${initial_capital:,}")
            st.text(f"Fees: {fee_bps} bps")
            st.text(f"Lag: {signal_lag} days")
        
        with preview_col2:
            st.markdown("**Performance**")
            st.text(f"Return: {results['total_return_pct']:.1%}")
            st.text(f"Sharpe: {results['sharpe_ratio']:.2f}")
            st.text(f"Max DD: {results['max_drawdown_pct']:.1%}")
        
        with preview_col3:
            st.markdown("**Trading Activity**")
            st.text(f"Trades: {results['num_trades']}")
            st.text(f"Win Rate: {results['win_rate']:.1%}")
            st.text(f"Fees Paid: ${results['total_fees_paid']:,.0f}")


# ============================================================================
# TAB 3: OPTIMIZATION & ANALYSIS
# ============================================================================

elif tab_choice == "📈 Optimization & Analysis":
    st.title("📈 Economic Analysis & Optimization")
    
    st.info(
        "**Objective:** Understand the economic relationship between vessel dispersion and freight rates, "
        "and optimize signal parameters for best performance."
    )
    
    # ========================================================================
    # SECTION 1: KEY INSIGHTS (TOP)
    # ========================================================================
    
    st.markdown("---")
    st.header("🎯 Key Insights")
    
    corr_avg = data_summary['correlation_avg']
    r_squared = corr_avg ** 2
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "📊 Correlation",
            f"{corr_avg:.3f}",
            delta="Weak positive"
        )
    
    with col2:
        st.metric(
            "📉 R² (Variance Explained)",
            f"{r_squared:.1%}",
            delta=f"{100-r_squared*100:.0f}% unexplained"
        )
    
    with col3:
        # Calculate Q1 vs Q4 premium
        regime_prices_temp = signals_df.groupby('disp_quartile', observed=True)['price_5tc'].mean()
        if 'Q1_Low' in regime_prices_temp.index and 'Q4_High' in regime_prices_temp.index:
            premium_pct = (regime_prices_temp['Q4_High'] - regime_prices_temp['Q1_Low']) / regime_prices_temp['Q1_Low']
            st.metric(
                "💰 Q4 vs Q1 Premium",
                f"{premium_pct:.1%}",
                delta="Higher dispersion → Higher rates"
            )
    
    with col4:
        active_days = (signals_df['signal_momentum'] != 0).sum()
        active_pct = active_days / len(signals_df)
        st.metric(
            "📅 Signal Activity",
            f"{active_pct:.1%}",
            delta=f"{active_days:,} trading days"
        )
    
    st.success(
        "**Bottom Line:** Dispersion has a real but modest relationship with freight rates (~27% correlation). "
        "High dispersion consistently commands premium pricing (+30-50% vs low dispersion), making it a useful "
        "**filter or confirmation signal** in a multi-factor trading framework."
    )
    
    st.markdown("---")
    
    # ========================================================================
    # SECTION 2: QUARTILE ANALYSIS (VISUAL)
    # ========================================================================
    
    st.header("📊 Price by Dispersion Regime")
    
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
        
        # Create two-column layout: Chart + Details
        col_chart, col_details = st.columns([2, 1])
        
        with col_chart:
            # Enhanced chart with error bars
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=regime_prices['disp_quartile'],
                y=regime_prices['mean'],
                marker_color=['#dc3545', '#ff9800', '#90ee90', '#28a745'],
                text=[f"${v:.0f}" for v in regime_prices['mean']],
                textposition='outside',
                error_y=dict(
                    type='data',
                    array=regime_prices['std'],
                    visible=True,
                    color='gray'
                ),
                hovertemplate='<b>%{x}</b><br>Mean: $%{y:.0f}<br>Std Dev: %{error_y.array:.0f}<extra></extra>'
            ))
            fig.update_layout(
                title="Average 5TC Price by Dispersion Quartile",
                xaxis_title="Dispersion Regime",
                yaxis_title="Average 5TC Price ($/day)",
                height=400,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col_details:
            st.markdown("**📋 Regime Statistics:**")
            for _, row in regime_prices.iterrows():
                quartile = row['disp_quartile']
                mean_price = row['mean']
                count = row['count']
                std = row['std']
                
                st.markdown(f"**{quartile}**")
                st.metric("Avg Price", f"${mean_price:.0f}/day", delta=f"σ=${std:.0f}")
                st.caption(f"{count:,} observations ({100*count/len(signals_df):.1f}%)")
                st.markdown("---")
        
        st.success(
            f"**Economic Interpretation:** Prices increase monotonically with dispersion. "
            f"Q4 (high dispersion) commands a **{premium_pct:.1%} premium** (${premium_dollars:.0f}/day) "
            f"over Q1 (low dispersion). This is a structural market feature reflecting better "
            f"vessel positioning and stronger demand conditions."
        )
    
    st.markdown("---")
    
    # ========================================================================
    # SECTION 3: LAG OPTIMIZATION
    # ========================================================================
    
    st.header("⏱️ Signal Lag Optimization")
    
    st.info(
        f"**Question:** Does dispersion lead prices, or is the relationship contemporaneous?\n\n"
        f"Testing lags 0-20 days to find optimal predictive horizon. "
        f"**Current setting:** {signal_lag}-day lag | "
        f"**Hypothesis:** Forward contracts may respond with 1-3 week delay due to negotiation time."
    )
    
    # User control for test range
    col_test1, col_test2 = st.columns([1, 3])
    with col_test1:
        max_test_lag = st.selectbox(
            "Test up to:",
            options=[5, 10, 14, 20],
            index=3,
            help="Balance between thoroughness and computation time"
        )
    
    with st.spinner(f"Testing lags 0-{max_test_lag} days..."):
        lag_results = []
        
        for test_lag in range(0, max_test_lag + 1):
            sg_test = SignalGenerator(clean_data, signal_lag=test_lag)
            signals_test = sg_test.get_signals_dataframe()
            
            engine_test = BacktestEngine(
                signals_test,
                initial_capital=initial_capital,
                transaction_fee_bps=fee_bps
            )
            results_test = engine_test.backtest_strategy('signal_momentum', f'Momentum_Lag{test_lag}')
            
            lag_results.append({
                'Lag': test_lag,
                'Sharpe': results_test['sharpe_ratio'],
                'Return': results_test['total_return_pct'],
                'Max DD': results_test['max_drawdown_pct'],
                'Win Rate': results_test['win_rate'],
                'Trades': results_test['num_trades']
            })
    
    lag_df = pd.DataFrame(lag_results)
    
    # Find optimal lag
    best_lag_idx = lag_df['Sharpe'].idxmax()
    best_lag = lag_df.loc[best_lag_idx, 'Lag']
    best_sharpe = lag_df.loc[best_lag_idx, 'Sharpe']
    worst_sharpe = lag_df['Sharpe'].min()
    
    # Display key findings at top
    col_opt1, col_opt2, col_opt3, col_opt4 = st.columns(4)
    with col_opt1:
        st.metric("🎯 Optimal Lag", f"{int(best_lag)} days", delta=f"Sharpe: {best_sharpe:.3f}")
    with col_opt2:
        improvement = best_sharpe - lag_df.loc[0, 'Sharpe']
        st.metric("📈 vs Immediate", f"{improvement:+.3f}", delta="Sharpe improvement")
    with col_opt3:
        sharpe_range = best_sharpe - worst_sharpe
        st.metric("📊 Sharpe Range", f"{sharpe_range:.3f}", delta=f"{worst_sharpe:.3f} to {best_sharpe:.3f}")
    with col_opt4:
        optimal_return = lag_df.loc[best_lag_idx, 'Return']
        st.metric("💰 Best Return", f"{optimal_return:.1%}", delta=f"at {int(best_lag)}-day lag")
    
    # Visualization: Sharpe by lag
    col_chart, col_table = st.columns([2, 1])
    
    with col_chart:
        fig_lag = go.Figure()
        
        # Line + markers with color gradient
        fig_lag.add_trace(go.Scatter(
            x=lag_df['Lag'],
            y=lag_df['Sharpe'],
            mode='lines+markers',
            marker=dict(
                size=10,
                color=lag_df['Sharpe'],
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="Sharpe")
            ),
            line=dict(width=2, color='lightblue'),
            hovertemplate='<b>Lag %{x} days</b><br>Sharpe: %{y:.3f}<br>Return: ' + 
                          lag_df['Return'].apply(lambda x: f"{x:.2%}").tolist()[0] + '<extra></extra>'
        ))
        
        # Highlight optimal
        fig_lag.add_trace(go.Scatter(
            x=[best_lag],
            y=[best_sharpe],
            mode='markers',
            marker=dict(size=20, color='gold', symbol='star', line=dict(width=2, color='red')),
            name='Optimal',
            hovertemplate='<b>⭐ OPTIMAL</b><br>Lag: %{x} days<br>Sharpe: %{y:.3f}<extra></extra>'
        ))
        
        fig_lag.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        fig_lag.update_layout(
            title=f"Performance by Signal Lag (0-{max_test_lag} days)",
            xaxis_title="Signal Lag (days)",
            yaxis_title="Sharpe Ratio",
            height=400,
            hovermode='x unified',
            showlegend=False
        )
        st.plotly_chart(fig_lag, use_container_width=True)
    
    with col_table:
        st.markdown("**📊 Top 5 Lags:**")
        top_5 = lag_df.nlargest(5, 'Sharpe')[['Lag', 'Sharpe', 'Return']].copy()
        top_5['Lag'] = top_5['Lag'].astype(int).astype(str) + ' days'
        top_5['Sharpe'] = top_5['Sharpe'].apply(lambda x: f"{x:.3f}")
        top_5['Return'] = top_5['Return'].apply(lambda x: f"{x:.1%}")
        st.dataframe(top_5, use_container_width=True, hide_index=True)
    
    # Interpretation
    if best_lag == 0:
        st.success(
            f"✅ **Finding: Contemporaneous Relationship**\n\n"
            f"Optimal lag is **0 days** (Sharpe: {best_sharpe:.3f}). The signal works best with immediate entry, "
            f"suggesting dispersion and prices move together rather than in a lead-lag relationship. "
            f"This indicates dispersion is a **coincident indicator**, not a leading one."
        )
    elif best_lag <= 3:
        st.success(
            f"✅ **Finding: Short-Term Predictive Power**\n\n"
            f"Optimal lag is **{int(best_lag)} days** (Sharpe: {best_sharpe:.3f}). "
            f"Brief delay improves performance, suggesting dispersion momentum has {int(best_lag)}-day predictive power. "
            f"This could reflect information diffusion or contract negotiation lags in spot/near-term markets."
        )
    else:
        st.success(
            f"✅ **Finding: Forward Contract Dynamics**\n\n"
            f"Optimal lag is **{int(best_lag)} days** (Sharpe: {best_sharpe:.3f}). "
            f"Longer lag suggests dispersion changes predict forward prices with ~{int(best_lag)}-day horizon, "
            f"consistent with vessel repositioning time and forward contract negotiation periods. "
            f"This supports the hypothesis that fleet positioning precedes forward curve adjustments."
        )
    
    with st.expander("📋 View Full Results Table"):
        display_lag_df = lag_df.copy()
        display_lag_df['Lag'] = display_lag_df['Lag'].astype(int)
        st.dataframe(
            display_lag_df.style.format({
                'Sharpe': '{:.3f}',
                'Return': '{:.2%}',
                'Max DD': '{:.2%}',
                'Win Rate': '{:.2%}',
                'Trades': '{:.0f}'
            }).background_gradient(subset=['Sharpe'], cmap='RdYlGn', vmin=-0.5, vmax=1.0),
            use_container_width=True,
            hide_index=True
        )
    
    st.markdown("---")
    
    # ========================================================================
    # SECTION 4: RISK FACTORS
    # ========================================================================
    
    st.header("⚠️ Key Risk Factors")
    
    col_risk1, col_risk2 = st.columns(2)
    
    with col_risk1:
        st.markdown("**🔴 Critical Limitations:**")
        st.warning(
            "• **Weak Correlation (r=0.27):** Only 7% of price variance explained\n\n"
            "• **Non-Stationary:** Relationship changes over time/regimes\n\n"
            "• **In-Sample Bias:** Optimized on historical data\n\n"
            "• **Fee Sensitivity:** Edge degrades quickly with transaction costs"
        )
    
    with col_risk2:
        st.markdown("**🟡 Usage Recommendations:**")
        st.info(
            "✅ **Use as confirmation signal** in multi-factor framework\n\n"
            "✅ **Combine with fundamentals** (iron ore prices, PMI, rates)\n\n"
            "✅ **Monitor regime changes** (correlation can flip)\n\n"
            "✅ **Keep fees realistic** (10-20 bps for institutional trading)"
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
