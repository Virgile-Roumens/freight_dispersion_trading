"""
ARCHITECTURE RAPIDE - Référence pour Developers
================================================

Structure du Projet:
"""

# ============================================================================
# STRUCTURE DES FICHIERS
# ============================================================================

"""
├── cape_front_month.csv                [Données d'entrée]
├── dispersion_case_study.csv           [Données d'entrée]
├── requirements.txt                    [Dépendances Python]
│
├── data_manager.py                     [Classe #1: Chargement données]
│   ├── class DataManager
│   │   ├── __init__(price_csv, dispersion_csv)
│   │   ├── get_clean_data()            → DataFrame propre
│   │   ├── get_data_summary()          → Dict avec stats
│   │   └── validate_data()             → Rapport qualité
│
├── signal_generator.py                 [Classe #2: Signaux]
│   ├── class SignalGenerator
│   │   ├── __init__(clean_data)
│   │   ├── get_signals_dataframe()     → DataFrame avec signaux
│   │   ├── get_signal_statistics()     → Stats par signal
│   │   ├── get_all_explanations()      → Explications économiques
│   │   └── signal_summary()            → Résumé texte
│
├── backtest_engine.py                  [Classe #3: Backtest]
│   ├── class BacktestEngine
│   │   ├── __init__(data_with_signals, params)
│   │   ├── backtest_strategy()         → Dict résultats
│   │   ├── get_results()               → Métriques finales
│   │   ├── get_trade_log()             → DataFrame trades
│   │   ├── get_equity_curve()          → Courbe équité
│   │   └── compare_fees_sensitivity()  → Sensibilité frais
│
└── streamlit_app.py                    [Interface Utilisateur]
    ├── @st.cache_resource load_data_once()
    ├── Tab 1: 📊 Aperçu Données
    ├── Tab 2: 🎯 Explorateur Signaux
    ├── Tab 3: 🏦 Résultats Backtest
    ├── Tab 4: 📈 Analyse Économique
    └── Tab 5: ⚔️ Comparaison Stratégies
"""

# ============================================================================
# FLUX DE DONNÉES
# ============================================================================

"""
CSV (prix + dispersion)
    │
    ↓
DataManager.load()
    │
    ├─→ price_data (nettoyé)
    ├─→ dispersion_data (Capesize + VLOC séparés)
    └─→ merged_data (fusionné, features basiques)
    │
    ↓
clean_data = DataManager.get_clean_data()
    │
    ↓
SignalGenerator(clean_data)
    │
    ├─→ Calcule z-scores, quartiles, momentum
    ├─→ Crée signal_momentum (+ ou -)
    └─→ Crée signal_regime (+ ou -)
    │
    ↓
signals_df = SignalGenerator.get_signals_dataframe()
    │
    ↓
BacktestEngine(signals_df)
    │
    ├─→ Simule trades quotidiens
    ├─→ Calcule P&L avec frais
    └─→ Génère equity curve
    │
    ↓
results = BacktestEngine.backtest_strategy()
    │
    ├─→ Sharpe, Drawdown, Return, Win Rate
    ├─→ Trade log
    └─→ Equity curve
    │
    ↓
Streamlit Dashboard affiche tout
"""

# ============================================================================
# CLASSES - VUE D'ENSEMBLE
# ============================================================================

class DataManager:
    """
    Responsabilités:
    - Charger prix 5TC front-month
    - Charger dispersion (Capesize + VLOC)
    - Fusionner les données
    - Valider la qualité
    - Fournir DataFrame propre
    
    Inputs:
    - cape_front_month.csv (date, value)
    - dispersion_case_study.csv (date, VesselClass, VesselCount, Dispersion)
    
    Outputs:
    - DataFrame merged avec colonnes:
      - date, price_5tc
      - cape_dispersion, cape_vessel_count
      - vloc_dispersion, vloc_vessel_count
      - avg_dispersion (pondérée)
      - log_return_1d, return_5d
      - *_disp_change_1d, *_disp_change_5d
    
    Méthodes clés:
    - get_clean_data() → DataFrame propre (NaN supprimés)
    - get_data_summary() → Dict{sample_size, corrélations, stats}
    - validate_data() → Dict{checks: outliers, gaps, variance}
    """
    pass


class SignalGenerator:
    """
    Responsabilités:
    - Normaliser données (z-scores)
    - Créer quartiles (régimes)
    - Générer 2 signaux simples
    - Expliquer économiquement
    
    Inputs:
    - DataFrame propre de DataManager
    
    Outputs:
    - DataFrame features avec colonnes:
      - *_zscore (normalisations)
      - *_quartile (classifications)
      - signal_momentum (+1, -1, 0)
      - signal_regime (+1, -1, 0)
      - *_strength (Z-scores absolus)
    
    Méthodes clés:
    - get_signals_dataframe() → DataFrame avec signaux
    - get_signal_statistics() → Dict stats par signal
    - get_all_explanations() → Dict explications économiques
    - signal_summary() → String résumé texte
    """
    pass


class BacktestEngine:
    """
    Responsabilités:
    - Simuler trading quotidien
    - Rebalancing automatique
    - Calculer P&L avec frais
    - Générer métriques (Sharpe, Drawdown, etc.)
    - Analyser sensibilité frais
    
    Inputs:
    - DataFrame avec signaux de SignalGenerator
    - initial_capital (défaut: 1M)
    - transaction_fee_bps (défaut: 10)
    - max_drawdown_stop (défaut: 0.02)
    
    Outputs:
    - results: Dict{
        sharpe_ratio, max_drawdown_pct, total_return_pct,
        win_rate, num_trades, profit_factor, ...
      }
    - trade_log: List[{entry_date, exit_date, entry_price, exit_price,
                       direction, net_pnl, return_pct, ...}]
    - equity_curve: List[portfolio values]
    
    Méthodes clés:
    - backtest_strategy(signal_col) → Dict résultats
    - get_results() → Dict métriques
    - get_trade_log() → DataFrame trades
    - get_equity_curve() → (values, dates)
    - compare_fees_sensitivity(fee_levels) → DataFrame sensibilité
    """
    pass


# ============================================================================
# SIGNAUX - DÉTAIL TECHNIQUE
# ============================================================================

"""
SIGNAL 1: MOMENTUM DISPERSION
=============================

Calcul:
  avg_disp_change_5d = avg_dispersion[t] - avg_dispersion[t-5]
  
  signal_momentum = sign(avg_disp_change_5d)
                  = +1 si > 0 (LONG)
                  = -1 si < 0 (SHORT)
                  =  0 sinon (FLAT)

Strength:
  momentum_zscore = (avg_disp_change_5d - mean_60d) / std_60d
  strength = |momentum_zscore|

Logique économique:
  ↑ Dispersion = bateaux se dispersent (réagissent à demande)
  ↓ Dispersion = bateaux se concentrent (demande faible)

Horizon: 5-20 jours (court terme)


SIGNAL 2: REGIME (QUARTILES)
============================

Calcul:
  quartile = pd.qcut(avg_dispersion, q=4)
           = [Q1_Bas, Q2_Moyen_Bas, Q3_Moyen_Haut, Q4_Haut]
  
  signal_regime = +1 si quartile in [Q3_Moyen_Haut, Q4_Haut]
                = -1 si quartile == Q1_Bas
                =  0 sinon

Strength:
  avg_disp_zscore = (avg_dispersion - mean_60d) / std_60d
  strength = |avg_disp_zscore|

Logique économique:
  Q4 (haute dispersion) = marché équilibré = prix élevés
  Q1 (basse dispersion) = congestion = prix bas
  Capture l'état structurel

Horizon: Multi-semaines (long terme relatif)
"""

# ============================================================================
# MÉTRIQUES BACKTEST - DÉFINITIONS
# ============================================================================

"""
RETOUR TOTAL
============
total_return = (final_equity - initial_capital) / initial_capital

Exemples:
  - 18% = bon
  - 5% = faible
  - -5% = perte


SHARPE RATIO
============
sharpe = (mean_excess_return / std_excess_return) * sqrt(252)

where:
  excess_return = daily_return - risk_free_rate
  risk_free_rate ≈ 2% annualisé = 0.02 / 252 par jour

Interprétation:
  - < 0.5: Faible
  - 0.5-0.75: Acceptable
  - 0.75-1.0: Bon ← VOUS ÊTES ICI
  - > 1.0: Excellent (rare)


MAX DRAWDOWN
============
drawdown_t = (portfolio_t - max_portfolio_0_to_t) / max_portfolio_0_to_t
max_drawdown = min(drawdown_t)

Exemples:
  - -5% = excellent
  - -12% = acceptable
  - -25% = risqué


WIN RATE
========
win_rate = num_winning_trades / total_trades

Exemples:
  - 50% = normal (si gains > pertes)
  - 55% = bon
  - 60% = excellent

Note: Win rate ne suffit pas. Exemple:
  - 60% gagnants mais -1% moy
  - 40% perdants mais -10% moy
  → Win rate 60% mais PnL négatif (mauvais sizing)


CALMAR RATIO
============
calmar = annual_return / abs(max_drawdown)

Interprétation:
  - > 2.0: Excellent (bonne retour, peu de risque)
  - > 1.0: Bon
  - < 0.5: Faible


PROFIT FACTOR
==============
profit_factor = total_winning_pnl / abs(total_losing_pnl)

Exemples:
  - 2.0 = 2x plus de gains que de pertes → bon
  - 1.5 = bon
  - 1.0 = break-even
  - < 1.0 = négatif
"""

# ============================================================================
# UTILISATION COURANTE
# ============================================================================

"""
CHARGER, GÉNÉRER SIGNAUX, BACKTESTER:
======================================

    from data_manager import DataManager
    from signal_generator import SignalGenerator
    from backtest_engine import BacktestEngine
    
    # 1. Charger
    dm = DataManager('cape_front_month.csv', 'dispersion_case_study.csv')
    data = dm.get_clean_data()
    
    # 2. Signaux
    sg = SignalGenerator(data)
    signals = sg.get_signals_dataframe()
    
    # 3. Backtest
    engine = BacktestEngine(signals, initial_capital=1_000_000, fee_bps=10)
    results_momentum = engine.backtest_strategy('signal_momentum', 'Momentum')
    results_regime = engine.backtest_strategy('signal_regime', 'Regime')
    
    # 4. Afficher
    print(f"Momentum: Sharpe={results_momentum['sharpe_ratio']:.2f}")
    print(f"Regime: Sharpe={results_regime['sharpe_ratio']:.2f}")


EXPLORER INTERACTIVEMENT (STREAMLIT):
====================================

    streamlit run streamlit_app.py
    
    # Puis:
    # 1. Tab "Data Overview" → Vérifier corrélations
    # 2. Tab "Signal Explorer" → Comprendre les signaux
    # 3. Tab "Backtest Results" → Voir performance
    # 4. Tab "Economic Analysis" → Analyser pourquoi
    # 5. Tab "Strategy Comparison" → Comparer les deux
"""

# ============================================================================
# CUSTOMISATION
# ============================================================================

"""
MODIFIER LES PARAMÈTRES DES SIGNAUX
===================================

Dans SignalGenerator._compute_features():
  
  window = 60  # Fenêtre rolling pour z-scores
             # Essayer: 30 (rapide), 90 (stable), 120 (très stable)
  
  Q1/Q2/Q3/Q4 = pd.qcut(avg_dispersion, q=4)
              # Essayer: q=3 (3 régimes), q=5 (5 régimes)
  
  signal_momentum = sign(change_5d)
                  # Essayer: change_1d, change_10d
  
  regime = Q3+Q4 LONG, Q1 SHORT
        # Essayer: Q4 LONG only, Q1-Q2 SHORT


MODIFIER LES PARAMÈTRES DU BACKTEST
===================================

Dans BacktestEngine.__init__():
  
  initial_capital = 1_000_000
                  # Essayer: 100k (petit), 5M (large)
  
  transaction_fee_bps = 10
                      # Essayer: 0 (aucun), 5 (optimiste), 20 (pessimiste)
  
  max_drawdown_stop = 0.02
                    # Essayer: 0.01 (strict), 0.03 (loose), 0 (désactiver)


IMPORTANT: Toujours tester forward après customisation!
"""

# ============================================================================
# LIMITATIONS CONNUES
# ============================================================================

"""
1. CORRÉLATION FAIBLE (r=0.27)
   - Explique seulement 7% de la variance
   - D'autres facteurs dominent 93%

2. IN-SAMPLE BIAS
   - Données utilisées pour construire = données utilisées pour tester
   - Forward-test obligatoire

3. RÉGIMES CHANGEANTS
   - La corrélation peut se briser à tout moment
   - Monitoring rolling recommandé

4. FRAIS RÉELS
   - L'edge diminue rapidement avec les frais
   - 10 bps est conservateur; vrais coûts peuvent être plus hauts

5. FACTEURS OMIS
   - Prix fer, taux USD, géopolitique, sentiment
   - Affectent les prix plus que la dispersion

6. DONNÉES DE QUALITÉ
   - Si CSV mal formatées → résultats invalides
   - Vérifier avec validate_data()
"""

# ============================================================================
# STRUCTURE DES DONNÉES (DÉTAIL)
# ============================================================================

"""
APRÈS DataManager.get_clean_data():
===================================

Colonne              | Type     | Source            | Sens
─────────────────────┼──────────┼───────────────────┼──────────────────
date                 | datetime | Input             | Date du jour
price_5tc            | float    | cape_front_month  | Prix 5TC $/jour
cape_vessel_count    | int      | dispersion_csv    | # Capesize
cape_dispersion      | float    | dispersion_csv    | Dispersion Cape
vloc_vessel_count    | int      | dispersion_csv    | # VLOC
vloc_dispersion      | float    | dispersion_csv    | Dispersion VLOC
total_vessel_count   | int      | Calculé           | Cape + VLOC
avg_dispersion       | float    | Calculé           | Pondérée par count
log_return_1d        | float    | Calculé           | Log-return prix 1j
return_5d            | float    | Calculé           | Return prix 5j
cape_disp_change_1d  | float    | Calculé           | Δ Cape disp 1j
cape_disp_change_5d  | float    | Calculé           | Δ Cape disp 5j
vloc_disp_change_1d  | float    | Calculé           | Δ VLOC disp 1j
vloc_disp_change_5d  | float    | Calculé           | Δ VLOC disp 5j
avg_disp_change_1d   | float    | Calculé           | Δ Avg disp 1j
avg_disp_change_5d   | float    | Calculé           | Δ Avg disp 5j


APRÈS SignalGenerator.get_signals_dataframe():
==============================================

+ Des colonnes ci-dessus, ajoute:

Colonne              | Type     | Sens
─────────────────────┼──────────┼────────────────────────────
avg_disp_zscore      | float    | Normalisation avg_disp
cape_disp_zscore     | float    | Normalisation cape_disp
vloc_disp_zscore     | float    | Normalisation vloc_disp
price_zscore         | float    | Normalisation prix
momentum_zscore      | float    | Normalisation momentum
disp_quartile        | str      | Q1/Q2/Q3/Q4 (régime)
signal_momentum      | int      | +1/-1/0
signal_momentum_strength | float | |momentum_zscore|
signal_regime        | int      | +1/-1/0
signal_regime_strength | float | |avg_disp_zscore|
"""

# ============================================================================
# POUR DÉBOGUER
# ============================================================================

"""
SI QUELQUE CHOSE NE VA PAS:
==========================

1. Vérifier les données d'entrée:
   >>> dm = DataManager(...)
   >>> summary = dm.get_data_summary()
   >>> print(summary)
   # Vérifier: sample_size, date range, corrélations
   
   >>> validation = dm.validate_data()
   >>> print(validation)
   # Vérifier: tous les checks au vert?

2. Vérifier que les signaux sont générés:
   >>> sg = SignalGenerator(clean_data)
   >>> signals = sg.get_signals_dataframe()
   >>> print(signals[['date', 'signal_momentum', 'signal_regime']].head(20))
   # Vérifier: +1/-1/0 alterné? Pas toutes 0?
   
   >>> stats = sg.get_signal_statistics()
   >>> print(stats)
   # Vérifier: long_signals, short_signals, flat_signals > 0?

3. Vérifier le backtest:
   >>> engine = BacktestEngine(signals)
   >>> results = engine.backtest_strategy('signal_momentum', 'Test')
   >>> print(results)
   # Vérifier: sharpe_ratio > 0? num_trades > 0? fees paid > 0?
   
   >>> trades = engine.get_trade_log()
   >>> print(trades.head(20))
   # Vérifier: entry/exit dates, net_pnl réalistes?
   
   >>> equity_vals, equity_dates = engine.get_equity_curve()
   >>> print(f"Start: {equity_vals[0]}, End: {equity_vals[-1]}")
   # Vérifier: courbe monotone croissante/décroissante?

4. Vérifier le Streamlit:
   >>> streamlit run streamlit_app.py --logger.level=debug
   # Attendre 30s au premier lancement (cache)
   # Vérifier les erreurs dans la console
"""

print(__doc__)
