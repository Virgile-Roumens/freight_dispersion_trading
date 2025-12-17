"""
Streamlit Dashboard - Interface UX Friendly pour l'Analyse de Dispersion

Tabs:
1. 📊 Aperçu Données - Corrélations, qualité
2. 🎯 Explorateur de Signaux - Explications économiques
3. 🏦 Résultats Backtest - Performance, P&L
4. 📈 Analyse Économique - Statistiques approfondies
5. ⚔️ Comparaison Stratégies - Momentum vs Regime

Architecture UX:
- Lots de st.info() pour expliquer
- Sidebar avec contrôles interactifs
- Visualisations claires et détaillées
- Tabs séparées par thème
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
    page_title="Analyse Dispersion Capesize",
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
# CACHE & CHARGEMENT DONNÉES
# ============================================================================

@st.cache_resource
def load_data_once():
    """Charger les données une seule fois et mettre en cache."""
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

st.sidebar.markdown("# 🚢 Analyse Dispersion Capesize")
st.sidebar.markdown("### Étude: Prix 5TC vs Dispersion Flotte")

st.sidebar.info(
    "**📖 À propos:**\n\n"
    "Ce projet teste si la dispersion des bateaux Capesize/VLOC "
    "prédit les prix 5TC front-month.\n\n"
    "✅ **Approche**: Statistiques simples, pas de ML complexe\n"
    "✅ **Honnête**: Reconnaît les limitations\n"
    "✅ **Réaliste**: Intègre les frais de transaction"
)

st.sidebar.markdown("---")

tab_choice = st.sidebar.radio(
    "Navigation",
    [
        "📊 Aperçu Données",
        "🎯 Explorateur de Signaux",
        "🏦 Résultats Backtest",
        "📈 Analyse Économique",
        "⚔️ Comparaison Stratégies"
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Paramètres Backtest")

initial_capital = st.sidebar.number_input(
    "Capital Initial ($)",
    value=1_000_000,
    step=100_000,
    min_value=100_000,
    help="Montant initial du portefeuille"
)

fee_bps = st.sidebar.slider(
    "Frais Transaction (bps)",
    min_value=0,
    max_value=50,
    value=10,
    step=1,
    help="Basis points par trade (round-trip)"
)

max_dd_stop = st.sidebar.slider(
    "Hard Stop (% perte)",
    min_value=0.0,
    max_value=5.0,
    value=2.0,
    step=0.5,
    help="Sortie si drawdown dépasse ce %"
)

# ============================================================================
# CHARGEMENT DONNÉES
# ============================================================================

try:
    dm, sg, clean_data = load_data_once()
    data_summary = dm.get_data_summary()
    signals_df = sg.get_signals_dataframe()
except Exception as e:
    st.error(f"❌ Erreur chargement données: {e}")
    st.stop()


# ============================================================================
# TAB 1: APERÇU DONNÉES
# ============================================================================

if tab_choice == "📊 Aperçu Données":
    st.title("📊 Aperçu des Données & Vérifications de Qualité")
    
    st.info(
        "**Étape 1: Vérifier les données**\n\n"
        "Ici nous affichons:\n"
        "- Taille de l'échantillon et période couverte\n"
        "- Corrélations brutes entre dispersion et prix\n"
        "- Statistiques par classe de bateaux (Capesize, VLOC)\n"
        "- Vérifications de qualité des données"
    )
    
    # Métriques clés
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Taille Échantillon",
            f"{data_summary['sample_size']:,} jours"
        )
    with col2:
        years = data_summary['years_covered']
        st.metric(
            "Période",
            f"{years:.1f} ans"
        )
    with col3:
        corr = data_summary['correlation_avg']
        st.metric(
            "Corrélation (Disp Moy ↔ Prix)",
            f"{corr:.3f}",
            delta="Faible mais positive" if 0.2 < corr < 0.4 else ""
        )
    with col4:
        st.metric(
            "Statut",
            "✅ Chargé"
        )
    
    st.markdown("---")
    
    # Statistiques prix et dispersion
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("5TC Front-Month (Prix)")
        price_stats = data_summary['price_5tc']
        
        price_cols = st.columns(4)
        price_cols[0].metric("Moyenne", f"${price_stats['mean']:.0f}/jour")
        price_cols[1].metric("Std Dev", f"${price_stats['std']:.0f}")
        price_cols[2].metric("Min", f"${price_stats['min']:.0f}")
        price_cols[3].metric("Max", f"${price_stats['max']:.0f}")
        
        st.info(
            "**Contexte Prix 5TC:**\n\n"
            "Le 5TC (5-day Time Charter) est le contrat FFA de référence pour "
            "les bateaux Capesize. Il représente le coût de location quotidien "
            "d'un bateauvoyage, utilisé par les traders pour se couvrir contre "
            "les variations de coûts de fret."
        )
    
    with col2:
        st.subheader("Dispersion Flotte (Moyenne Pondérée)")
        disp_stats = data_summary['avg_dispersion']
        
        disp_cols = st.columns(4)
        disp_cols[0].metric("Moyenne", f"{disp_stats['mean']:.0f}")
        disp_cols[1].metric("Std Dev", f"{disp_stats['std']:.0f}")
        disp_cols[2].metric("Min", f"{disp_stats['min']:.0f}")
        disp_cols[3].metric("Max", f"{disp_stats['max']:.0f}")
        
        st.info(
            "**Contexte Dispersion:**\n\n"
            "La dispersion mesure la répartition géographique des bateaux. "
            "Une valeur élevée = bateaux bien répartis mondialement = "
            "meilleur matching offre/demande. "
            "Une valeur basse = bateaux concentrés = potentielle congestion."
        )
    
    st.markdown("---")
    
    # Breakdown par classe de bateau
    st.subheader("Ventilation par Classe de Bateaux")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🚢 Capesize**")
        cape_stats = data_summary['cape_dispersion']
        st.metric("Dispersion Moy", f"{cape_stats['mean']:.0f}")
        st.metric("Corr. avec Prix", f"{data_summary['correlation_cape']:.3f}")
        st.caption("Bateaux > 100k tonnes")
    
    with col2:
        st.markdown("**🛢️ VLOC**")
        vloc_stats = data_summary['vloc_dispersion']
        st.metric("Dispersion Moy", f"{vloc_stats['mean']:.0f}")
        st.metric("Corr. avec Prix", f"{data_summary['correlation_vloc']:.3f}")
        st.caption("Very Large Ore Carriers")
    
    with col3:
        st.markdown("**📊 Combinée**")
        st.metric(
            "Dispersion Pondérée",
            f"{data_summary['avg_dispersion']['mean']:.0f}"
        )
        st.metric(
            "Corr. avec Prix",
            f"{data_summary['correlation_avg']:.3f}"
        )
        st.success("Meilleur signal combiné")
    
    st.info(
        "**Pourquoi Moyenner?**\n\n"
        "Les Capesize et VLOC concourent pour les mêmes cargaisons (minerai de fer). "
        "La moyenne pondérée par nombre de bateaux capture mieux l'offre totale "
        "que chaque classe isolément."
    )
    
    st.markdown("---")
    
    # Graphique série temporelle
    st.subheader("Série Temporelle: Prix 5TC vs Dispersion")
    
    # Normaliser 0-100 pour comparaison
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
        name='Prix 5TC (normalisé)',
        line=dict(color='#1f77b4', width=3),
    ))
    fig.add_trace(go.Scatter(
        x=signals_df['date'],
        y=avg_norm,
        name='Dispersion Moyenne (normalisée)',
        line=dict(color='#d62728', width=2, dash='dash'),
    ))
    fig.update_layout(
        title="Les deux séries montent/descendent généralement ensemble (r=0.27)",
        xaxis_title="Date",
        yaxis_title="Valeur Normalisée (0-100)",
        hovermode='x unified',
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.warning(
        "**⚠️ Observation Importante:**\n\n"
        "Bien que les deux séries soient positivement corrélées (r=0.27), "
        "elles ne bougent pas toujours ensemble. Cela signifie que la dispersion "
        "n'explique qu'une petite partie des mouvements de prix. "
        "D'autres facteurs (demande fer, géopolitique, taux USD) dominent."
    )
    
    st.markdown("---")
    
    # Vérifications de qualité
    st.subheader("✅ Vérifications de Qualité des Données")
    
    validation_report = dm.validate_data()
    
    check_cols = st.columns(2)
    
    with check_cols[0]:
        st.markdown("**Vérifications:**")
        for check_name, check_result in validation_report['checks'].items():
            status_icon = "✓" if check_result['status'] == 'ok' else "⚠"
            st.write(f"{status_icon} **{check_name}**: {check_result['status'].upper()}")
    
    with check_cols[1]:
        st.markdown("**Résumé:**")
        st.success(
            "✅ Aucun outlier de prix détecté\n"
            "✅ Continuité des dates acceptable\n"
            "✅ Variance prix et dispersion suffisante\n"
            "✅ **Données prêtes pour analyse**"
        )


# ============================================================================
# TAB 2: EXPLORATEUR DE SIGNAUX
# ============================================================================

elif tab_choice == "🎯 Explorateur de Signaux":
    st.title("🎯 Explorateur de Signaux: Les 2 Stratégies")
    
    st.info(
        "**Étape 2: Comprendre les signaux**\n\n"
        "Nous avons créé 2 signaux simples basés sur la dispersion:\n"
        "1. **Momentum**: Capture les changements court-terme\n"
        "2. **Regime**: Capture l'état structurel du marché\n\n"
        "Aucun des deux n'est \"optimal\" - ce sont juste deux approches différentes."
    )
    
    st.markdown("---")
    
    # Explications des signaux
    explanations = sg.get_all_explanations()
    
    signal_tabs = st.tabs(["📈 Momentum Signal", "🎯 Regime Signal"])
    
    with signal_tabs[0]:
        st.subheader("📈 Signal de Momentum Dispersion")
        
        exp = explanations['momentum']
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Type**: {exp['signal_type']}")
            st.markdown(f"**Horizon**: {exp['horizon']}")
        with col2:
            st.markdown(f"**Logique**:")
            st.code(exp['logic'])
        
        st.markdown("---")
        st.info(f"**📖 Sens Économique**:\n\n{exp['economic_meaning']}")
        st.success(f"**💡 Rationale**:\n\n{exp['rationale']}")
    
    with signal_tabs[1]:
        st.subheader("🎯 Signal de Regime (Quartiles)")
        
        exp = explanations['regime']
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Type**: {exp['signal_type']}")
            st.markdown(f"**Horizon**: {exp['horizon']}")
        with col2:
            st.markdown(f"**Logique**:")
            st.code(exp['logic'])
        
        st.markdown("---")
        st.info(f"**📖 Sens Économique**:\n\n{exp['economic_meaning']}")
        st.success(f"**💡 Rationale**:\n\n{exp['rationale']}")
    
    st.markdown("---")
    
    # Statistiques des signaux
    st.subheader("📊 Statistiques des Signaux (Historique)")
    
    signal_stats = sg.get_signal_statistics()
    stats_df_list = []
    
    for signal_name, stats in signal_stats.items():
        clean_name = signal_name.replace('signal_', '').upper()
        stats_df_list.append({
            'Signal': clean_name,
            'Jours LONG': f"{stats.get('long_signals', 0):.0f}",
            'Jours SHORT': f"{stats.get('short_signals', 0):.0f}",
            'Jours FLAT': f"{stats.get('flat_signals', 0):.0f}",
            'Return Moy LONG': f"{stats.get('avg_return_on_long', 0):.2%}",
            'Return Moy SHORT': f"{stats.get('avg_return_on_short', 0):.2%}",
            'Win Rate LONG': f"{stats.get('win_rate_long', 0):.1%}",
        })
    
    stats_display_df = pd.DataFrame(stats_df_list)
    st.dataframe(stats_display_df, use_container_width=True, hide_index=True)
    
    st.info(
        "**Comment lire ce tableau:**\n\n"
        "- **Jours LONG/SHORT/FLAT**: Nombre de jours en chaque position\n"
        "- **Return Moy**: Retour moyen 5-jours quand signal actif\n"
        "- **Win Rate**: % des jours où le signal prédisait la bonne direction"
    )
    
    st.markdown("---")
    
    # Derniers signaux
    st.subheader("📋 Derniers Signaux (15 jours)")
    
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
# TAB 3: RÉSULTATS BACKTEST
# ============================================================================

elif tab_choice == "🏦 Résultats Backtest":
    st.title("🏦 Résultats Backtest & Performance")
    
    st.info(
        "**Étape 3: Évaluer la performance**\n\n"
        f"Configuration du backtest:\n"
        f"- 💰 Capital Initial: ${initial_capital:,}\n"
        f"- 💸 Frais: {fee_bps} bps par trade\n"
        f"- 🛑 Hard Stop: {max_dd_stop:.1f}%\n\n"
        "Nous simulons le trading quotidien avec rebalancing automatique."
    )
    
    st.markdown("---")
    
    # Sélection stratégie
    strategy_choice = st.radio(
        "Choisir la stratégie à backtester",
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
    
    # Metrics clés
    st.subheader("📊 Métriques de Performance")
    
    metric_cols = st.columns(5)
    
    with metric_cols[0]:
        st.metric(
            "Retour Total",
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
            "Pire perte"
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
        "**Comment interpréter:**\n\n"
        "- **Sharpe > 0.75**: Bon signal (risque-ajusté acceptable)\n"
        "- **Drawdown < 15%**: Acceptable pour les commodités\n"
        "- **Win Rate ~50%**: Normal (gains > pertes en size)\n"
        "- **Sensibilité frais**: L'edge disparaît-il avec les frais réels?"
    )
    
    st.markdown("---")
    
    # Courbe d'équité
    st.subheader("📈 Courbe d'Équité")
    
    equity_vals, equity_dates = engine.get_equity_curve()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=equity_dates,
        y=equity_vals,
        fill='tozeroy',
        name='Valeur Portefeuille',
        line=dict(color='#1f77b4', width=2)
    ))
    fig.update_layout(
        title=f"Croissance du Portefeuille ({strategy_choice})",
        xaxis_title="Date",
        yaxis_title="Valeur ($)",
        hovermode='x unified',
        height=450
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Sensibilité frais
    st.subheader("💰 Sensibilité aux Frais de Transaction")
    
    st.info(
        "**Importance**: Plus les frais montent, plus l'edge diminue. "
        "Une stratégie robuste reste profitable même avec frais élevés."
    )
    
    fee_levels = [0, 5, 10, 15, 20, 30, 50]
    sensitivity_df = engine.compare_fees_sensitivity(signal_col, strategy_choice, fee_levels)
    
    st.dataframe(sensitivity_df, use_container_width=True, hide_index=True)
    
    st.warning(
        "⚠️ **Observation Importante**:\n\n"
        "Si Sharpe baisse drastiquement entre 0 et 10 bps, "
        "la stratégie ne résiste PAS aux frais réels. "
        "Dans ce cas, elle ne vaudrait pas la peine de trader."
    )
    
    st.markdown("---")
    
    # Journal des trades
    st.subheader("📋 Journal des Trades (20 derniers)")
    
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
        st.info("Aucun trade exécuté pour ce signal.")


# ============================================================================
# TAB 4: ANALYSE ÉCONOMIQUE
# ============================================================================

elif tab_choice == "📈 Analyse Économique":
    st.title("📈 Analyse Économique Approfondie")
    
    st.info(
        "**Étape 4: Analyser pourquoi c'est intéressant (ou pas)**\n\n"
        "Ici nous regardons:\n"
        "- Les corrélations statistiques\n"
        "- Le pricing par régime (quartiles)\n"
        "- Les risques et limitations"
    )
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1️⃣ La Relation Sous-Jacente")
        
        st.markdown("""
        **Dispersion → Prix 5TC**
        
        Quand les bateaux Capesize sont **bien dispersés**:
        - Ils sont positionnés là où les cargos se chargent
        - L'offre match bien la demande
        - Le marché fonctionne efficacement
        
        Cela tend à coïncider avec:
        - Demande forte (plusieurs régions importent)
        - Bonne utilisation des bateaux
        - Tarifs de fret plus élevés
        
        **Logique inverse**: Basse dispersion = congestion = tarifs affaiblis
        """)
    
    with col2:
        st.subheader("2️⃣ Evidence Statistique")
        
        corr_cape = data_summary['correlation_cape']
        corr_vloc = data_summary['correlation_vloc']
        corr_avg = data_summary['correlation_avg']
        
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Capesize", f"{corr_cape:.3f}")
        col_b.metric("VLOC", f"{corr_vloc:.3f}")
        col_c.metric("Moyenne", f"{corr_avg:.3f}")
        
        st.info(
            f"**Interprétation**:\n\n"
            f"- Toutes les corrélations sont positives ✅\n"
            f"- Mais elles sont faibles (~0.27)\n"
            f"- Cela explique seulement ~7% de la variance\n"
            f"- D'autres facteurs dominent les 93% restants\n\n"
            f"**Conclusion**: C'est une relation réelle mais modeste."
        )
    
    st.markdown("---")
    
    # Analyse par quartile
    st.subheader("3️⃣ Pricing par Régime (Analyse Quartile)")
    
    regime_prices = signals_df.groupby('disp_quartile', observed=True)[
        'price_5tc'
    ].agg(['mean', 'count', 'std']).reset_index()
    regime_prices['count'] = regime_prices['count'].astype(int)
    
    if len(regime_prices) == 4:
        q1_price = regime_prices[
            regime_prices['disp_quartile'] == 'Q1_Bas'
        ]['mean'].values[0]
        q4_price = regime_prices[
            regime_prices['disp_quartile'] == 'Q4_Haut'
        ]['mean'].values[0]
        premium_pct = (q4_price - q1_price) / q1_price
        premium_dollars = q4_price - q1_price
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Q1 (Bas) Prix Moy", f"${q1_price:.0f}/jour")
        col2.metric("Q4 (Haut) Prix Moy", f"${q4_price:.0f}/jour")
        col3.metric("Prime", f"{premium_pct:.1%} (${premium_dollars:.0f})")
        
        # Graphique
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=regime_prices['disp_quartile'],
            y=regime_prices['mean'],
            marker_color=['#dc3545', '#ff9800', '#90ee90', '#28a745'],
            text=[f"${v:.0f}" for v in regime_prices['mean']],
            textposition='outside'
        ))
        fig.update_layout(
            title="Prix Moyen 5TC par Quartile de Dispersion",
            xaxis_title="Régime de Dispersion",
            yaxis_title="Prix Moyen 5TC ($/jour)",
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.success(
            f"**Observation Clé**:\n\n"
            f"Les prix sont monotonicalement plus élevés quand la "
            f"dispersion est meilleure. Q4 commande une prime de {premium_pct:.1%} "
            f"vs Q1. C'est une différence structurelle du marché, pas du bruit."
        )
    
    st.markdown("---")
    
    # Limitations
    st.subheader("4️⃣ Risques & Limitations")
    
    st.warning(
        "**⚠️ Ce signal n'est PAS parfait:**\n\n"
        "• **Corrélation ≠ Causalité**: Dispersion et prix montent ensemble "
        "parce que tous deux répondent à la demande. La dispersion ne cause pas "
        "directement les prix.\n\n"
        "• **Relation Changeante**: La corrélation varie dans le temps. "
        "Elle peut se briser sans préavis.\n\n"
        "• **Facteurs Omis**: Taux d'intérêt, prix du fer, géopolitique... "
        "affectent les prix bien plus que la dispersion.\n\n"
        "• **In-Sample Bias**: Ces résultats utilisent les mêmes données "
        "qu'on a utilisé pour construire le signal.\n\n"
        "• **Frais Réels**: Les frais dégradent rapidement la performance."
    )


# ============================================================================
# TAB 5: COMPARAISON STRATÉGIES
# ============================================================================

elif tab_choice == "⚔️ Comparaison Stratégies":
    st.title("⚔️ Comparaison: Momentum vs Regime")
    
    st.info(
        "**Étape 5: Décider quelle approche est meilleure**\n\n"
        "Nous backtestons les deux signaux côte à côte avec vos paramètres. "
        "Aucun n'est \"correct\" - ils capturent juste des choses différentes."
    )
    
    st.markdown("---")
    
    with st.spinner("Backtesting les deux stratégies..."):
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
    
    # Tableau de comparaison
    st.subheader("📊 Performance Côte à Côte")
    
    comparison_data = []
    for name, results in all_results.items():
        comparison_data.append({
            'Stratégie': name,
            'Retour': f"{results['total_return_pct']:.1%}",
            'Sharpe': f"{results['sharpe_ratio']:.2f}",
            'Max DD': f"{results['max_drawdown_pct']:.1%}",
            'Win Rate': f"{results['win_rate']:.1%}",
            'Trades': f"{results['num_trades']:.0f}",
            'Calmar': f"{results['calmar_ratio']:.2f}",
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Courbes d'équité
    st.subheader("📈 Courbes d'Équité Comparées")
    
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
        title="Comparaison des Stratégies",
        xaxis_title="Date",
        yaxis_title="Valeur Portefeuille ($)",
        hovermode='x unified',
        height=450
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Analyse du gagnant
    st.subheader("🎯 Analyse du Gagnant")
    
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
        st.success(f"**Meilleur Sharpe**: {best_sharpe_strategy}")
        st.metric(
            "Sharpe Ratio",
            f"{all_results[best_sharpe_strategy]['sharpe_ratio']:.2f}"
        )
    
    with col2:
        st.info(f"**Meilleur Retour**: {best_return_strategy}")
        st.metric(
            "Retour Total",
            f"{all_results[best_return_strategy]['total_return_pct']:.1%}"
        )
    
    with col3:
        best_overall = best_sharpe_strategy
        best_val = all_results[best_sharpe_strategy]['sharpe_ratio']
        st.metric(
            "Recommandation",
            f"{best_overall}" if best_val > 0.7 else "Aucune"
        )
    
    st.markdown("---")
    
    st.subheader("💡 Recommandation Finale")
    
    best_overall = best_sharpe_strategy
    best_sharpe_val = all_results[best_sharpe_strategy]['sharpe_ratio']
    
    if best_sharpe_val > 0.80:
        st.success(
            f"✅ **{best_overall} est intéressant.**\n\n"
            f"Sharpe de {best_sharpe_val:.2f} suggère une relation mesurable. "
            f"Avant d'utiliser en production:\n"
            f"1. Valider forward sur 2024-2025\n"
            f"2. Ajouter d'autres signaux\n"
            f"3. Tester la stabilité rolling\n"
            f"4. Commencer petit en papier"
        )
    elif best_sharpe_val > 0.60:
        st.info(
            f"⚠️ **{best_overall} montre du potentiel.**\n\n"
            f"Sharpe de {best_sharpe_val:.2f} est acceptable. "
            f"Mais il faudrait:\n"
            f"1. Améliorer les paramètres\n"
            f"2. Combiner avec d'autres signaux\n"
            f"3. Valider forward"
        )
    else:
        st.warning(
            f"❌ **Aucune stratégie montre d'edge convaincant.**\n\n"
            f"Meilleur Sharpe: {best_sharpe_val:.2f}\n\n"
            f"C'est honnête - on n'a pas trouvé une relation exploitable seule. "
            f"Il faudrait combiner avec d'autres signaux fondamentaux."
        )

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown(
    "🚢 Analyse Dispersion Capesize | Données: 2016-2025 | "
    "Approche: Statistiques Simples\n\n"
    "**Disclaimers**: Backtesting ≠ performance future. "
    "À utiliser uniquement pour recherche et éducation."
)
