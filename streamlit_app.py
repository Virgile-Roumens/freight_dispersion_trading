"""
Streamlit Dashboard - User-Friendly Interface for Dispersion Analysis

Tabs:
1. 📊 Data Overview - Correlations, quality, statistical tests
2. 🎯 Signal Explorer - Momentum + Mean Reversion signals
3. 🏬 Backtest Results - Performance, P&L, strategy comparison
4. 📈 Economic Analysis - In-depth statistics
5. 🔬 Lead-Lag Analysis - Cross-correlation diagnostic

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
import glob

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

# Brand Styling — enhanced with better spacing, card styling, animations
st.markdown("""
<style>
    :root {
        --brand-navy: #132c68;
        --brand-gold: #f4c430;
        --brand-teal: #5eb8e8;
        --brand-light-blue: #4a90e2;
        --brand-dark: #0d1f4a;
        --card-shadow: 0 2px 12px rgba(19, 44, 104, 0.08);
    }

    /* Global */
    .main { padding: 0rem 0rem; background-color: #f5f7fb; }
    section[data-testid="stSidebar"] > div { padding-top: 1rem; }

    /* Headers */
    h1 { color: #132c68; font-size: 2.6rem; font-weight: 700; letter-spacing: -0.5px; margin-bottom: 0.3rem; }
    h2 { color: #132c68; font-size: 1.8rem; font-weight: 600; border-bottom: 3px solid #f4c430;
         padding-bottom: 0.5rem; margin-top: 1.5rem; }
    h3 { color: #132c68; font-weight: 600; font-size: 1.2rem; }
    h4 { color: #132c68; font-weight: 600; font-size: 1.05rem; margin-bottom: 0.2rem; }

    /* Sidebar */
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0d1f4a 0%, #132c68 40%, #1a3a7f 100%); }
    [data-testid="stSidebar"] label { color: rgba(255,255,255,0.92) !important; font-weight: 500; font-size: 0.9rem; }
    [data-testid="stSidebar"] .stMarkdown { color: rgba(255,255,255,0.88); }
    [data-testid="stSidebar"] .stRadio label span { color: rgba(255,255,255,0.92) !important; }
    [data-testid="stSidebar"] .stSlider label { color: rgba(255,255,255,0.92) !important; }
    [data-testid="stSidebar"] hr { border-color: rgba(244,196,48,0.3); }

    /* Metrics */
    [data-testid="stMetricValue"] { color: #132c68; font-size: 1.85rem; font-weight: 700; }
    [data-testid="stMetricLabel"] { font-size: 0.82rem; color: #555; font-weight: 500; text-transform: uppercase;
                                     letter-spacing: 0.3px; }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #132c68 0%, #1a3a7f 100%);
        color: white; border: none; border-radius: 8px;
        padding: 0.7rem 1.5rem; font-weight: 600; font-size: 0.9rem;
        box-shadow: 0 4px 12px rgba(19, 44, 104, 0.25);
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        box-shadow: 0 6px 16px rgba(19, 44, 104, 0.35);
        transform: translateY(-1px);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px; background-color: white; border-radius: 10px;
        padding: 0.4rem 0.5rem; box-shadow: var(--card-shadow);
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6; color: #132c68; border-radius: 8px;
        padding: 0.65rem 1.2rem; font-weight: 600; font-size: 0.88rem;
        border: 1px solid transparent; transition: all 0.15s ease;
    }
    .stTabs [data-baseweb="tab"]:hover { background-color: #e4e8f0; }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #132c68 0%, #1a3a7f 100%);
        color: white; border: 2px solid #f4c430;
        box-shadow: 0 2px 8px rgba(19, 44, 104, 0.3);
    }

    /* Info / Warning boxes */
    .stAlert { border-radius: 10px; }

    /* Expanders */
    .streamlit-expanderHeader { font-weight: 600; color: #132c68; font-size: 0.95rem; }

    /* Dataframes */
    .stDataFrame { border-radius: 8px; overflow: hidden; }

    /* Custom card class */
    .metric-card {
        background: white; border-radius: 12px; padding: 1.2rem 1rem;
        box-shadow: var(--card-shadow); border-left: 4px solid #f4c430;
        margin-bottom: 0.5rem;
    }
    .metric-card h4 { margin: 0 0 0.3rem 0; color: #132c68; font-size: 0.8rem;
                       text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; }
    .metric-card .value { font-size: 1.8rem; font-weight: 700; color: #132c68; }
    .metric-card .sub { font-size: 0.78rem; color: #888; margin-top: 0.15rem; }

    /* Signal badge */
    .signal-long { display: inline-block; background: #d4edda; color: #155724; padding: 0.25rem 0.75rem;
                   border-radius: 20px; font-weight: 600; font-size: 0.85rem; }
    .signal-short { display: inline-block; background: #f8d7da; color: #721c24; padding: 0.25rem 0.75rem;
                    border-radius: 20px; font-weight: 600; font-size: 0.85rem; }
    .signal-flat { display: inline-block; background: #e2e3e5; color: #383d41; padding: 0.25rem 0.75rem;
                   border-radius: 20px; font-weight: 600; font-size: 0.85rem; }

    /* Strategy selector — card-style radio in sidebar */
    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] {
        gap: 0.35rem;
        display: flex;
        flex-direction: column;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label {
        background: rgba(255,255,255,0.06);
        border: 1.5px solid rgba(255,255,255,0.12);
        border-radius: 10px;
        padding: 0.6rem 0.85rem;
        cursor: pointer;
        transition: all 0.15s ease;
        margin: 0 !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        background: rgba(244,196,48,0.12);
        border-color: rgba(244,196,48,0.5);
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) {
        background: rgba(244,196,48,0.18);
        border: 2px solid #f4c430;
        box-shadow: 0 0 0 3px rgba(244,196,48,0.12);
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label p {
        color: rgba(255,255,255,0.88) !important;
        font-weight: 500 !important;
        font-size: 0.88rem !important;
        margin: 0 !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) p {
        color: #f4c430 !important;
        font-weight: 700 !important;
    }
    /* Hide the radio circle dot — the card border IS the selector */
    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }

    /* Divider */
    .gold-divider { margin: 1.5rem 0; border: none; border-top: 3px solid #f4c430; }

    /* Footer */
    .footer-text { text-align: center; color: #999; font-size: 0.75rem; padding: 2rem 0 1rem 0; }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# HELPER: find logo in assets/
# ============================================================================

def find_logo(folder: str = "assets", keywords=("logo", "vessel", "ship", "boat")):
    """Find the first image file in assets/ matching common logo names."""
    asset_path = Path(folder)
    if not asset_path.exists():
        return None
    for ext in ("png", "jpg", "jpeg", "svg", "webp"):
        for f in asset_path.glob(f"*.{ext}"):
            return str(f)
    return None


def signal_badge_html(val: float, label: str = "") -> str:
    """Return HTML badge for a signal value."""
    if val > 0:
        pct = int(abs(val) * 100)
        return f'<span class="signal-long">🟢 LONG {pct}%</span>'
    elif val < 0:
        pct = int(abs(val) * 100)
        return f'<span class="signal-short">🔴 SHORT {pct}%</span>'
    return '<span class="signal-flat">⚪ FLAT</span>'


# ============================================================================
# CACHE & DATA LOADING
# ============================================================================

@st.cache_resource
def load_data():
    """Load and cache data."""
    dm = DataManager(
        price_csv="data/cape_front_month.csv",
        dispersion_csv="data/dispersion_case_study.csv"
    )
    return dm


def get_signal_generator(clean_data, signal_lag, mr_threshold):
    """Create SignalGenerator with current sidebar parameters."""
    return SignalGenerator(clean_data, signal_lag=signal_lag, mr_threshold=mr_threshold)


# ============================================================================
# BRANDED HEADER
# ============================================================================

logo_file = find_logo("assets")

# ── Hero banner ──
st.markdown("""
<div style='
    background: linear-gradient(135deg, #0d1f4a 0%, #132c68 55%, #1a3a7f 100%);
    border-radius: 16px;
    padding: 2.2rem 2.4rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 4px 24px rgba(19,44,104,0.18);
    border-bottom: 4px solid #f4c430;
    display: flex;
    align-items: center;
    gap: 2rem;
'>
""", unsafe_allow_html=True)

banner_col_logo, banner_col_divider, banner_col_text = st.columns([2, 0.04, 5])

with banner_col_logo:
    if logo_file:
        st.image(logo_file, use_container_width=True)
    else:
        st.markdown(
            "<div style='font-size:7rem; text-align:center; line-height:1;'>⚓</div>",
            unsafe_allow_html=True,
        )

with banner_col_divider:
    st.markdown(
        "<div style='width:2px; background:rgba(244,196,48,0.45); height:120px; margin:auto;'></div>",
        unsafe_allow_html=True,
    )

with banner_col_text:
    st.markdown("""
    <div style='padding: 0.6rem 0 0.6rem 0.5rem;'>
        <h1 style='
            color: white;
            margin: 0 0 0.35rem 0;
            font-size: 2.6rem;
            font-weight: 700;
            letter-spacing: -0.5px;
            text-shadow: 0 2px 8px rgba(0,0,0,0.25);
        '>Freight Analytics Platform</h1>
        <p style='
            color: #5eb8e8;
            font-size: 1.1rem;
            margin: 0 0 0.6rem 0;
            font-weight: 500;
            letter-spacing: 0.2px;
        '>Capesize Dispersion Intelligence &nbsp;·&nbsp; 5TC FFA Price Prediction Engine</p>
        <div style='display:flex; gap:0.7rem; flex-wrap:wrap; margin-top:0.3rem;'>
            <span style='background:rgba(244,196,48,0.18); border:1px solid rgba(244,196,48,0.45);
                         color:#f4c430; border-radius:20px; padding:0.2rem 0.75rem;
                         font-size:0.78rem; font-weight:600;'>⚓ Capesize 5TC</span>
            <span style='background:rgba(94,184,232,0.15); border:1px solid rgba(94,184,232,0.4);
                         color:#5eb8e8; border-radius:20px; padding:0.2rem 0.75rem;
                         font-size:0.78rem; font-weight:600;'>📊 Dual-Signal Engine</span>
            <span style='background:rgba(94,184,232,0.15); border:1px solid rgba(94,184,232,0.4);
                         color:#5eb8e8; border-radius:20px; padding:0.2rem 0.75rem;
                         font-size:0.78rem; font-weight:600;'>🔬 Lead-Lag Diagnostic</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)


# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding:0.8rem 0 1rem 0; border-bottom:2px solid rgba(244,196,48,0.4);
                margin-bottom:1rem;'>
        <h2 style='color:white; margin:0; font-size:1.5rem; letter-spacing:-0.3px;'>🚢 FREIGHT ANALYTICS</h2>
        <p style='color:#5eb8e8; margin:0.4rem 0 0 0; font-size:0.82rem;'>Capesize · 5TC FFA Intelligence</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Signal parameters ──
    st.markdown("#### ⚙️ Signal Parameters")

    signal_lag = st.slider(
        "Signal Lag (days)",
        min_value=0, max_value=20, value=0, step=1,
        help="Delay signal execution by N days to test if dispersion leads prices."
    )

    mr_threshold = st.slider(
        "Mean-Reversion Threshold (σ)",
        min_value=0.5, max_value=2.5, value=1.0, step=0.25,
        help="Minimum |z-score| vs 120d mean to trigger mean-reversion signal."
    )

    st.markdown(
        "<p style='color:rgba(255,255,255,0.65); font-size:0.75rem; margin:0 0 0.4rem 0; "
        "text-transform:uppercase; letter-spacing:0.6px; font-weight:600;'>🎯 Strategy to Backtest</p>",
        unsafe_allow_html=True,
    )
    _STRATEGY_OPTIONS = [
        "📉  Inverted Momentum",
        "🔄  Mean Reversion",
        "⚖️  Compare Both",
    ]
    _STRATEGY_MAP = {
        "📉  Inverted Momentum": "Inverted Momentum",
        "🔄  Mean Reversion":    "Mean Reversion",
        "⚖️  Compare Both":      "Compare Both",
    }
    _strategy_display = st.radio(
        "Strategy to Backtest",
        options=_STRATEGY_OPTIONS,
        index=0,
        label_visibility="collapsed",
        help="Select which signal to evaluate in the Backtest tab.",
    )
    strategy_choice = _STRATEGY_MAP[_strategy_display]

    st.markdown("---")
    st.markdown("#### 💰 Backtest Settings")

    initial_capital = st.number_input(
        "Initial Capital ($)",
        min_value=100_000, max_value=10_000_000, value=1_000_000, step=100_000,
        help="Starting portfolio value."
    )

    transaction_fees_bps = st.slider(
        "Transaction Fees (bps)",
        min_value=0, max_value=50, value=10, step=1,
        help="Round-trip cost per trade in basis points."
    )

    st.markdown("---")

    # Current signal quick-view
    st.markdown("#### 📡 Live Signal")


# ============================================================================
# LOAD DATA & COMPUTE SIGNALS
# ============================================================================

dm = load_data()
clean_data = dm.get_clean_data(drop_na=True)
sg = get_signal_generator(clean_data, signal_lag, mr_threshold)
signals_df = sg.get_signals_dataframe()

# ── Sidebar live signal badges ──
with st.sidebar:
    if len(signals_df) > 0:
        latest = signals_df.iloc[-1]
        mom_val = latest.get('signal_momentum', 0)
        mr_val = latest.get('signal_mean_reversion', 0)

        st.markdown(
            f"**Momentum:** {signal_badge_html(mom_val)}<br>"
            f"**Mean Rev:** {signal_badge_html(mr_val)}<br>"
            f"<span style='font-size:0.75rem; color:rgba(255,255,255,0.6);'>"
            f"as of {latest['date'].strftime('%d %b %Y')}</span>",
            unsafe_allow_html=True
        )
    else:
        st.markdown("_No data loaded_")

    st.markdown("---")
    st.markdown(
        "<p style='color:rgba(255,255,255,0.5); font-size:0.72rem; text-align:center; line-height:1.4;'>"
        "✅ Corrected Economic Logic<br>"
        "HIGH disp → Bearish · LOW disp → Bullish<br><br>"
        "</p>",
        unsafe_allow_html=True
    )


# ============================================================================
# TABS
# ============================================================================

tab_overview, tab_signals, tab_backtest, tab_economics, tab_leadlag = st.tabs([
    "📊  Data Overview",
    "🎯  Signal Explorer",
    "🏬  Backtest Results",
    "📈  Economic Analysis",
    "🔬  Lead-Lag Analysis",
])


# ============================================================================
# TAB 1: DATA OVERVIEW
# ============================================================================

with tab_overview:
    st.header("Data Overview & Market Intelligence")

    summary = dm.get_data_summary()
    validation = dm.validate_data()

    # Key metrics in styled cards
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📅 Sample Size", f"{summary['sample_size']:,} days")
    c2.metric("🗓️ Date Range",
              f"{summary['date_start'].strftime('%b %Y')} → {summary['date_end'].strftime('%b %Y')}")
    c3.metric("💵 Avg 5TC Price", f"${summary['price_5tc']['mean']:,.0f}/day")
    c4.metric("📐 Avg Dispersion", f"{summary['avg_dispersion']['mean']:,.0f}")

    st.markdown("")  # spacer

    st.info(
        "💡 **Economic Intuition (Expert-Validated)**\n\n"
        "| Dispersion | Fleet Position | Supply | Price Impact |\n"
        "|---|---|---|---|\n"
        "| **HIGH** (rising) | Well spread globally | Efficient — cargo easily matched | **BEARISH** |\n"
        "| **LOW** (falling) | Concentrated regionally | Scarcity in key loading areas | **BULLISH** |"
    )

    # Dual-axis time series
    st.subheader("Price & Dispersion Time Series")
    fig_ts = make_subplots(specs=[[{"secondary_y": True}]])
    fig_ts.add_trace(
        go.Scatter(x=clean_data['date'], y=clean_data['price_5tc'],
                   name='5TC Price ($/day)', line=dict(color='#132c68', width=2.5)),
        secondary_y=False,
    )
    fig_ts.add_trace(
        go.Scatter(x=clean_data['date'], y=clean_data['avg_dispersion'],
                   name='Avg Dispersion', line=dict(color='#f4c430', width=2)),
        secondary_y=True,
    )
    fig_ts.update_layout(
        template="plotly_white", height=480,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0.5, xanchor="center"),
        margin=dict(l=60, r=60, t=40, b=40),
        hovermode="x unified",
    )
    fig_ts.update_yaxes(title_text="5TC Price ($/day)", secondary_y=False,
                        tickformat="$,.0f", gridcolor="#eee")
    fig_ts.update_yaxes(title_text="Avg Dispersion", secondary_y=True, gridcolor="#eee")
    st.plotly_chart(fig_ts, use_container_width=True)

    # Two-column: Correlation + Rolling
    col_corr, col_roll = st.columns(2)

    with col_corr:
        st.subheader("Correlation Matrix")
        corr_cols = ['price_5tc', 'cape_dispersion', 'vloc_dispersion', 'avg_dispersion']
        corr_matrix = clean_data[corr_cols].corr()
        fig_corr = px.imshow(
            corr_matrix, text_auto=".2f", color_continuous_scale="RdBu_r",
            zmin=-1, zmax=1,
            labels=dict(color="Correlation"),
        )
        fig_corr.update_layout(height=380, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_corr, use_container_width=True)

    with col_roll:
        st.subheader("Rolling 60-Day Correlation")
        rolling_corr = clean_data['price_5tc'].rolling(60).corr(clean_data['avg_dispersion'])
        fig_rc = go.Figure()
        fig_rc.add_trace(go.Scatter(
            x=clean_data['date'], y=rolling_corr,
            line=dict(color='#132c68', width=2), fill='tozeroy',
            fillcolor='rgba(19,44,104,0.08)', name='Rolling Corr (60d)',
        ))
        fig_rc.add_hline(y=0, line_dash="dash", line_color="#ccc")
        fig_rc.update_layout(
            yaxis_title="Correlation", template="plotly_white", height=380,
            margin=dict(l=40, r=20, t=30, b=40), hovermode="x unified",
        )
        st.plotly_chart(fig_rc, use_container_width=True)

    # Data quality
    st.subheader("Data Quality Checks")
    checks = validation.get('checks', {})
    if checks:
        quality_cols = st.columns(min(len(checks), 4))
        for idx, (check_name, check_info) in enumerate(checks.items()):
            col = quality_cols[idx % len(quality_cols)]
            is_ok = check_info.get('status') == 'ok' if isinstance(check_info, dict) else True
            icon = "✅" if is_ok else "⚠️"
            col.markdown(f"{icon} **{check_name}**")
            if isinstance(check_info, dict):
                for k, v in check_info.items():
                    if k != 'status':
                        col.caption(f"{k}: {v}")
    else:
        st.success("✅ All data quality checks passed.")


# ============================================================================
# TAB 2: SIGNAL EXPLORER
# ============================================================================

with tab_signals:
    st.header("Signal Explorer")

    st.info(
        "🎯 **Two complementary signals** generated from fleet dispersion data, "
        "both using corrected economic logic: HIGH dispersion = BEARISH, LOW dispersion = BULLISH.\n\n"
        "1. **Inverted Momentum** — trades short-term directional changes (60d window)\n"
        "2. **Mean Reversion** — fades extreme deviations from 120-day equilibrium (accordion effect)"
    )

    # ── Current signal state ──
    if len(signals_df) > 0:
        latest = signals_df.iloc[-1]
        mom_v = latest.get('signal_momentum', 0)
        mr_v = latest.get('signal_mean_reversion', 0)

        st.markdown("### 📡 Current Signal State")
        sc1, sc2, sc3, sc4 = st.columns(4)
        sc1.markdown(
            f"<div class='metric-card'><h4>Momentum Signal</h4>"
            f"<div>{signal_badge_html(mom_v)}</div>"
            f"<div class='sub'>z-score: {latest.get('momentum_zscore', 0):.2f}σ</div></div>",
            unsafe_allow_html=True
        )
        sc2.markdown(
            f"<div class='metric-card'><h4>Mean Reversion Signal</h4>"
            f"<div>{signal_badge_html(mr_v)}</div>"
            f"<div class='sub'>z-score: {latest.get('avg_disp_mr_zscore', 0):.2f}σ</div></div>",
            unsafe_allow_html=True
        )
        sc3.markdown(
            f"<div class='metric-card'><h4>5TC Price</h4>"
            f"<div class='value'>${latest['price_5tc']:,.0f}</div>"
            f"<div class='sub'>per day</div></div>",
            unsafe_allow_html=True
        )
        sc4.markdown(
            f"<div class='metric-card'><h4>Dispersion Regime</h4>"
            f"<div class='value' style='font-size:1.3rem;'>{latest.get('disp_quartile', 'N/A')}</div>"
            f"<div class='sub'>avg: {latest['avg_dispersion']:,.0f}</div></div>",
            unsafe_allow_html=True
        )

        st.markdown("")

    # Explanations in expanders
    for key in ('momentum', 'mean_reversion'):
        expl = sg.get_signal_explanation(key)
        with st.expander(f"📖 {expl.get('description', key)}", expanded=False):
            col_logic, col_econ = st.columns(2)
            with col_logic:
                st.markdown(f"**🔧 Logic**\n\n{expl.get('logic', '')}")
                st.markdown(f"**⏱️ Horizon:** {expl.get('horizon', '')}")
            with col_econ:
                st.markdown(f"**💡 Economic Meaning**\n\n{expl.get('economic_meaning', '')}")
                st.markdown(f"**📝 Rationale**\n\n{expl.get('rationale', '')}")

    # Signal overlay on price chart
    st.subheader("Signals Overlaid on Price")

    ov_col1, ov_col2, _ = st.columns([1, 1, 3])
    with ov_col1:
        show_momentum = st.checkbox("Show Inverted Momentum", value=True)
    with ov_col2:
        show_mr = st.checkbox("Show Mean Reversion", value=True)

    fig_sig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        row_heights=[0.6, 0.4], vertical_spacing=0.06,
        subplot_titles=("5TC Price ($/day)", "Signal Value (−1 to +1)")
    )

    fig_sig.add_trace(
        go.Scatter(x=signals_df['date'], y=signals_df['price_5tc'],
                   name='5TC Price', line=dict(color='#132c68', width=2.5)),
        row=1, col=1,
    )

    if show_momentum and 'signal_momentum' in signals_df.columns:
        # Color fill for long/short regions
        fig_sig.add_trace(
            go.Scatter(x=signals_df['date'], y=signals_df['signal_momentum'],
                       name='Inverted Momentum', line=dict(color='#e74c3c', width=1.5),
                       fill='tozeroy', fillcolor='rgba(231,76,60,0.1)'),
            row=2, col=1,
        )

    if show_mr and 'signal_mean_reversion' in signals_df.columns:
        fig_sig.add_trace(
            go.Scatter(x=signals_df['date'], y=signals_df['signal_mean_reversion'],
                       name='Mean Reversion', line=dict(color='#2ecc71', width=1.5),
                       fill='tozeroy', fillcolor='rgba(46,204,113,0.1)'),
            row=2, col=1,
        )

    fig_sig.add_hline(y=0, row=2, col=1, line_dash="dash", line_color="#bbb", line_width=1)
    fig_sig.add_hline(y=0.5, row=2, col=1, line_dash="dot", line_color="#ddd", line_width=0.5)
    fig_sig.add_hline(y=-0.5, row=2, col=1, line_dash="dot", line_color="#ddd", line_width=0.5)
    fig_sig.update_layout(
        template="plotly_white", height=620,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0.5, xanchor="center"),
        margin=dict(l=60, r=40, t=50, b=40), hovermode="x unified",
    )
    fig_sig.update_yaxes(tickformat="$,.0f", row=1, col=1)
    fig_sig.update_yaxes(range=[-1.15, 1.15], row=2, col=1)
    st.plotly_chart(fig_sig, use_container_width=True)

    # Signal statistics
    st.subheader("Signal Statistics")
    sig_stats = sg.get_signal_statistics()
    if sig_stats:
        for sig_name, stats in sig_stats.items():
            label = "📉 Inverted Momentum" if "momentum" in sig_name else "🔄 Mean Reversion"
            st.markdown(f"#### {label}")

            s1, s2, s3, s4, s5, s6 = st.columns(6)
            s1.metric("Long Days", f"{stats['long_signals']:,}")
            s2.metric("Short Days", f"{stats['short_signals']:,}")
            s3.metric("Flat Days", f"{stats['flat_signals']:,}")

            win_l = stats.get('win_rate_long', np.nan)
            win_s = stats.get('win_rate_short', np.nan)
            avg_ret_l = stats.get('avg_return_on_long', np.nan)

            s4.metric("Win Rate (Long)", f"{win_l:.1%}" if not np.isnan(win_l) else "N/A")
            s5.metric("Win Rate (Short)", f"{win_s:.1%}" if not np.isnan(win_s) else "N/A")
            s6.metric("Avg Return (Long)", f"{avg_ret_l:.4f}" if not np.isnan(avg_ret_l) else "N/A")

            st.markdown("---")

    # Latest signals table
    st.subheader("Latest Signals (last 20 days)")
    latest_df = sg.get_latest_signals(20)
    st.dataframe(
        latest_df.style.format({
            'price_5tc': '${:,.0f}',
            'avg_dispersion': '{:,.0f}',
            'cape_dispersion': '{:,.0f}',
            'vloc_dispersion': '{:,.0f}',
            'avg_disp_change_5d': '{:+.1f}',
            'momentum_zscore': '{:.2f}',
            'avg_disp_mr_zscore': '{:.2f}',
            'signal_momentum': '{:+.2f}',
            'signal_mean_reversion': '{:+.2f}',
            'return_5d': '{:.4f}',
        }, na_rep="—"),
        use_container_width=True,
        height=500,
    )


# ============================================================================
# TAB 3: BACKTEST RESULTS
# ============================================================================

with tab_backtest:
    st.header("Backtest Results")

    st.info(
        f"🏬 **Configuration:** {strategy_choice} · "
        f"Capital: ${initial_capital:,.0f} · Fees: {transaction_fees_bps} bps · "
        f"Lag: {signal_lag}d · MR threshold: {mr_threshold}σ"
    )

    def run_backtest(signal_col, name):
        engine = BacktestEngine(
            data_with_signals=signals_df,
            initial_capital=initial_capital,
            transaction_fee_bps=transaction_fees_bps,
        )
        results = engine.backtest_strategy(signal_col, name)
        return engine, results

    # ── Run selected strategy(ies) ──
    with st.spinner("Running backtest..."):
        if strategy_choice == "Inverted Momentum":
            engine_mom, res_mom = run_backtest('signal_momentum', 'Inverted Momentum')
            engines = [('Inverted Momentum', engine_mom, res_mom)]
        elif strategy_choice == "Mean Reversion":
            engine_mr, res_mr = run_backtest('signal_mean_reversion', 'Mean Reversion')
            engines = [('Mean Reversion', engine_mr, res_mr)]
        else:  # Compare Both
            engine_mom, res_mom = run_backtest('signal_momentum', 'Inverted Momentum')
            engine_mr, res_mr = run_backtest('signal_mean_reversion', 'Mean Reversion')
            engines = [
                ('Inverted Momentum', engine_mom, res_mom),
                ('Mean Reversion', engine_mr, res_mr),
            ]

    # ── Display results for each strategy ──
    for label, engine, results in engines:
        st.subheader(f"📌 {label}")

        # Metrics row
        m1, m2, m3, m4, m5 = st.columns(5)
        ret_color = "normal" if results['total_return_pct'] >= 0 else "inverse"
        m1.metric("Total Return", f"{results['total_return_pct']:.1%}",
                  delta=f"${results['total_pnl']:,.0f}")
        m2.metric("Annualized Return", f"{results['annualized_return_pct']:.1%}")
        m3.metric("Sharpe Ratio", f"{results['sharpe_ratio']:.2f}")
        m4.metric("Max Drawdown", f"{results['max_drawdown_pct']:.1%}")
        m5.metric("Win Rate", f"{results['win_rate']:.1%}",
                  delta=f"{results['num_trades']} trades")

        # Summary line
        pf = results.get('profit_factor', 0)
        pf_str = f"{pf:.2f}" if pf != np.inf else "∞"
        st.caption(
            f"**{results['winning_trades']}W / {results['losing_trades']}L** · "
            f"Profit Factor: {pf_str} · "
            f"Total Fees: ${results.get('total_fees_paid', 0):,.0f} · "
            f"RF Rate: {results.get('risk_free_rate', 0.02):.2%} · "
            f"Vol: {results.get('annualized_volatility', 0):.1%}"
        )

        # Equity curve
        equity_vals, equity_dates = engine.get_equity_curve()
        fig_eq = go.Figure()
        fig_eq.add_trace(go.Scatter(
            x=equity_dates, y=equity_vals,
            fill='tozeroy', fillcolor='rgba(19,44,104,0.06)',
            line=dict(color='#132c68', width=2.5),
            name='Portfolio Value',
            hovertemplate='%{x|%b %d, %Y}<br>$%{y:,.0f}<extra></extra>',
        ))
        fig_eq.add_hline(y=initial_capital, line_dash="dash", line_color="#f4c430",
                         line_width=1.5, annotation_text="Initial Capital",
                         annotation_position="bottom right",
                         annotation_font_color="#999")
        fig_eq.update_layout(
            title=f"Equity Curve — {label}",
            yaxis_title="Portfolio Value ($)", template="plotly_white", height=400,
            margin=dict(l=60, r=40, t=50, b=40), hovermode="x unified",
            yaxis_tickformat="$,.0f",
        )
        st.plotly_chart(fig_eq, use_container_width=True)

        # Trade log
        trades_df = engine.get_trade_log()
        if not trades_df.empty:
            with st.expander(f"📋 Trade Log — {label} ({len(trades_df)} trades)", expanded=False):
                styled_trades = trades_df.copy()
                st.dataframe(styled_trades, use_container_width=True, height=400)

    # ── Side-by-side comparison (when both selected) ──
    if strategy_choice == "Compare Both":
        st.markdown("<hr class='gold-divider'>", unsafe_allow_html=True)
        st.subheader("📊 Side-by-Side Comparison")

        comp_data = {
            'Metric': [
                'Total Return', 'Annualized Return', 'Sharpe Ratio',
                'Max Drawdown', 'Win Rate', 'Num Trades', 'Profit Factor',
                'Total Fees Paid', 'Ann. Volatility',
            ],
            '📉 Inverted Momentum': [
                f"{res_mom['total_return_pct']:.1%}",
                f"{res_mom['annualized_return_pct']:.1%}",
                f"{res_mom['sharpe_ratio']:.2f}",
                f"{res_mom['max_drawdown_pct']:.1%}",
                f"{res_mom['win_rate']:.1%}",
                f"{res_mom['num_trades']}",
                f"{res_mom.get('profit_factor', 0):.2f}",
                f"${res_mom.get('total_fees_paid', 0):,.0f}",
                f"{res_mom.get('annualized_volatility', 0):.1%}",
            ],
            '🔄 Mean Reversion': [
                f"{res_mr['total_return_pct']:.1%}",
                f"{res_mr['annualized_return_pct']:.1%}",
                f"{res_mr['sharpe_ratio']:.2f}",
                f"{res_mr['max_drawdown_pct']:.1%}",
                f"{res_mr['win_rate']:.1%}",
                f"{res_mr['num_trades']}",
                f"{res_mr.get('profit_factor', 0):.2f}",
                f"${res_mr.get('total_fees_paid', 0):,.0f}",
                f"{res_mr.get('annualized_volatility', 0):.1%}",
            ],
        }
        st.dataframe(pd.DataFrame(comp_data), use_container_width=True, hide_index=True)

        # Overlaid equity curves
        fig_comp = go.Figure()
        eq_mom, dt_mom = engine_mom.get_equity_curve()
        eq_mr, dt_mr = engine_mr.get_equity_curve()
        fig_comp.add_trace(go.Scatter(
            x=dt_mom, y=eq_mom, name='Inverted Momentum',
            line=dict(color='#e74c3c', width=2.5),
        ))
        fig_comp.add_trace(go.Scatter(
            x=dt_mr, y=eq_mr, name='Mean Reversion',
            line=dict(color='#2ecc71', width=2.5),
        ))
        fig_comp.add_hline(y=initial_capital, line_dash="dash", line_color="#999", line_width=1)
        fig_comp.update_layout(
            title="Equity Curves — Head to Head",
            yaxis_title="Portfolio Value ($)", template="plotly_white", height=450,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0.5, xanchor="center"),
            margin=dict(l=60, r=40, t=50, b=40), hovermode="x unified",
            yaxis_tickformat="$,.0f",
        )
        st.plotly_chart(fig_comp, use_container_width=True)

    # ── Fee sensitivity ──
    st.markdown("<hr class='gold-divider'>", unsafe_allow_html=True)
    st.subheader("Fee Sensitivity Analysis")
    st.caption("How does performance degrade as transaction costs increase?")

    fee_levels = [0, 2, 5, 10, 15, 20, 30, 50]

    if strategy_choice != "Compare Both":
        sig_col = 'signal_momentum' if strategy_choice == "Inverted Momentum" else 'signal_mean_reversion'
        with st.spinner("Computing fee sensitivity..."):
            eng_fee = BacktestEngine(signals_df, initial_capital, transaction_fees_bps)
            fee_df = eng_fee.compare_fees_sensitivity(sig_col, strategy_choice, fee_levels)
        st.dataframe(fee_df, use_container_width=True, hide_index=True)
    else:
        fc1, fc2 = st.columns(2)
        with fc1:
            st.markdown("**📉 Inverted Momentum**")
            with st.spinner("..."):
                eng1 = BacktestEngine(signals_df, initial_capital, transaction_fees_bps)
                st.dataframe(eng1.compare_fees_sensitivity('signal_momentum', 'Momentum', fee_levels),
                             use_container_width=True, hide_index=True)
        with fc2:
            st.markdown("**🔄 Mean Reversion**")
            with st.spinner("..."):
                eng2 = BacktestEngine(signals_df, initial_capital, transaction_fees_bps)
                st.dataframe(eng2.compare_fees_sensitivity('signal_mean_reversion', 'Mean Rev', fee_levels),
                             use_container_width=True, hide_index=True)

    # ── Export ──
    st.markdown("<hr class='gold-divider'>", unsafe_allow_html=True)
    st.subheader("📤 Export Results")

    exp_col1, exp_col2, exp_col3 = st.columns([2, 2, 3])
    with exp_col1:
        export_format = st.radio("Format", ["xlsx", "csv"], horizontal=True, key="export_fmt")
    with exp_col2:
        export_btn = st.button("⬇️ Export Backtest Results", use_container_width=True)

    if export_btn:
        export_dir = Path("export")
        export_dir.mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        for label, engine, _ in engines:
            safe_label = label.lower().replace(" ", "_")
            fp = str(export_dir / f"backtest_{safe_label}_lag{signal_lag}_{ts}")
            engine.export_results(fp, signal_lag=signal_lag, file_format=export_format)
        st.success("✅ Results exported to `export/` folder.")


# ============================================================================
# TAB 4: ECONOMIC ANALYSIS
# ============================================================================

with tab_economics:
    st.header("Economic Analysis")

    st.info(
        "📈 **Regime Analysis:** Days are split into dispersion quartiles to examine "
        "how 5TC prices and forward returns behave in each regime.\n\n"
        "| Quartile | Dispersion | Fleet | Expected Price Impact |\n"
        "|---|---|---|---|\n"
        "| **Q1** | Low | Concentrated | **Bullish** — scarcity |\n"
        "| **Q2** | Med-Low | Slightly concentrated | Mildly bullish |\n"
        "| **Q3** | Med-High | Slightly spread | Mildly bearish |\n"
        "| **Q4** | High | Well spread | **Bearish** — efficient supply |"
    )

    # Quartile analysis
    if 'disp_quartile' in signals_df.columns and 'return_5d' in signals_df.columns:
        regime_stats = (
            signals_df.dropna(subset=['return_5d'])
            .groupby('disp_quartile', observed=True)
            .agg(
                avg_price=('price_5tc', 'mean'),
                avg_return_5d=('return_5d', 'mean'),
                std_return_5d=('return_5d', 'std'),
                count=('price_5tc', 'size'),
            )
            .reset_index()
        )

        st.dataframe(
            regime_stats.style.format({
                'avg_price': '${:,.0f}',
                'avg_return_5d': '{:.4f}',
                'std_return_5d': '{:.4f}',
                'count': '{:,}',
            }),
            use_container_width=True,
        )

        fig_regime = px.bar(
            regime_stats, x='disp_quartile', y='avg_return_5d',
            color='disp_quartile',
            title="Average 5-Day Forward Return by Dispersion Quartile",
            labels={'avg_return_5d': 'Avg 5d Return', 'disp_quartile': 'Dispersion Quartile'},
            color_discrete_sequence=['#2ecc71', '#5eb8e8', '#f4c430', '#e74c3c'],
        )
        fig_regime.update_layout(template="plotly_white", height=400, showlegend=False,
                                 margin=dict(l=40, r=40, t=50, b=40))
        st.plotly_chart(fig_regime, use_container_width=True)

    # Distribution plots
    st.subheader("Distributions")
    dc1, dc2 = st.columns(2)
    with dc1:
        fig_d1 = px.histogram(clean_data, x='price_5tc', nbins=50,
                              title="5TC Price Distribution",
                              color_discrete_sequence=['#132c68'])
        fig_d1.update_layout(template="plotly_white", height=340,
                             xaxis_title="5TC Price ($/day)", yaxis_title="Frequency",
                             margin=dict(l=40, r=20, t=50, b=40))
        st.plotly_chart(fig_d1, use_container_width=True)
    with dc2:
        fig_d2 = px.histogram(clean_data, x='avg_dispersion', nbins=50,
                              title="Avg Dispersion Distribution",
                              color_discrete_sequence=['#f4c430'])
        fig_d2.update_layout(template="plotly_white", height=340,
                             xaxis_title="Avg Dispersion", yaxis_title="Frequency",
                             margin=dict(l=40, r=20, t=50, b=40))
        st.plotly_chart(fig_d2, use_container_width=True)

    # Granger causality
    st.subheader("Granger Causality Test")
    st.info(
        "🔍 Tests whether **past dispersion** values help predict **future 5TC prices** "
        "(beyond what past prices alone predict). Significant p-values (< 0.05) suggest predictive power."
    )
    try:
        from statsmodels.tsa.stattools import grangercausalitytests

        gc_data = clean_data[['price_5tc', 'avg_dispersion']].dropna()
        max_gc_lag = st.slider("Max Granger Lag", 1, 20, 10, key="gc_lag")

        with st.spinner("Running Granger causality tests..."):
            gc_results = grangercausalitytests(gc_data, maxlag=max_gc_lag, verbose=False)

        gc_rows = []
        for lag, result in gc_results.items():
            f_test = result[0]['ssr_ftest']
            gc_rows.append({
                'Lag (days)': lag,
                'F-statistic': f"{f_test[0]:.3f}",
                'p-value': f"{f_test[1]:.4f}",
                'Significant (5%)': "✅ Yes" if f_test[1] < 0.05 else "❌ No",
            })
        st.dataframe(pd.DataFrame(gc_rows), use_container_width=True, hide_index=True)

        # Quick interpretation
        sig_lags = [r['Lag (days)'] for r in gc_rows if "✅" in r['Significant (5%)']]
        if sig_lags:
            st.success(f"📊 Dispersion has significant predictive power at lag(s): **{sig_lags}** days.")
        else:
            st.warning("⚠️ No significant Granger causality found at any tested lag.")

    except ImportError:
        st.warning("Install `statsmodels` for Granger causality tests: `pip install statsmodels`")
    except Exception as e:
        st.error(f"Granger test error: {e}")


# ============================================================================
# TAB 5: LEAD-LAG ANALYSIS (CHANGE 3)
# ============================================================================

with tab_leadlag:
    st.header("🔬 Lead-Lag Cross-Correlation Analysis")

    st.info(
        "**Purpose:** Determine whether dispersion **leads** or **lags** 5TC price movements.\n\n"
        "| Lag | Meaning | Trading Implication |\n"
        "|---|---|---|\n"
        "| **Positive (+k)** | Dispersion at *t* → Price at *t+k* | Dispersion **predicts** prices ✅ |\n"
        "| **Zero (0)** | Contemporaneous | No predictive edge |\n"
        "| **Negative (−k)** | Price at *t* → Dispersion at *t+k* | Signal is **late** ⚠️ |\n\n"
        "If the peak |correlation| is at a positive lag, dispersion is a **leading indicator**."
    )

    # User toggles
    ll_col1, ll_col2, ll_col3 = st.columns([2, 2, 1])
    with ll_col1:
        series_x_choice = st.selectbox(
            "Dispersion Series (X)",
            options=['avg_dispersion', 'avg_disp_change_5d'],
            index=0,
            format_func=lambda x: "Avg Dispersion (level)" if x == 'avg_dispersion' else "5-Day Change (Δ)",
            help="Choose raw dispersion level or 5-day change."
        )
    with ll_col2:
        series_y_choice = st.selectbox(
            "Price Series (Y)",
            options=['price_5tc', 'return_5d'],
            index=0,
            format_func=lambda x: "5TC Price (level)" if x == 'price_5tc' else "5-Day Return (%)",
            help="Choose raw price or 5-day return."
        )
    with ll_col3:
        max_lag_input = st.number_input("Max Lag (days)", min_value=5, max_value=40, value=20,
                                        step=5, key="ll_max_lag")

    # Compute cross-correlation
    try:
        cc_df = sg.compute_lead_lag_crosscorr(
            series_x=series_x_choice,
            series_y=series_y_choice,
            max_lag=max_lag_input,
        )

        # Find peak absolute correlation
        peak_idx = cc_df['correlation'].abs().idxmax()
        peak_lag = int(cc_df.loc[peak_idx, 'lag'])
        peak_corr = cc_df.loc[peak_idx, 'correlation']

        # Interpretation with colored callout
        if peak_lag > 0:
            st.success(
                f"📈 **Peak |correlation| at lag +{peak_lag} days (r = {peak_corr:.3f}):** "
                f"Dispersion **LEADS** price by ~{peak_lag} days. "
                f"This supports using dispersion as a **predictive** indicator for trading."
            )
        elif peak_lag < 0:
            st.warning(
                f"📉 **Peak |correlation| at lag {peak_lag} days (r = {peak_corr:.3f}):** "
                f"Dispersion **LAGS** price by ~{abs(peak_lag)} days. "
                f"The momentum signal may be **reacting late** to price moves. "
                f"Consider using a different lag parameter."
            )
        else:
            st.info(
                f"⚖️ **Peak |correlation| at lag 0 (r = {peak_corr:.3f}):** "
                f"Relationship is **contemporaneous** — no lead/lag advantage. "
                f"The signal has no predictive edge at this combination."
            )

        # Bar chart with improved styling
        colors = []
        for i, row in cc_df.iterrows():
            if i == peak_idx:
                colors.append('#f4c430')  # Gold for peak
            elif row['correlation'] > 0:
                colors.append('#132c68')  # Navy for positive
            else:
                colors.append('#5eb8e8')  # Teal for negative

        fig_ll = go.Figure()
        fig_ll.add_trace(go.Bar(
            x=cc_df['lag'], y=cc_df['correlation'],
            marker_color=colors,
            name='Cross-Correlation',
            hovertemplate='Lag: %{x} days<br>Correlation: %{y:.4f}<extra></extra>',
        ))
        fig_ll.add_vline(x=0, line_dash="dash", line_color="#e74c3c", line_width=2,
                         annotation_text="Lag = 0", annotation_position="top right",
                         annotation_font=dict(size=11, color="#e74c3c"))
        fig_ll.add_vline(x=peak_lag, line_dash="dot", line_color="#f4c430", line_width=2.5,
                         annotation_text=f"Peak: lag={peak_lag} (r={peak_corr:.3f})",
                         annotation_position="top left",
                         annotation_font=dict(size=11, color="#b8860b"))

        x_label = "Avg Dispersion (level)" if series_x_choice == 'avg_dispersion' else "5-Day Δ Dispersion"
        y_label = "5TC Price (level)" if series_y_choice == 'price_5tc' else "5-Day Return"

        fig_ll.update_layout(
            title=f"Lead-Lag Cross-Correlation: {x_label} → {y_label}",
            xaxis_title="Lag (days) — positive = dispersion leads price",
            yaxis_title="Pearson Correlation Coefficient",
            template="plotly_white", height=480,
            margin=dict(l=60, r=40, t=60, b=50),
            xaxis=dict(dtick=5, gridcolor="#eee"),
            yaxis=dict(gridcolor="#eee"),
        )
        st.plotly_chart(fig_ll, use_container_width=True)

        # Raw data in compact expander
        with st.expander("📋 Raw Cross-Correlation Data"):
            display_cc = cc_df[['lag', 'correlation']].copy()
            display_cc['abs_correlation'] = display_cc['correlation'].abs()
            display_cc = display_cc.sort_values('abs_correlation', ascending=False)
            st.dataframe(
                display_cc.style.format({'correlation': '{:.4f}', 'abs_correlation': '{:.4f}'}),
                use_container_width=True, hide_index=True, height=400,
            )

    except Exception as e:
        st.error(f"Error computing cross-correlation: {e}")


# ============================================================================
# FOOTER
# ============================================================================

st.markdown("<hr class='gold-divider'>", unsafe_allow_html=True)
st.markdown(
    "<p class='footer-text'>"
    "⚓ Freight Analytics Platform · Capesize Dispersion Intelligence<br>"
    "</p>",
    unsafe_allow_html=True
)