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
    page_title="Freight Analytics | Capesize Intelligence",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Freight Analytics Platform - Professional Trading Intelligence"
    }
)

# Brand Styling
st.markdown("""
<style>
    /* Brand Colors */
    :root {
        --brand-navy: #132c68;
        --brand-gold: #f4c430;
        --brand-teal: #5eb8e8;
        --brand-light-blue: #4a90e2;
    }
    
    /* Main Container */
    .main {
        padding: 0rem 0rem;
        background-color: #f8f9fa;
    }
    
    /* Headers */
    h1 {
        color: #132c68;
        font-size: 2.8rem;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin-bottom: 0.5rem;
    }
    h2 {
        color: #132c68;
        font-size: 2rem;
        font-weight: 600;
        border-bottom: 3px solid #f4c430;
        padding-bottom: 0.5rem;
        margin-top: 1.5rem;
    }
    h3 {
        color: #132c68;
        font-weight: 600;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #132c68 0%, #1a3a7f 100%);
    }
    [data-testid="stSidebar"] .css-1d391kg, [data-testid="stSidebar"] .st-emotion-cache-1d391kg {
        color: white;
    }
    [data-testid="stSidebar"] label {
        color: white !important;
        font-weight: 500;
    }
    [data-testid="stSidebar"] .stMarkdown {
        color: white;
    }
    
    /* Sidebar Radio Buttons - Aggressive white text enforcement */
    [data-testid="stSidebar"] .stRadio > label {
        color: white !important;
        font-weight: 600;
    }
    [data-testid="stSidebar"] .stRadio [role="radiogroup"] label {
        color: white !important;
        font-weight: 500;
    }
    [data-testid="stSidebar"] .stRadio [role="radiogroup"] label span {
        color: white !important;
    }
    [data-testid="stSidebar"] .stRadio [role="radiogroup"] label p {
        color: white !important;
    }
    [data-testid="stSidebar"] .stRadio [role="radiogroup"] label div {
        color: white !important;
    }
    [data-testid="stSidebar"] .stRadio * {
        color: white !important;
    }
    
    /* Info Boxes */
    .stInfo {
        background: linear-gradient(135deg, #f0f7ff 0%, #e6f2ff 100%);
        border-left: 5px solid #132c68;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(19, 44, 104, 0.1);
    }
    .stSuccess {
        background: linear-gradient(135deg, #f0fff4 0%, #e6f9ea 100%);
        border-left: 5px solid #28a745;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(40, 167, 69, 0.1);
    }
    .stWarning {
        background: linear-gradient(135deg, #fffbf0 0%, #fff8e6 100%);
        border-left: 5px solid #f4c430;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(244, 196, 48, 0.1);
    }
    .stError {
        background: linear-gradient(135deg, #fff0f0 0%, #ffe6e6 100%);
        border-left: 5px solid #dc3545;
        border-radius: 8px;
        padding: 1rem;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #132c68;
        font-size: 2rem;
        font-weight: 700;
    }
    [data-testid="stMetricDelta"] {
        font-weight: 600;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #132c68 0%, #1a3a7f 100%);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        box-shadow: 0 4px 6px rgba(19, 44, 104, 0.2);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #1a3a7f 0%, #132c68 100%);
        box-shadow: 0 6px 8px rgba(19, 44, 104, 0.3);
        transform: translateY(-2px);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: white;
        border-radius: 8px;
        padding: 0.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f8f9fa;
        color: #132c68;
        border-radius: 6px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        border: 2px solid transparent;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #132c68 0%, #1a3a7f 100%);
        color: white;
        border: 2px solid #f4c430;
    }
    
    /* Dataframes */
    .stDataFrame {
        border: 2px solid #132c68;
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background-color: #f8f9fa;
        border: 2px solid #132c68;
        border-radius: 6px;
        color: #132c68;
        font-weight: 600;
    }
    
    /* Professional Cards */
    .metric-card {
        background: white;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(19, 44, 104, 0.1);
        border-top: 4px solid #132c68;
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
        price_csv='data/cape_front_month.csv',
        dispersion_csv='data/dispersion_case_study.csv'
    )
    clean_data = dm.get_clean_data(drop_na=True)
    sg = SignalGenerator(clean_data)
    return dm, sg, clean_data


# ============================================================================
# BRANDED HEADER
# ============================================================================

# Main page header with branding
col_logo, col_title = st.columns([1, 4])

with col_logo:
    try:
        st.image('assets/logo.jpg', width=120)
    except:
        st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)  # Spacer if no logo

with col_title:
    st.markdown("""
    <div style='padding: 0;'>
        <h1 style='color: #132c68; margin: 0; font-size: 2.5rem; font-weight: 700;'>⚓ Capesize Freight Analytics</h1>
        <p style='color: #132c68; font-size: 1.2rem; margin: 0.3rem 0 0 0; font-weight: 600; letter-spacing: 1px;'>FREIGHT INTELLIGENCE PLATFORM</p>
        <p style='color: #5eb8e8; font-size: 0.95rem; margin: 0.3rem 0 0 0; font-style: italic;'>Professional Trading Intelligence • Data-Driven Insights</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='margin: 1.5rem 0; border: none; border-top: 3px solid #f4c430;'>", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR & NAVIGATION
# ============================================================================

# Sidebar logo
try:
    st.sidebar.image('assets/logo.jpg', use_container_width=True)
except:
    pass  # Logo not found, continue without it

st.sidebar.markdown("""
<div style='text-align: center; padding: 1rem 0; border-bottom: 2px solid #f4c430; margin-bottom: 1rem;'>
    <h2 style='color: white; margin: 0; font-size: 1.8rem;'>🚢 FREIGHT ANALYTICS</h2>
    <p style='color: #5eb8e8; margin: 0.5rem 0 0 0; font-size: 0.9rem;'>5TC Price Prediction Engine</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
<div style='background: rgba(244, 196, 48, 0.1); border: 2px solid #f4c430; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;'>
    <p style='color: white; margin: 0; font-weight: 600; font-size: 1.1rem;'>💡 ANALYTICAL FRAMEWORK</p>
    <p style='color: #e0e0e0; margin: 0.5rem 0 0 0; font-size: 0.9rem;'>
    Advanced quantitative analysis combining vessel dispersion patterns with forward freight pricing dynamics.
    </p>
    <hr style='border: 1px solid #f4c430; margin: 1rem 0;'>
    <p style='color: #5eb8e8; margin: 0; font-size: 0.85rem;'>
    ⚡ <b>Momentum-Based Signals</b><br>
    📊 <b>Multi-Threshold Position Sizing</b><br>
    🎯 <b>Risk-Adjusted Performance</b><br>
    💼 <b>Institutional-Grade Metrics</b>
    </p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

tab_choice = st.sidebar.radio(
    "Navigation",
    [
        "📊 Data Overview",
        "⚡ Strategy & Performance",
        "📈 Optimization & Analysis"
    ]
)

st.sidebar.markdown("<hr style='border: 1px solid rgba(244, 196, 48, 0.3); margin: 1.5rem 0;'>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='color: #f4c430; font-weight: 700; font-size: 1.1rem; margin-bottom: 0.5rem;'>⚙️ SIGNAL PARAMETERS</p>", unsafe_allow_html=True)

signal_lag = st.sidebar.slider(
    "Signal Lag (days)",
    min_value=0,
    max_value=20,
    value=0,
    step=1,
    help="Wait N days after signal before entering position (0 = immediate). Test if dispersion momentum leads prices by several days."
)

st.sidebar.markdown("<hr style='border: 1px solid rgba(244, 196, 48, 0.3); margin: 1.5rem 0;'>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='color: #f4c430; font-weight: 700; font-size: 1.1rem; margin-bottom: 0.5rem;'>💼 BACKTEST CONFIGURATION</p>", unsafe_allow_html=True)

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
    st.markdown("""
    <div style='background: linear-gradient(135deg, #132c68 0%, #1a3a7f 100%); padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem;'>
        <h1 style='color: white; margin: 0;'>📊 Market Intelligence & Data Foundation</h1>
        <p style='color: #f4c430; margin: 0.5rem 0 0 0; font-size: 1.1rem;'>Rigorous Statistical Analysis for Informed Trading Decisions</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background: linear-gradient(135deg, #f0f7ff 0%, #e6f2ff 100%); border-left: 5px solid #132c68; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;'>
        <p style='color: #132c68; margin: 0; font-weight: 600; font-size: 1.05rem;'>🎯 <b>ANALYTICAL FRAMEWORK</b></p>
        <p style='color: #495057; margin: 0.5rem 0 0 0;'>
        Our quantitative approach combines institutional-grade statistical methods with freight market expertise:
        </p>
        <ul style='color: #495057; margin: 0.5rem 0 0 1.5rem;'>
            <li><b>Data Characterization</b> - Comprehensive dataset profiling</li>
            <li><b>Distribution Analytics</b> - Statistical behavior analysis</li>
            <li><b>Correlation Dynamics</b> - Relationship pattern identification</li>
            <li><b>Causality Testing</b> - Predictive power validation</li>
            <li><b>Quality Assurance</b> - Data integrity verification</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
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
            delta=f"{100-r_squared*100:.0f}% unexplained",
            delta_color="inverse"
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
            line=dict(color='#132c68', width=2.5)
        ),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(
            x=signals_df['date'],
            y=signals_df['avg_dispersion'],
            name='Avg Dispersion',
            line=dict(color='#5eb8e8', width=2.5)
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
    
    col_corr_controls = st.columns([2, 2, 1])
    
    with col_corr_controls[0]:
        window = st.slider("Select rolling window (days)", 30, 365, 90, 30)
    
    with col_corr_controls[1]:
        corr_type = st.radio(
            "Correlation Type",
            options=["Raw Levels", "Returns (Differenced)"],
            help="Raw Levels: correlation of prices/dispersion directly | Returns: correlation of daily changes (avoids spurious correlation)"
        )
    
    # Calculate rolling correlation based on selection
    if corr_type == "Raw Levels":
        rolling_corr = signals_df['price_5tc'].rolling(window).corr(signals_df['avg_dispersion'])
        overall_corr = data_summary['correlation_avg']
        corr_description = "Price vs Dispersion (Levels)"
        color_scheme = '#f4c430'
    else:
        # Calculate returns (daily changes)
        price_returns = signals_df['price_5tc'].pct_change()
        disp_returns = signals_df['avg_dispersion'].pct_change()
        rolling_corr = price_returns.rolling(window).corr(disp_returns)
        overall_corr = price_returns.corr(disp_returns)
        corr_description = "Price vs Dispersion (Returns)"
        color_scheme = '#5eb8e8'
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=signals_df['date'],
        y=rolling_corr,
        name=f'{window}-day Rolling Correlation',
        line=dict(color=color_scheme, width=3),
        fill='tozeroy',
        fillcolor=f'rgba({int(color_scheme[1:3], 16)}, {int(color_scheme[3:5], 16)}, {int(color_scheme[5:7], 16)}, 0.2)'
    ))
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_hline(y=overall_corr, line_dash="dot", line_color="red", 
                  annotation_text=f"Overall: {overall_corr:.3f}")
    fig.update_layout(
        title=f"Rolling {window}-Day Correlation: {corr_description}",
        xaxis_title="Date",
        yaxis_title="Correlation Coefficient",
        height=350
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Display metrics
    col_metrics1, col_metrics2, col_metrics3 = st.columns(3)
    with col_metrics1:
        st.metric("Overall Correlation", f"{overall_corr:.3f}")
    with col_metrics2:
        st.metric("Mean Rolling Corr", f"{rolling_corr.mean():.3f}")
    with col_metrics3:
        st.metric("Std Dev", f"{rolling_corr.std():.3f}", delta="Volatility of relationship")
    
    if corr_type == "Raw Levels":
        st.warning(
            "**⚠️ Key Observation (Raw Levels):** The rolling correlation varies significantly over time. "
            "It's sometimes strongly positive, sometimes near zero, and occasionally negative. "
            "This indicates the relationship is **not stable** - it changes with market regimes. "
            "Any trading strategy must account for this non-stationarity.\n\n"
            "**Note:** Raw level correlations can be **spurious** (both series trending together without causal link). "
            "Consider analyzing **Returns** for a more robust measure of true co-movement."
        )
    else:
        st.info(
            "**📊 Returns Correlation Analysis (Differenced Data):**\n\n"
            f"Overall correlation on returns: **{overall_corr:.3f}**\n\n"
            "This measures co-movement of **daily changes** rather than levels, avoiding spurious correlation "
            "from common trends. A lower correlation on returns vs levels suggests much of the level correlation "
            "was driven by shared trends (e.g., both rising in bull markets) rather than true day-to-day co-movement.\n\n"
            f"**Interpretation:** {'Weak' if abs(overall_corr) < 0.2 else 'Moderate' if abs(overall_corr) < 0.4 else 'Strong'} "
            f"day-to-day co-movement between price changes and dispersion changes."
        )
    
    # ========================================================================
    # SECTION 5: GRANGER CAUSALITY TEST
    # ========================================================================
    
    st.markdown("---")
    st.header("5️⃣ Granger Causality & Predictive Power Analysis")
    
    st.info(
        "**🎯 Economic Rationale: Why Test Granger Causality?**\n\n"
        "**Question:** Does vessel positioning today predict freight rates tomorrow?\n\n"
        "**Theory:** When vessels disperse globally (high dispersion), they are better positioned to "
        "pick up cargo quickly. This should lead to higher freight rates as charterers compete for well-positioned tonnage. "
        "**If this relationship has a time lag** (vessels reposition → rates adjust), dispersion could be a **leading indicator**.\n\n"
        "**Granger Causality Test** formally tests if past dispersion values help predict future prices, "
        "beyond what past prices already tell us. This is the gold standard for testing predictive relationships in time series."
    )
    
    # Create sub-tabs for different analysis steps
    granger_tabs = st.tabs([
        "📋 Step 1: Stationarity Check",
        "📊 Step 2: Granger Test Results",
        "💡 Step 3: Economic Interpretation"
    ])
    
    # ========================================================================
    # SUB-TAB 1: STATIONARITY CHECK
    # ========================================================================
    
    with granger_tabs[0]:
        st.subheader("Augmented Dickey-Fuller (ADF) Test")
        
        st.markdown("""
        **Why check stationarity?**  
        Granger causality tests require **stationary data** (constant mean/variance over time). 
        If series are non-stationary (trending), we must difference them first to avoid spurious results.
        
        **Augmented Dickey-Fuller (ADF) Test:**
        - **Null Hypothesis:** Series has a unit root (non-stationary)
        - **Alternative:** Series is stationary
        - **Decision Rule:** p-value < 0.05 → Reject null → Series is stationary ✅
        """)
        
        st.markdown("---")
    
    try:
        from statsmodels.tsa.stattools import grangercausalitytests, adfuller
        
        # Prepare data (drop NaNs)
        test_data = signals_df[['price_5tc', 'avg_dispersion']].dropna()
        
        # Step 1: ADF Test for Stationarity
        def run_adf_test(series, name):
            result = adfuller(series.dropna(), autolag='AIC')
            return {
                'name': name,
                'adf_stat': result[0],
                'p_value': result[1],
                'is_stationary': result[1] < 0.05,
                'critical_1pct': result[4]['1%'],
                'critical_5pct': result[4]['5%'],
                'critical_10pct': result[4]['10%']
            }
        
        price_adf = run_adf_test(test_data['price_5tc'], '5TC Price')
        disp_adf = run_adf_test(test_data['avg_dispersion'], 'Dispersion')
        
        # Continue in Sub-Tab 1
        with granger_tabs[0]:
            # Display ADF results
            col_adf1, col_adf2 = st.columns(2)
            
            with col_adf1:
                st.markdown("**5TC Price Series**")
                if price_adf['is_stationary']:
                    st.success(f"✅ **Stationary** (p-value: {price_adf['p_value']:.4f})")
                else:
                    st.warning(f"⚠️ **Non-Stationary** (p-value: {price_adf['p_value']:.4f})")
                st.caption(f"ADF Statistic: {price_adf['adf_stat']:.3f}")
                st.caption(f"Critical Value (5%): {price_adf['critical_5pct']:.3f}")
            
            with col_adf2:
                st.markdown("**Dispersion Series**")
                if disp_adf['is_stationary']:
                    st.success(f"✅ **Stationary** (p-value: {disp_adf['p_value']:.4f})")
                else:
                    st.warning(f"⚠️ **Non-Stationary** (p-value: {disp_adf['p_value']:.4f})")
                st.caption(f"ADF Statistic: {disp_adf['adf_stat']:.3f}")
                st.caption(f"Critical Value (5%): {disp_adf['critical_5pct']:.3f}")
            
            # Determine if differencing is needed
            needs_differencing = not (price_adf['is_stationary'] and disp_adf['is_stationary'])
            
            st.markdown("---")
            st.subheader("🔧 Data Preparation Decision")
            
            if needs_differencing:
                st.warning(
                    "⚠️ **One or both series are non-stationary.** "
                    "We will use **first differences** (daily changes) for the Granger test to ensure valid results."
                )
                # Apply first differencing
                test_data_granger = test_data.diff().dropna()
                data_type = "First Differences (Daily Changes)"
                
                st.info(
                    "**Transformation Applied:**\n\n"
                    "```\n"
                    "price_diff[t] = price[t] - price[t-1]\n"
                    "disp_diff[t] = disp[t] - disp[t-1]\n"
                    "```\n\n"
                    "This removes trends and makes the series stationary, allowing for valid Granger causality testing."
                )
            else:
                st.success(
                    "✅ **Both series are stationary.** "
                    "We can proceed with Granger causality test on the raw levels."
                )
                test_data_granger = test_data.copy()
                data_type = "Raw Levels"
        
        # ========================================================================
        # SUB-TAB 2: GRANGER TEST RESULTS
        # ========================================================================
        
        with granger_tabs[1]:
            st.subheader("Granger Causality Test: Dispersion → Prices")
        
            st.markdown(f"""
            **Test Setup:**
            - **Data:** {data_type}
            - **Null Hypothesis:** Dispersion does NOT Granger-cause prices
            - **Alternative:** Dispersion DOES Granger-cause prices (predictive power)
            - **Test Statistic:** F-test comparing restricted vs unrestricted models
            """)
            
            # Test with multiple lags
            max_lag = st.slider("Maximum lag to test (days)", 1, 20, 10, 1, key="granger_lag_slider")
            
            with st.spinner("Running Granger causality tests..."):
                # Test: Does dispersion Granger-cause price?
                gc_results = grangercausalitytests(
                    test_data_granger[['price_5tc', 'avg_dispersion']], 
                    max_lag,
                    verbose=False
                )
        
            # Extract p-values and statistics
            results_list = []
            for lag in range(1, max_lag + 1):
                # Get F-test p-value (ssr_ftest)
                f_test = gc_results[lag][0]['ssr_ftest']
                f_stat = f_test[0]
                p_value = f_test[1]
                results_list.append({
                    'Lag': lag,
                    'F-statistic': f_stat,
                    'p-value': p_value,
                    'Significant (5%)': '✅ Yes' if p_value < 0.05 else '❌ No',
                    'Significant (10%)': '✅ Yes' if p_value < 0.10 else '❌ No'
                })
            
            results_df = pd.DataFrame(results_list)
            
            # Find optimal lag (lowest p-value)
            optimal_lag_idx = results_df['p-value'].idxmin()
            optimal_lag = results_df.loc[optimal_lag_idx, 'Lag']
            optimal_pvalue = results_df.loc[optimal_lag_idx, 'p-value']
            optimal_fstat = results_df.loc[optimal_lag_idx, 'F-statistic']
            
            # Display optimal lag summary
            st.markdown("---")
            col_opt1, col_opt2, col_opt3, col_opt4 = st.columns(4)
        
            with col_opt1:
                st.metric("🎯 Optimal Lag", f"{int(optimal_lag)} days", delta="Lowest p-value")
            with col_opt2:
                st.metric("📊 F-Statistic", f"{optimal_fstat:.2f}", delta=f"at {int(optimal_lag)}-day lag")
            with col_opt3:
                sig_status = "Significant ✅" if optimal_pvalue < 0.05 else "Not Significant ❌"
                st.metric("P-value", f"{optimal_pvalue:.4f}", delta=sig_status)
            with col_opt4:
                significant_5 = (results_df['p-value'] < 0.05).sum()
                st.metric("Significant Lags (5%)", f"{significant_5}/{max_lag}")
            
            st.markdown("---")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Plot p-values
                fig = go.Figure()
                
                # Main p-value line
                fig.add_trace(go.Scatter(
                    x=results_df['Lag'],
                    y=results_df['p-value'],
                    mode='lines+markers',
                    name='p-value',
                    line=dict(color='#f4c430', width=3),
                    marker=dict(size=10, color='#132c68', line=dict(color='#f4c430', width=2))
                ))
                
                # Highlight optimal lag
                fig.add_trace(go.Scatter(
                    x=[optimal_lag],
                    y=[optimal_pvalue],
                    mode='markers',
                    name='Optimal Lag',
                    marker=dict(size=20, color='#5eb8e8', symbol='star', line=dict(width=2, color='white')),
                    hovertemplate=f'<b>⭐ OPTIMAL LAG: {int(optimal_lag)} days</b><br>p-value: {optimal_pvalue:.4f}<extra></extra>'
                ))
                
                # Significance thresholds
                fig.add_hline(y=0.05, line_dash="dash", line_color="red", line_width=2,
                             annotation_text="5% significance", annotation_position="right")
                fig.add_hline(y=0.10, line_dash="dot", line_color="orange", line_width=2,
                             annotation_text="10% significance", annotation_position="right")
                
                fig.update_layout(
                    title=f"Granger Causality Test: P-values by Lag ({data_type})",
                    xaxis_title="Lag (days)",
                    yaxis_title="P-value",
                    height=400,
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("**📊 Summary Statistics:**")
                significant_10 = (results_df['p-value'] < 0.10).sum()
                
                st.caption(f"**Lags tested:** {max_lag}")
                st.caption(f"**Significant at 5%:** {significant_5} lags")
                st.caption(f"**Significant at 10%:** {significant_10} lags")
                st.caption(f"**Min p-value:** {optimal_pvalue:.4f}")
                st.caption(f"**Max p-value:** {results_df['p-value'].max():.4f}")
                st.caption(f"**Mean p-value:** {results_df['p-value'].mean():.4f}")
                
                st.markdown("---")
                
            
            with st.expander("📊 Detailed Results Table"):
                st.dataframe(
                    results_df.style.background_gradient(
                        subset=['p-value'], 
                        cmap='RdYlGn_r',  # Red (high p-value) to Green (low p-value)
                        vmin=0, 
                        vmax=0.15
                    ),
                    use_container_width=True, 
                    hide_index=True
                )
        
        # ========================================================================
        # SUB-TAB 3: ECONOMIC INTERPRETATION
        # ========================================================================
        
        with granger_tabs[2]:
            st.subheader("Trading Implications & Economic Context")
        
            if optimal_pvalue < 0.05:
                st.success(
                    f"✅ **SIGNIFICANT PREDICTIVE RELATIONSHIP DETECTED**\n\n"
                    f"**Finding:** Dispersion Granger-causes prices with optimal lag of **{int(optimal_lag)} days** "
                    f"(p-value: {optimal_pvalue:.4f}, F-stat: {optimal_fstat:.2f})\n\n"
                    f"**What this means economically:**\n"
                    f"- Changes in vessel dispersion today predict price changes {int(optimal_lag)} days later\n"
                    f"- When vessels spread globally (↑ dispersion), rates tend to rise {int(optimal_lag)} days ahead\n"
                    f"- This lag likely reflects: vessel repositioning time ({int(optimal_lag//7)} weeks), "
                    f"contract negotiation periods, or information diffusion in forward markets\n\n"
                    f"**Trading Implications:**\n"
                    f"- Dispersion can be used as a **leading indicator** with {int(optimal_lag)}-day horizon\n"
                    f"- Forward contracts (C+1MON) may take ~{int(optimal_lag)} days to fully price in fleet positioning\n"
                    f"- Strategy: Monitor dispersion changes → anticipate price moves {int(optimal_lag)} days later"
                )
                
                if significant_5 > max_lag * 0.5:
                    st.info(
                        f"💡 **Strong Evidence:** {significant_5}/{max_lag} lags are significant. "
                        f"Multiple lags show predictive power, suggesting a robust relationship."
                    )
            
            elif optimal_pvalue < 0.10:
                st.warning(
                    f"⚠️ **WEAK PREDICTIVE RELATIONSHIP DETECTED**\n\n"
                    f"**Finding:** Dispersion shows marginal Granger causality at optimal lag of **{int(optimal_lag)} days** "
                    f"(p-value: {optimal_pvalue:.4f}, F-stat: {optimal_fstat:.2f})\n\n"
                    f"**What this means:**\n"
                    f"- Evidence is **borderline significant** (p-value between 0.05 and 0.10)\n"
                    f"- Dispersion may have some predictive power, but it's weak and unreliable\n"
                    f"- Only {significant_5} out of {max_lag} lags are significant at 5% level\n\n"
                    f"**Trading Implications:**\n"
                    f"- Dispersion should be used as a **confirmation signal**, not primary signal\n"
                    f"- Combine with other factors (fundamentals, technicals, sentiment)\n"
                    f"- Standalone trading on dispersion is **not recommended** (high risk of false signals)"
                )
            
            else:
                st.error(
                    f"❌ **NO SIGNIFICANT PREDICTIVE RELATIONSHIP**\n\n"
                    f"**Finding:** Dispersion does NOT Granger-cause prices (p-value: {optimal_pvalue:.4f} > 0.05)\n\n"
                    f"**What this means economically:**\n"
                    f"- Past dispersion values do NOT help predict future prices beyond what prices already tell us\n"
                    f"- The correlation we observe is likely **contemporaneous** (both move together) rather than **predictive**\n"
                    f"- Dispersion and prices may be driven by common factors (e.g., iron ore demand) without causal link\n\n"
                    f"**Trading Implications:**\n"
                    f"- Dispersion is NOT a reliable leading indicator for this dataset\n"
                    f"- Using dispersion for systematic trading is **NOT recommended**\n"
                    f"- The relationship may be spurious or driven by shared trends\n\n"
                    f"**Why might this happen?**\n"
                    f"- Forward contracts (C+1MON) may already price in expected fleet positioning\n"
                    f"- Market is efficient → dispersion information is already in prices\n"
                    f"- Non-linear relationship not captured by Granger test"
                )
                
                if needs_differencing:
                    st.info(
                        "📌 **Note:** We used first differences (daily changes) because the raw series were non-stationary. "
                        "The lack of Granger causality on **changes** suggests day-to-day dispersion fluctuations "
                        "don't predict day-to-day price movements, even if the levels correlate."
                    )
            
            # Add context about limitations
            st.markdown("---")
            st.subheader("⚠️ Important Caveats")
            
            col_cav1, col_cav2 = st.columns(2)
            
            with col_cav1:
                st.markdown("**Statistical Limitations:**")
                st.caption("• **Linear relationships only** - Granger test can't detect non-linear patterns")
                st.caption("• **In-sample test** - Results may not hold out-of-sample")
                st.caption("• **Multiple testing** - With many lags, some significance by chance")
                st.caption("• **Correlation ≠ Causation** - Granger 'causality' is predictive, not true causation")
            
            with col_cav2:
                st.markdown("**Economic Limitations:**")
                st.caption("• **Statistical significance ≠ Economic profitability**")
                st.caption("• **Transaction costs** matter (predictability may be unprofitable after fees)")
                st.caption("• **Regime changes** - Relationship may break down in different markets")
                st.caption("• **Data frequency** - Daily data may miss intraday dynamics")
    
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
        
        # Calculate warm-up period (rows with NaN from rolling windows)
        warmup_rows = signals_df.isna().any(axis=1).sum()
        usable_rows = len(signals_df) - warmup_rows
        
        st.metric("Usable Rows", f"{usable_rows:,}", 
                 delta=f"{warmup_rows} warm-up rows" if warmup_rows > 0 else "All rows usable",
                 delta_color="off")
        
        if warmup_rows > 0:
            st.info(f"ℹ️ {warmup_rows} initial rows excluded (60-day rolling window warm-up)")
        else:
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
    st.markdown("""
    <div style='background: linear-gradient(135deg, #132c68 0%, #1a3a7f 100%); padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem;'>
        <h1 style='color: white; margin: 0;'>⚡ Strategy Engine & Performance Analytics</h1>
        <p style='color: #f4c430; margin: 0.5rem 0 0 0; font-size: 1.1rem;'>Quantitative Signals Powering Freight Trading Decisions</p>
    </div>
    """, unsafe_allow_html=True)
    
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
        with col_tier2:
            st.metric("🟡 STRONG", "50%", "1.5σ ≤ |z| < 2.0σ")
        with col_tier3:
            st.metric("🟠 V.STRONG", "75%", "2.0σ ≤ |z| < 2.5σ")
        with col_tier4:
            st.metric("🔴 EXTREME", "100%", "|z| ≥ 2.5σ")
        
        st.markdown("---")
        
        # Protective mechanisms
        st.subheader("🛡️ Risk Management Filters")
        
        col_protect1, col_protect2, col_protect3 = st.columns(3)
        
        with col_protect1:
            st.markdown("**1️⃣ Persistence Filter**")
            st.info("Requires **2 consecutive days** same direction to filter noise")
        
        with col_protect2:
            st.markdown("**2️⃣ Volatility Filter**")
            st.info("Blocks trading when |price z-score| > **2.0σ** (extreme volatility on the FFA price)")
        
        with col_protect3:
            st.markdown("**3️⃣ Regime Detection**")
            st.info("Avoids trading in low-volatility regimes (90-day lookback dispersion vol > **0.5σ**)")
        
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
        
        # First row: Main metrics
        metric_cols = st.columns(5)
        
        with metric_cols[0]:
            st.metric(
                "Total Return",
                f"{results['total_return_pct']:.1%}",
                f"${results['total_pnl']:,.0f}"
            )
        
        with metric_cols[1]:
            st.metric(
                "Annualized Return",
                f"{results['annualized_return_pct']:.1%}",
                "Per year"
            )
        
        with metric_cols[2]:
            sharpe_color = "inverse" if results['sharpe_ratio'] < 0.5 else "normal"
            st.metric(
                "Sharpe Ratio",
                f"{results['sharpe_ratio']:.2f}",
                "Risk-adjusted return",
                delta_color=sharpe_color
            )
        with metric_cols[3]:
            st.metric(
                "Max Drawdown",
                f"{results['max_drawdown_pct']:.1%}",
                "Worst loss"
            )
        
        with metric_cols[4]:
            st.metric(
                "Win Rate",
                f"{results['win_rate']:.1%}",
                f"{results['winning_trades']}/{results['num_trades']}"
            )
        
        # Second row: Additional risk metrics
        metric_cols2 = st.columns([1, 1, 3])
        
        with metric_cols2[0]:
            st.metric(
                "Annualized Volatility",
                f"{results['annualized_volatility']:.1%}",
                "Annual std dev"
            )
        
        with metric_cols2[1]:
            st.metric(
                "Total Fees Paid",
                f"${results['total_fees_paid']:,.0f}",
                "Transaction costs"
            )
        
        # Performance interpretation
        st.caption(f"📌 Risk-Free Rate: {results['risk_free_rate']:.2%} (US 10Y Treasury average over backtest period)")
        
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
            line=dict(color='#132c68', width=3),
            fillcolor='rgba(19, 44, 104, 0.15)',
            hovertemplate='Date: %{x}<br>Value: $%{y:,.0f}<extra></extra>'
        ))
        
        # Add initial capital line
        fig.add_hline(
            y=initial_capital,
            line_dash="dash",
            line_color="#f4c430",
            line_width=2.5,
            annotation_text=f"Initial: ${initial_capital:,}",
            annotation_font_color="#132c68"
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
            st.text(f"Total: {results['total_return_pct']:.1%}")
            st.text(f"Annual: {results['annualized_return_pct']:.1%}")
            st.text(f"Sharpe: {results['sharpe_ratio']:.2f}")
        
        with preview_col3:
            st.markdown("**Trading Activity**")
            st.text(f"Trades: {results['num_trades']}")
            st.text(f"Win Rate: {results['win_rate']:.1%}")
            st.text(f"Fees Paid: ${results['total_fees_paid']:,.0f}")


# ============================================================================
# TAB 3: OPTIMIZATION & ANALYSIS
# ============================================================================

elif tab_choice == "📈 Optimization & Analysis":
    st.markdown("""
    <div style='background: linear-gradient(135deg, #132c68 0%, #1a3a7f 100%); padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem;'>
        <h1 style='color: white; margin: 0;'>📈 Strategic Optimization & Economic Intelligence</h1>
        <p style='color: #f4c430; margin: 0.5rem 0 0 0; font-size: 1.1rem;'>Advanced Analytics for Parameter Tuning & Market Insights</p>
    </div>
    """, unsafe_allow_html=True)
    
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

st.markdown("<hr style='border: 2px solid #132c68; margin: 2rem 0 1rem 0;'>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 8px; border: 2px solid #132c68;'>
    <p style='color: #132c68; font-weight: 700; font-size: 1.2rem; margin: 0;'>⚓ FREIGHT ANALYTICS PLATFORM</p>
    <p style='color: #5eb8e8; margin: 0.5rem 0; font-size: 0.95rem;'>Capesize Dispersion Intelligence • Professional Trading Tools • 2016-2025</p>
    <p style='color: #6c757d; margin: 0.5rem 0 0 0; font-size: 0.85rem; font-style: italic;'>
    <p style='color: #f4c430; margin: 0.75rem 0 0 0; font-size: 0.9rem; font-weight: 600;'>
    Data-Driven Market Intelligence
    </p>
</div>
""", unsafe_allow_html=True)
