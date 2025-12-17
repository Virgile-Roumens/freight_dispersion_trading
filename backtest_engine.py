"""
BacktestEngine Class - Simulation de Portefeuille et Performance

Responsabilités:
- Simuler le trading quotidien
- Rebalancing automatique
- Calcul P&L avec frais réalistes
- Métriques de performance (Sharpe, Drawdown, Win Rate)
- Analyse de sensibilité aux frais
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, List
from datetime import datetime


class BacktestEngine:
    """
    Backteste les stratégies avec assumptions réalistes.
    
    Attributes:
        data (pd.DataFrame): DataFrame avec signaux
        initial_capital (float): Capital initial
        transaction_fee_bps (float): Frais en basis points
        results (dict): Résultats du backtest
        trade_log (list): Historique des trades
        equity_curve (list): Courbe d'équité
    """
    
    def __init__(
        self,
        data_with_signals: pd.DataFrame,
        initial_capital: float = 1_000_000,
        transaction_fee_bps: float = 10,
        max_drawdown_stop: float = 0.02,
        verbose: bool = True
    ):
        """
        Initialiser BacktestEngine.
        
        Args:
            data_with_signals: DataFrame avec signaux de SignalGenerator
            initial_capital: Capital initial en USD
            transaction_fee_bps: Frais par trade en basis points
            max_drawdown_stop: Hard stop si drawdown > ce %, 0 pour désactiver
            verbose: Afficher les logs
        """
        self.data = data_with_signals.copy()
        self.initial_capital = initial_capital
        self.fee_bps = transaction_fee_bps / 10000  # Convertir en décimal
        self.max_dd_stop = max_drawdown_stop
        self.verbose = verbose
        
        # Stockage des résultats
        self.results = {}
        self.trade_log = []
        self.equity_curve = []
        self.dates_equity = []
    
    def backtest_strategy(
        self,
        signal_column: str,
        strategy_name: str
    ) -> Dict:
        """
        Lancer un backtest complet.
        
        Args:
            signal_column: Colonne du signal ('signal_momentum' ou 'signal_regime')
            strategy_name: Nom de la stratégie pour affichage
            
        Returns:
            Dict avec les résultats (Sharpe, Return, Drawdown, etc.)
        """
        # Réinitialiser
        self.trade_log = []
        self.equity_curve = [self.initial_capital]
        self.dates_equity = [self.data.iloc[0]['date']]
        
        position = 0  # +1 (LONG), -1 (SHORT), 0 (FLAT)
        entry_price = None
        entry_date = None
        capital = self.initial_capital
        
        if self.verbose:
            print(f"\n{'='*70}")
            print(f"BACKTEST: {strategy_name}")
            print(f"{'='*70}")
            print(f"Capital: ${self.initial_capital:,.0f}")
            print(f"Frais: {self.fee_bps*10000:.1f} bps")
        
        # Boucle sur chaque jour
        for i in range(len(self.data)):
            row = self.data.iloc[i]
            new_signal = row[signal_column]
            current_price = row['price_5tc']
            current_date = row['date']
            
            # Vérifier si rebalancing nécessaire
            should_rebalance = False
            
            if new_signal != position:
                should_rebalance = True
            
            # Hard stop si drawdown dépassé
            if position != 0 and entry_price is not None and self.max_dd_stop > 0:
                unrealized_pnl = position * (current_price - entry_price)
                unrealized_pct = unrealized_pnl / (entry_price * abs(position))
                if unrealized_pct < -self.max_dd_stop:
                    should_rebalance = True
            
            # REBALANCE
            if should_rebalance:
                # Fermer position précédente
                if position != 0 and entry_price is not None:
                    exit_pnl = position * (current_price - entry_price)
                    fee_exit = abs(position) * current_price * self.fee_bps
                    net_pnl = exit_pnl - fee_exit
                    capital += net_pnl
                    
                    self.trade_log.append({
                        'entry_date': entry_date,
                        'exit_date': current_date,
                        'entry_price': entry_price,
                        'exit_price': current_price,
                        'direction': 'LONG' if position > 0 else 'SHORT',
                        'size': abs(position),
                        'gross_pnl': exit_pnl,
                        'fee_cost': fee_exit,
                        'net_pnl': net_pnl,
                        'return_pct': exit_pnl / (entry_price * abs(position)),
                        'days_held': (current_date - entry_date).days,
                    })
                
                # Ouvrir nouvelle position
                if new_signal != 0:
                    entry_price = current_price
                    entry_date = current_date
                    fee_entry = abs(new_signal) * current_price * self.fee_bps
                    capital -= fee_entry
                    position = new_signal
                else:
                    position = 0
                    entry_price = None
                    entry_date = None
            
            # Enregistrer equity quotidienne
            self.equity_curve.append(capital)
            self.dates_equity.append(current_date)
        
        # Calculer métriques
        self.results = self._compute_metrics(strategy_name)
        
        if self.verbose:
            self._print_results(strategy_name)
        
        return self.results
    
    def _compute_metrics(self, strategy_name: str) -> Dict:
        """Calculer toutes les métriques de performance."""
        trades_df = pd.DataFrame(self.trade_log) if self.trade_log else pd.DataFrame()
        equity_arr = np.array(self.equity_curve)
        
        # Returns basiques
        total_pnl = self.equity_curve[-1] - self.initial_capital
        total_return = total_pnl / self.initial_capital
        
        # Stats des trades
        if len(trades_df) > 0:
            winning_trades = (trades_df['net_pnl'] > 0).sum()
            losing_trades = (trades_df['net_pnl'] < 0).sum()
            num_trades = len(trades_df)
            win_rate = winning_trades / num_trades if num_trades > 0 else 0
            avg_win = trades_df[trades_df['net_pnl'] > 0]['net_pnl'].mean() if winning_trades > 0 else 0
            avg_loss = trades_df[trades_df['net_pnl'] < 0]['net_pnl'].mean() if losing_trades > 0 else 0
            profit_factor = (
                abs(winning_trades * avg_win / (losing_trades * avg_loss)) 
                if losing_trades > 0 and avg_loss != 0 else np.inf
            )
            total_fees_paid = trades_df['fee_cost'].sum() if len(trades_df) > 0 else 0
        else:
            winning_trades = 0
            losing_trades = 0
            num_trades = 0
            win_rate = 0
            avg_win = 0
            avg_loss = 0
            profit_factor = 0
            total_fees_paid = 0
        
        # Sharpe ratio
        daily_returns = np.diff(equity_arr) / equity_arr[:-1]
        excess_returns = daily_returns - (0.02 / 252)
        sharpe = (
            (np.mean(excess_returns) / np.std(excess_returns)) * np.sqrt(252)
            if len(excess_returns) > 0 and np.std(excess_returns) > 0
            else 0
        )
        
        # Drawdown
        running_max = np.maximum.accumulate(equity_arr)
        drawdowns = (equity_arr - running_max) / running_max
        max_drawdown = np.min(drawdowns)
        
        # Calmar ratio
        calmar = (
            total_return / abs(max_drawdown)
            if abs(max_drawdown) > 0
            else (np.inf if total_return > 0 else 0)
        )
        
        return {
            'strategy_name': strategy_name,
            'total_return_pct': total_return,
            'total_pnl': total_pnl,
            'sharpe_ratio': sharpe,
            'max_drawdown_pct': max_drawdown,
            'calmar_ratio': calmar,
            'win_rate': win_rate,
            'num_trades': num_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'total_fees_paid': total_fees_paid,
        }
    
    def _print_results(self, strategy_name: str) -> None:
        """Afficher les résultats du backtest."""
        if not self.results:
            return
        
        print(f"\n{'─'*70}")
        print(f"RÉSULTATS: {strategy_name}")
        print(f"{'─'*70}")
        print(f"Retour Total:      {self.results['total_return_pct']:.1%} "
              f"({self.results['total_pnl']:,.0f}$)")
        print(f"Sharpe Ratio:      {self.results['sharpe_ratio']:.2f}")
        print(f"Max Drawdown:      {self.results['max_drawdown_pct']:.1%}")
        print(f"Calmar Ratio:      {self.results['calmar_ratio']:.2f}")
        print(f"Win Rate:          {self.results['win_rate']:.1%} "
              f"({self.results['winning_trades']}/{self.results['num_trades']})")
        print(f"Frais Totaux:      ${self.results['total_fees_paid']:,.0f}")
    
    def get_results(self) -> Dict:
        """Retourner les résultats du backtest."""
        return self.results.copy()
    
    def get_trade_log(self) -> pd.DataFrame:
        """Retourner le journal des trades."""
        return pd.DataFrame(self.trade_log) if self.trade_log else pd.DataFrame()
    
    def get_equity_curve(self) -> Tuple[List, List]:
        """Retourner la courbe d'équité (values, dates)."""
        return self.equity_curve, self.dates_equity
    
    def compare_fees_sensitivity(
        self,
        signal_column: str,
        strategy_name: str,
        fee_levels: List[float]
    ) -> pd.DataFrame:
        """Analyser la sensibilité à différents niveaux de frais."""
        results_list = []
        
        for fee_bps in fee_levels:
            # Sauvegarder frais actuels
            original_fee = self.fee_bps
            self.fee_bps = fee_bps / 10000
            
            # Lancer backtest
            results = self.backtest_strategy(signal_column, strategy_name)
            
            results_list.append({
                'Frais (bps)': int(fee_bps),
                'Retour': f"{results['total_return_pct']:.1%}",
                'Sharpe': f"{results['sharpe_ratio']:.2f}",
                'Max DD': f"{results['max_drawdown_pct']:.1%}",
                'Win Rate': f"{results['win_rate']:.1%}",
                'Frais Totaux': f"${results['total_fees_paid']:,.0f}",
            })
            
            # Restaurer frais
            self.fee_bps = original_fee
        
        return pd.DataFrame(results_list)
