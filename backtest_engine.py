"""
BacktestEngine Class - Portfolio Simulation and Performance

Responsibilities:
- Simulate daily trading
- Automatic rebalancing
- Calculate P&L with realistic fees
- Performance metrics (Sharpe, Drawdown, Win Rate)
- Fee sensitivity analysis- Supports both signal types: signal_momentum, signal_mean_reversion

Economic Context:
- Signal values range from -1.0 (100% SHORT) to +1.0 (100% LONG)
- Position sizing is proportional to signal strength (0.25, 0.50, 0.75, 1.00)
- Fees applied on entry and exit (basis points per trade)"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, List
from datetime import datetime
from pathlib import Path
import warnings

# FRED API for risk-free rate
try:
    from fredapi import Fred
    FRED_AVAILABLE = True
except ImportError:
    FRED_AVAILABLE = False
    warnings.warn("fredapi not installed. Install with: pip install fredapi")


class BacktestEngine:
    """
    Backtests strategies with realistic assumptions.
    
    Attributes:
        data (pd.DataFrame): DataFrame with signals
        initial_capital (float): Initial capital
        transaction_fee_bps (float): Fees in basis points
        results (dict): Backtest results
        trade_log (list): Trade history
        equity_curve (list): Equity curve
    """
    
    def __init__(
        self,
        data_with_signals: pd.DataFrame,
        initial_capital: float = 1_000_000,
        transaction_fee_bps: float = 10
    ):
        """
        Initialize BacktestEngine.
        
        Args:
            data_with_signals: DataFrame with signals from SignalGenerator
            initial_capital: Initial capital in USD
            transaction_fee_bps: Fees per trade in basis points
        """
        self.data = data_with_signals.copy()
        self.initial_capital = initial_capital
        self.fee_bps = transaction_fee_bps / 10000  # Convert to decimal
        
        # FRED API setup for risk-free rate
        self.fred_api_key = "dddf15f3c59a3d9c5c331ecabed8a160"
        self.risk_free_rate = None  # Will be fetched dynamically
        
        # Store results
        self.results = {}
        self.trade_log = []
        self.equity_curve = []
        self.dates_equity = []
    
    def _fetch_risk_free_rate(self) -> float:
        """
        Fetch current US 10Y Treasury yield from FRED API.
        Falls back to 2% if API unavailable.
        
        Returns:
            Annual risk-free rate as decimal (e.g., 0.045 for 4.5%)
        """
        if not FRED_AVAILABLE:
            warnings.warn("FRED API not available. Using default 2% risk-free rate.")
            return 0.02
        
        try:
            fred = Fred(api_key=self.fred_api_key)
            # DGS10 = 10-Year Treasury Constant Maturity Rate
            treasury_10y = fred.get_series('DGS10', observation_start=self.data['date'].min())
            
            # Get the average rate over the backtest period
            # Filter to backtest date range
            backtest_start = self.data['date'].min()
            backtest_end = self.data['date'].max()
            treasury_10y = treasury_10y[
                (treasury_10y.index >= backtest_start) & 
                (treasury_10y.index <= backtest_end)
            ]
            
            if len(treasury_10y) > 0:
                # Use mean rate over period, convert from percentage to decimal
                avg_rate = treasury_10y.mean() / 100
                return avg_rate
            else:
                warnings.warn("No Treasury data for backtest period. Using default 2%.")
                return 0.02
                
        except Exception as e:
            warnings.warn(f"Error fetching FRED data: {e}. Using default 2%.")
            return 0.02
    
    def backtest_strategy(
        self,
        signal_column: str,
        strategy_name: str
    ) -> Dict:
        """
        Run a complete backtest.
        
        Args:
            signal_column: Signal column name. Supported signals:
                          - 'signal_momentum': Inverted momentum (HIGH disp = SHORT, LOW disp = LONG)
                          - 'signal_mean_reversion': Accordion effect (fade extremes from 120d mean)
            strategy_name: Strategy name for display and export
            
        Returns:
            Dict with results (Sharpe, Return, Drawdown, etc.)
            
        Raises:
            ValueError: If signal_column not found in data
        """
        # Validate signal column exists
        if signal_column not in self.data.columns:
            available_signals = [col for col in self.data.columns if col.startswith('signal_')]
            raise ValueError(
                f"Signal column '{signal_column}' not found in data. "
                f"Available signals: {available_signals}"
            )
        
        # Fetch risk-free rate for this backtest period
        self.risk_free_rate = self._fetch_risk_free_rate()
        
        # Reset
        self.trade_log = []
        self.equity_curve = [self.initial_capital]
        self.dates_equity = [self.data.iloc[0]['date']]
        
        position = 0  # +1 (LONG), -1 (SHORT), 0 (FLAT)
        entry_price = None
        entry_date = None
        capital = self.initial_capital
        
        # Loop over each day
        for i in range(len(self.data)):
            row = self.data.iloc[i]
            new_signal = row[signal_column]
            current_price = row['price_5tc']
            current_date = row['date']
            
            # Check if rebalancing necessary
            should_rebalance = False
            
            # Rebalance if signal changes (accounting for fractional signals)
            current_signal_direction = np.sign(position)
            new_signal_direction = np.sign(new_signal)
            
            # Rebalance if: direction changes OR position size changes
            if current_signal_direction != new_signal_direction:
                should_rebalance = True
            elif position != 0 and new_signal != 0:
                # Check if position size changed significantly (more than 5%)
                current_size = abs(position * entry_price / capital) if capital > 0 else 0
                target_size = abs(new_signal)
                if abs(current_size - target_size) > 0.05:
                    should_rebalance = True
            
            # REBALANCE
            if should_rebalance:
                # Close previous position
                if position != 0 and entry_price is not None:
                    # Calculate notional value at exit
                    position_value = abs(position) * entry_price
                    exit_pnl = position * (current_price - entry_price)
                    fee_exit = position_value * self.fee_bps
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
                        'return_pct': exit_pnl / position_value,
                        'days_held': (current_date - entry_date).days,
                    })
                
                # Open new position - size based on signal strength and current capital
                if new_signal != 0:
                    entry_price = current_price
                    entry_date = current_date
                    # Signal contains both direction (sign) and size (magnitude)
                    # new_signal ranges from -1.0 to +1.0
                    signal_direction = np.sign(new_signal)
                    signal_size = abs(new_signal)  # 0.25, 0.50, or 1.00
                    
                    # Fees based on intended position size
                    intended_capital = capital * signal_size
                    fee_entry = intended_capital * self.fee_bps
                    investable_capital = intended_capital - fee_entry
                    
                    # Position size = (investable capital × signal_size) / price
                    position = signal_direction * (investable_capital / current_price)
                    capital -= fee_entry
                else:
                    position = 0
                    entry_price = None
                    entry_date = None
            
            # Record daily equity (mark-to-market if position open)
            if position != 0 and entry_price is not None:
                mtm_value = capital + position * (current_price - entry_price)
                self.equity_curve.append(mtm_value)
            else:
                self.equity_curve.append(capital)
            self.dates_equity.append(current_date)
        
        # Calculate metrics
        self.results = self._compute_metrics(strategy_name)
        
        return self.results
    
    def _compute_metrics(self, strategy_name: str) -> Dict:
        """Calculate all performance metrics."""
        trades_df = pd.DataFrame(self.trade_log) if self.trade_log else pd.DataFrame()
        equity_arr = np.array(self.equity_curve)
        
        # Basic returns
        total_pnl = self.equity_curve[-1] - self.initial_capital
        total_return_pct = total_pnl / self.initial_capital
        
        # Annualized return
        num_days = len(self.dates_equity)
        num_years = num_days / 252  # Trading days
        annualized_return_pct = (
            (1 + total_return_pct) ** (1 / num_years) - 1
            if num_years > 0 else 0
        )
        
        # Trade stats
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
        
        # Sharpe ratio with dynamic risk-free rate
        daily_returns = np.diff(equity_arr) / equity_arr[:-1]
        daily_rf_rate = (self.risk_free_rate if self.risk_free_rate else 0.02) / 252
        excess_returns = daily_returns - daily_rf_rate
        
        # Annualized volatility
        annualized_volatility = (
            np.std(daily_returns) * np.sqrt(252)
            if len(daily_returns) > 0
            else 0
        )
        
        sharpe = (
            (np.mean(excess_returns) / np.std(excess_returns)) * np.sqrt(252)
            if len(excess_returns) > 0 and np.std(excess_returns) > 0
            else 0
        )
        
        # Drawdown
        running_max = np.maximum.accumulate(equity_arr)
        drawdowns = (equity_arr - running_max) / running_max
        max_drawdown = np.min(drawdowns)
        
        return {
            'strategy_name': strategy_name,
            'total_return_pct': total_return_pct,
            'annualized_return_pct': annualized_return_pct,
            'annualized_volatility': annualized_volatility,
            'total_pnl': total_pnl,
            'sharpe_ratio': sharpe,
            'risk_free_rate': self.risk_free_rate if self.risk_free_rate else 0.02,
            'max_drawdown_pct': max_drawdown,
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
        """Display backtest results."""
        if not self.results:
            return
        
        print(f"\n{'─'*70}")
        print(f"RESULTS: {strategy_name}")
        print(f"{'─'*70}")
        print(f"Total Return:      {self.results['total_return_pct']:.1%} "
              f"({self.results['total_pnl']:,.0f}$)")
        print(f"Annualized Return: {self.results['annualized_return_pct']:.1%}")
        print(f"Sharpe Ratio:      {self.results['sharpe_ratio']:.2f} "
              f"(RF Rate: {self.results['risk_free_rate']:.2%})")
        print(f"Annualized Volatility: {self.results['annualized_volatility']:.1%}")
        print(f"Max Drawdown:      {self.results['max_drawdown_pct']:.1%}")
        print(f"Win Rate:          {self.results['win_rate']:.1%} "
              f"({self.results['winning_trades']}/{self.results['num_trades']})")
        print(f"Total Fees:        ${self.results['total_fees_paid']:,.0f}")
    
    def get_results(self) -> Dict:
        """Return backtest results."""
        return self.results.copy()
    
    def get_trade_log(self) -> pd.DataFrame:
        """Return trade log."""
        return pd.DataFrame(self.trade_log) if self.trade_log else pd.DataFrame()
    
    def get_equity_curve(self) -> Tuple[List, List]:
        """Return equity curve (values, dates)."""
        return self.equity_curve, self.dates_equity
    
    def compare_fees_sensitivity(
        self,
        signal_column: str,
        strategy_name: str,
        fee_levels: List[float]
    ) -> pd.DataFrame:
        """
        Analyze strategy performance across different transaction fee levels.
        
        Args:
            signal_column: 'signal_momentum' or 'signal_mean_reversion'
            strategy_name: Strategy display name
            fee_levels: List of fee levels in basis points (e.g., [0, 5, 10, 20, 50])
            
        Returns:
            DataFrame with performance metrics at each fee level
        """
        # Save original state to restore after sensitivity analysis
        original_fee = self.fee_bps
        original_results = self.results.copy() if self.results else {}
        original_trade_log = self.trade_log.copy()
        original_equity_curve = self.equity_curve.copy()
        original_dates_equity = self.dates_equity.copy()
        
        results_list = []
        
        for fee_bps in fee_levels:
            # Set new fee level
            self.fee_bps = fee_bps / 10000
            
            # Run backtest
            results = self.backtest_strategy(signal_column, strategy_name)
            
            results_list.append({
                'Fees (bps)': int(fee_bps),
                'Return': f"{results['total_return_pct']:.1%}",
                'Sharpe': f"{results['sharpe_ratio']:.2f}",
                'Max DD': f"{results['max_drawdown_pct']:.1%}",
                'Win Rate': f"{results['win_rate']:.1%}",
                'Total Fees': f"${results['total_fees_paid']:,.0f}",
            })
        
        # Restore original state
        self.fee_bps = original_fee
        self.results = original_results
        self.trade_log = original_trade_log
        self.equity_curve = original_equity_curve
        self.dates_equity = original_dates_equity
        
        return pd.DataFrame(results_list)
    
    def export_results(
        self,
        filepath: str,
        signal_lag: int = 0,
        file_format: str = 'xlsx'
    ) -> None:
        """
        Export backtest results to Excel or CSV.
        
        Args:
            filepath: Path to save file (without extension)
            signal_lag: Signal lag used in backtest
            file_format: 'xlsx' or 'csv'
        """
        from pathlib import Path
        
        # Create export directory if it doesn't exist
        export_dir = Path(filepath).parent
        export_dir.mkdir(parents=True, exist_ok=True)
        
        # Prepare metadata
        metadata = {
            'Parameter': [
                'Strategy Name',
                'Initial Capital ($)',
                'Transaction Fees (bps)',
                'Signal Lag (days)',
                'Export Date',
                '',
                'Total Return (%)',
                'Annualized Return (%)',
                'Annualized Volatility (%)',
                'Total P&L ($)',
                'Sharpe Ratio',
                'Risk-Free Rate (10Y Treasury %)',
                'Max Drawdown (%)',
                'Win Rate (%)',
                'Number of Trades',
                'Winning Trades',
                'Losing Trades',
                'Average Win ($)',
                'Average Loss ($)',
                'Profit Factor',
                'Total Fees Paid ($)'
            ],
            'Value': [
                self.results.get('strategy_name', 'N/A'),
                f"{self.initial_capital:,.0f}",
                f"{self.fee_bps * 10000:.1f}",
                signal_lag,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                '',
                f"{self.results.get('total_return_pct', 0):.2%}",
                f"{self.results.get('annualized_return_pct', 0):.2%}",
                f"{self.results.get('annualized_volatility', 0):.2%}",
                f"{self.results.get('total_pnl', 0):,.2f}",
                f"{self.results.get('sharpe_ratio', 0):.3f}",
                f"{self.results.get('risk_free_rate', 0.02):.2%}",
                f"{self.results.get('max_drawdown_pct', 0):.2%}",
                f"{self.results.get('win_rate', 0):.2%}",
                self.results.get('num_trades', 0),
                self.results.get('winning_trades', 0),
                self.results.get('losing_trades', 0),
                f"{self.results.get('avg_win', 0):,.2f}",
                f"{self.results.get('avg_loss', 0):,.2f}",
                f"{self.results.get('profit_factor', 0):.3f}",
                f"{self.results.get('total_fees_paid', 0):,.2f}"
            ]
        }
        metadata_df = pd.DataFrame(metadata)
        
        # Prepare trade log
        trades_df = self.get_trade_log()
        if not trades_df.empty:
            # Format dates
            trades_df['entry_date'] = pd.to_datetime(trades_df['entry_date']).dt.strftime('%Y-%m-%d')
            trades_df['exit_date'] = pd.to_datetime(trades_df['exit_date']).dt.strftime('%Y-%m-%d')
            # Format numbers
            trades_df['entry_price'] = trades_df['entry_price'].round(2)
            trades_df['exit_price'] = trades_df['exit_price'].round(2)
            trades_df['gross_pnl'] = trades_df['gross_pnl'].round(2)
            trades_df['fee_cost'] = trades_df['fee_cost'].round(2)
            trades_df['net_pnl'] = trades_df['net_pnl'].round(2)
            trades_df['return_pct'] = (trades_df['return_pct'] * 100).round(2)
            
            # Rename columns for clarity
            trades_df = trades_df.rename(columns={
                'entry_date': 'Entry Date',
                'exit_date': 'Exit Date',
                'entry_price': 'Entry Price ($)',
                'exit_price': 'Exit Price ($)',
                'direction': 'Direction',
                'size': 'Size (units)',
                'gross_pnl': 'Gross P&L ($)',
                'fee_cost': 'Fees ($)',
                'net_pnl': 'Net P&L ($)',
                'return_pct': 'Return (%)',
                'days_held': 'Days Held'
            })
        
        # Prepare equity curve
        equity_df = pd.DataFrame({
            'Date': [d.strftime('%Y-%m-%d') for d in self.dates_equity],
            'Equity ($)': [round(e, 2) for e in self.equity_curve]
        })
        
        # Export based on format
        if file_format.lower() == 'xlsx':
            filepath_full = f"{filepath}.xlsx"
            with pd.ExcelWriter(filepath_full, engine='openpyxl') as writer:
                metadata_df.to_excel(writer, sheet_name='Summary', index=False)
                if not trades_df.empty:
                    trades_df.to_excel(writer, sheet_name='Trade Log', index=False)
                equity_df.to_excel(writer, sheet_name='Equity Curve', index=False)
        else:  # CSV
            # For CSV, save as separate files
            metadata_df.to_csv(f"{filepath}_summary.csv", index=False)
            if not trades_df.empty:
                trades_df.to_csv(f"{filepath}_trades.csv", index=False)
            equity_df.to_csv(f"{filepath}_equity.csv", index=False)
