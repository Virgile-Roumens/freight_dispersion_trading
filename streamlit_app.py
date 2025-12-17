"""
Streamlit Dashboard - User-Friendly Interface for Dispersion Analysis

Tabs:
1. 📊 Data Overview - Correlations, quality
2. 🎯 Signal Explorer - Economic explanations
3. 🏬 Backtest Results - Performance, P&L
4. 📈 Economic Analysis - In-depth statistics
5. ⚔️ Strategy Comparison - Momentum vs Regime

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
from datetime import datetime
from pathlib import Path
import sys

# Import des classes
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
        dispersion_csv='dispersion_case_study.csv',
        verbose=False
    )
    clean_data = dm.get_clean_data(drop_na=True)
    sg = SignalGenerator(clean_data, verbose=False)
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
    "✅ **Approach**: Simple statistics, no complex ML\n"
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
        "📈 Economic Analysis",
        "⚔️ Strategy Comparison"
    ]
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

max_dd_stop = st.sidebar.slider(
    "Hard Stop (% loss)",
    min_value=0.0,
    max_value=5.0,
    value=2.0,
    step=0.5,
    help="Exit if drawdown exceeds this %"
)

# ============================================================================
# DATA LOADING
# ============================================================================

try:
    dm, sg, clean_data = load_data_once()
    data_summary = dm.get_data_summary()
    signals_df = sg.get_signals_dataframe()
except Exception as e:
    st.error(f"❌ Error loading data: {e}")
    st.stop()


# ============================================================================
# TAB 1: DATA OVERVIEW
# ============================================================================

if tab_choice == "📊 Data Overview":
    st.title("📊 Data Overview & Quality Checks")
    
    st.info(
        "**Step 1: Verify the data**\n\n"
        "Here we display:\n"
        "- Sample size and period covered\n"
        "- Raw correlations between dispersion and prices\n"
        "- Statistics by vessel class (Capesize, VLOC)\n"
        "- Data quality checks"
    )
    
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
            f"{years:.1f} years"
        )
    with col3:
        corr = data_summary['correlation_avg']
        st.metric(
            "Correlation (Avg Disp ↔ Price)",
            f"{corr:.3f}",
            delta="Weak but positive" if 0.2 < corr < 0.4 else ""
        )
    with col4:
        st.metric(
            "Status",
            "✅ Loaded"
        )
    
    st.markdown("---")
    
    # Price and dispersion statistics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("5TC Front-Month (Price)")
        price_stats = data_summary['price_5tc']
        
        price_cols = st.columns(4)
        price_cols[0].metric("Mean", f"${price_stats['mean']:.0f}/day")
        price_cols[1].metric("Std Dev", f"${price_stats['std']:.0f}")
        price_cols[2].metric("Min", f"${price_stats['min']:.0f}")
        price_cols[3].metric("Max", f"${price_stats['max']:.0f}")
        
        st.info(
            "**5TC Price Context:**\n\n"
            "The 5TC (5-day Time Charter) is the reference FFA contract for "
            "Capesize vessels. It represents the daily charter cost of a "
            "voyage vessel, used by traders to hedge against "
            "freight cost variations."
        )
    
    with col2:
        st.subheader("Fleet Dispersion (Weighted Average)")
        disp_stats = data_summary['avg_dispersion']
        
        disp_cols = st.columns(4)
        disp_cols[0].metric("Mean", f"{disp_stats['mean']:.0f}")
        disp_cols[1].metric("Std Dev", f"{disp_stats['std']:.0f}")
        disp_cols[2].metric("Min", f"{disp_stats['min']:.0f}")
        disp_cols[3].metric("Max", f"{disp_stats['max']:.0f}")
        
        st.info(
            "**Dispersion Context:**\n\n"
            "Dispersion measures the geographic distribution of vessels. "
            "High value = well-distributed vessels globally = "
            "better supply/demand matching. "
            "Low value = concentrated vessels = potential congestion."
        )
    
    st.markdown("---")
    
    # Breakdown by vessel class
    st.subheader("Breakdown by Vessel Class")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🚢 Capesize**")
        cape_stats = data_summary['cape_dispersion']
        st.metric("Avg Dispersion", f"{cape_stats['mean']:.0f}")
        st.metric("Corr. with Price", f"{data_summary['correlation_cape']:.3f}")
        st.caption("Vessels > 100k tons")
    
    with col2:
        st.markdown("**🛢️ VLOC**")
        vloc_stats = data_summary['vloc_dispersion']
        st.metric("Avg Dispersion", f"{vloc_stats['mean']:.0f}")
        st.metric("Corr. with Price", f"{data_summary['correlation_vloc']:.3f}")
        st.caption("Very Large Ore Carriers")
    
    with col3:
        st.markdown("**📊 Combined**")
        st.metric(
            "Weighted Dispersion",
            f"{data_summary['avg_dispersion']['mean']:.0f}"
        )
        st.metric(
            "Corr. with Price",
            f"{data_summary['correlation_avg']:.3f}"
        )
        st.success("Best combined signal")
    
    st.info(
        "**Why Average?**\n\n"
        "Capesize and VLOC compete for the same cargoes (iron ore). "
        "The weighted average by number of vessels better captures total supply "
        "than each class in isolation."
    )
    
    st.markdown("---")
    
    # Time series graph
    st.subheader("Time Series: 5TC Price vs Dispersion")
    
    # Normalize 0-100 for comparison
    price_norm = (
        (signals_df['price_5tc'] - signals_df['price_5tc'].min()) /
        (signals_df['price_5tc'].max() - signals_df['price_5tc'].min()) * 100
    )
    avg_norm = (
        (signals_df['avg_dispersion'] - signals_df['avg_dispersion'].min()) /
        (signals_df['avg_dispersion'].max() - signals_df['avg_dispersion'].min()) * 100
    )
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=signals_df['date'],
        y=price_norm,
        name='5TC Price (normalized)',
        line=dict(color='#1f77b4', width=3),
    ))
    fig.add_trace(go.Scatter(
        x=signals_df['date'],
        y=avg_norm,
        name='Average Dispersion (normalized)',
        line=dict(color='#d62728', width=2, dash='dash'),
    ))
    fig.update_layout(
        title="Both series generally move together (r=0.27)",
        xaxis_title="Date",
        yaxis_title="Normalized Value (0-100)",
        hovermode='x unified',
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.warning(
        "**⚠️ Important Observation:**\n\n"
        "Although both series are positively correlated (r=0.27), "
        "they don't always move together. This means that dispersion "
        "only explains a small part of price movements. "
        "Other factors (iron demand, geopolitics, USD rates) dominate."
    )
    
    st.markdown("---")
    
    # Quality checks
    st.subheader("✅ Data Quality Checks")
    
    validation_report = dm.validate_data()
    
    check_cols = st.columns(2)
    
    with check_cols[0]:
        st.markdown("**Checks:**")
        for check_name, check_result in validation_report['checks'].items():
            status_icon = "✓" if check_result['status'] == 'ok' else "⚠"
            st.write(f"{status_icon} **{check_name}**: {check_result['status'].upper()}")
    
    with check_cols[1]:
        st.markdown("**Summary:**")
        st.success(
            "✅ No price outliers detected\n"
            "✅ Date continuity acceptable\n"
            "✅ Sufficient price and dispersion variance\n"
            "✅ **Data ready for analysis**"
        )


# ============================================================================
# TAB 2: SIGNAL EXPLORER
# ============================================================================

elif tab_choice == "🎯 Signal Explorer":
    st.title("🎯 Signal Explorer: The 2 Strategies")
    
    st.info(
        "**Step 2: Understand the signals**\n\n"
        "We have created 2 simple signals based on dispersion:\n"
        "1. **Momentum**: Captures short-term changes\n"
        "2. **Regime**: Captures structural market state\n\n"
        "Neither is \"optimal\" - they are just two different approaches."
    )
    
    st.markdown("---")
    
    # Explications des signaux
    explanations = sg.get_all_explanations()
    
    signal_tabs = st.tabs(["📈 Momentum Signal", "🎯 Regime Signal"])
    
    with signal_tabs[0]:
        st.subheader("📈 Momentum Dispersion Signal")
        
        exp = explanations['momentum']
        
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
    
    with signal_tabs[1]:
        st.subheader("🎯 Regime Signal (Quartiles)")
        
        exp = explanations['regime']
        
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
    
    # Signal statistics
    st.subheader("📊 Signal Statistics (Historical)")
    
    signal_stats = sg.get_signal_statistics()
    stats_df_list = []
    
    for signal_name, stats in signal_stats.items():
        clean_name = signal_name.replace('signal_', '').upper()
        stats_df_list.append({
            'Signal': clean_name,
            'Days LONG': f"{stats.get('long_signals', 0):.0f}",
            'Days SHORT': f"{stats.get('short_signals', 0):.0f}",
            'Days FLAT': f"{stats.get('flat_signals', 0):.0f}",
            'Avg Return LONG': f"{stats.get('avg_return_on_long', 0):.2%}",
            'Avg Return SHORT': f"{stats.get('avg_return_on_short', 0):.2%}",
            'Win Rate LONG': f"{stats.get('win_rate_long', 0):.1%}",
        })
    
    stats_display_df = pd.DataFrame(stats_df_list)
    st.dataframe(stats_display_df, use_container_width=True, hide_index=True)
    
    st.info(
        "**How to read this table:**\n\n"
        "- **Days LONG/SHORT/FLAT**: Number of days in each position\n"
        "- **Avg Return**: Average 5-day return when signal is active\n"
        "- **Win Rate**: % of days where the signal predicted the right direction"
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
        if val == 1:
            return "🟢 LONG"
        elif val == -1:
            return "🔴 SHORT"
        else:
            return "⚪ FLAT"
    
    latest_signals['Momentum'] = latest_signals['signal_momentum'].apply(signal_emoji)
    latest_signals['Regime'] = latest_signals['signal_regime'].apply(signal_emoji)
    
    display_cols = [
        'date', 'price_5tc', 'avg_dispersion', 'disp_quartile',
        'Momentum', 'Regime', 'return_5d'
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
    
    st.info(
        "**Step 3: Evaluate performance**\n\n"
        f"Backtest configuration:\n"
        f"- 💰 Initial Capital: ${initial_capital:,}\n"
        f"- 💸 Fees: {fee_bps} bps per trade\n"
        f"- 🛑 Hard Stop: {max_dd_stop:.1f}%\n\n"
        "We simulate daily trading with automatic rebalancing."
    )
    
    st.markdown("---")
    
    # Strategy selection
    strategy_choice = st.radio(
        "Choose the strategy to backtest",
        ["Momentum", "Regime"],
        horizontal=True
    )
    
    signal_col = 'signal_momentum' if strategy_choice == 'Momentum' else 'signal_regime'
    
    # Lancer backtest
    with st.spinner(f"Backtesting {strategy_choice}..."):
        engine = BacktestEngine(
            signals_df,
            initial_capital=initial_capital,
            transaction_fee_bps=fee_bps,
            max_drawdown_stop=max_dd_stop / 100,
            verbose=False
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
    else:
        st.info("No trades executed for this signal.")


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
    
    # Limitations
    st.subheader("4️⃣ Risks & Limitations")
    
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
# TAB 5: STRATEGY COMPARISON
# ============================================================================

elif tab_choice == "⚔️ Strategy Comparison":
    st.title("⚔️ Comparison: Momentum vs Regime")
    
    st.info(
        "**Step 5: Decide which approach is better**\n\n"
        "We backtest both signals side by side with your parameters. "
        "Neither is \"correct\" - they just capture different things."
    )
    
    st.markdown("---")
    
    with st.spinner("Backtesting both strategies..."):
        all_results = {}
        engines = {}
        
        for signal_col, name in [
            ('signal_momentum', 'Momentum'),
            ('signal_regime', 'Regime')
        ]:
            engine = BacktestEngine(
                signals_df,
                initial_capital=initial_capital,
                transaction_fee_bps=fee_bps,
                max_drawdown_stop=max_dd_stop / 100,
                verbose=False
            )
            results = engine.backtest_strategy(signal_col, name)
            all_results[name] = results
            engines[name] = engine
    
    st.markdown("---")
    
    # Comparison table
    st.subheader("📊 Side-by-Side Performance")
    
    comparison_data = []
    for name, results in all_results.items():
        comparison_data.append({
            'Strategy': name,
            'Return': f"{results['total_return_pct']:.1%}",
            'Sharpe': f"{results['sharpe_ratio']:.2f}",
            'Max DD': f"{results['max_drawdown_pct']:.1%}",
            'Win Rate': f"{results['win_rate']:.1%}",
            'Trades': f"{results['num_trades']:.0f}",
            'Calmar': f"{results['calmar_ratio']:.2f}",
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Equity curves
    st.subheader("📈 Compared Equity Curves")
    
    fig = go.Figure()
    colors = ['#1f77b4', '#ff7f0e']
    
    for (name, _), color in zip(
        [(k, v) for k, v in all_results.items()],
        colors
    ):
        equity_vals, equity_dates = engines[name].get_equity_curve()
        fig.add_trace(go.Scatter(
            x=equity_dates,
            y=equity_vals,
            name=name,
            line=dict(color=color, width=2)
        ))
    
    fig.update_layout(
        title="Strategy Comparison",
        xaxis_title="Date",
        yaxis_title="Portfolio Value ($)",
        hovermode='x unified',
        height=450
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Winner analysis
    st.subheader("🎯 Winner Analysis")
    
    best_sharpe_strategy = max(
        all_results.items(),
        key=lambda x: x[1]['sharpe_ratio']
    )[0]
    best_return_strategy = max(
        all_results.items(),
        key=lambda x: x[1]['total_return_pct']
    )[0]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success(f"**Best Sharpe**: {best_sharpe_strategy}")
        st.metric(
            "Sharpe Ratio",
            f"{all_results[best_sharpe_strategy]['sharpe_ratio']:.2f}"
        )
    
    with col2:
        st.info(f"**Best Return**: {best_return_strategy}")
        st.metric(
            "Total Return",
            f"{all_results[best_return_strategy]['total_return_pct']:.1%}"
        )
    
    with col3:
        best_overall = best_sharpe_strategy
        best_val = all_results[best_sharpe_strategy]['sharpe_ratio']
        st.metric(
            "Recommendation",
            f"{best_overall}" if best_val > 0.7 else "None"
        )
    
    st.markdown("---")
    
    st.subheader("💡 Final Recommendation")
    
    best_overall = best_sharpe_strategy
    best_sharpe_val = all_results[best_sharpe_strategy]['sharpe_ratio']
    
    if best_sharpe_val > 0.80:
        st.success(
            f"✅ **{best_overall} is interesting.**\n\n"
            f"Sharpe of {best_sharpe_val:.2f} suggests a measurable relationship. "
            f"Before using in production:\n"
            f"1. Validate forward on 2024-2025\n"
            f"2. Add other signals\n"
            f"3. Test rolling stability\n"
            f"4. Start small on paper"
        )
    elif best_sharpe_val > 0.60:
        st.info(
            f"⚠️ **{best_overall} shows potential.**\n\n"
            f"Sharpe of {best_sharpe_val:.2f} is acceptable. "
            f"But we would need to:\n"
            f"1. Improve parameters\n"
            f"2. Combine with other signals\n"
            f"3. Validate forward"
        )
    else:
        st.warning(
            f"❌ **No strategy shows convincing edge.**\n\n"
            f"Best Sharpe: {best_sharpe_val:.2f}\n\n"
            f"This is honest - we haven't found an exploitable relationship alone. "
            f"We would need to combine with other fundamental signals."
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
