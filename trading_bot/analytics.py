"""
Portfolio analytics and performance metrics
Calculates P&L, returns, and trading statistics
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from .logger import logger


class PortfolioAnalytics:
    """Analyze portfolio performance and statistics"""
    
    def __init__(self):
        """Initialize portfolio analytics"""
        self.trades = []
    
    def add_trade(
        self,
        symbol: str,
        side: str,
        quantity: float,
        entry_price: float,
        timestamp: Optional[datetime] = None
    ) -> None:
        """
        Add a trade to portfolio
        
        Args:
            symbol: Trading pair symbol
            side: Order side ('BUY' or 'SELL')
            quantity: Quantity traded
            entry_price: Execution price
            timestamp: Trade timestamp
        """
        trade = {
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'price': entry_price,
            'timestamp': timestamp or datetime.now(),
            'value': quantity * entry_price
        }
        self.trades.append(trade)
        logger.debug(f"Trade added: {symbol} {side} {quantity} @ {entry_price}")
    
    def calculate_pnl(self, current_prices: Dict[str, float]) -> Dict[str, Any]:
        """
        Calculate profit and loss for all positions
        
        Args:
            current_prices: Current prices for symbols {symbol: price}
            
        Returns:
            P&L analysis by symbol and total
        """
        pnl_data = {}
        
        # Group trades by symbol
        symbols = set(trade['symbol'] for trade in self.trades)
        
        for symbol in symbols:
            symbol_trades = [t for t in self.trades if t['symbol'] == symbol]
            current_price = current_prices.get(symbol, 0)
            
            if current_price == 0:
                continue
            
            buy_trades = [t for t in symbol_trades if t['side'] == 'BUY']
            sell_trades = [t for t in symbol_trades if t['side'] == 'SELL']
            
            buy_qty = sum(t['quantity'] for t in buy_trades)
            sell_qty = sum(t['quantity'] for t in sell_trades)
            buy_value = sum(t['value'] for t in buy_trades)
            sell_value = sum(t['value'] for t in sell_trades)
            
            # Current position
            position = buy_qty - sell_qty
            
            if position > 0:
                # Long position
                avg_entry = buy_value / buy_qty if buy_qty > 0 else 0
                unrealized_pnl = position * (current_price - avg_entry)
                realized_pnl = sell_value - (sell_qty * avg_entry) if sell_qty > 0 else 0
            else:
                # Short position or closed
                avg_entry = buy_value / buy_qty if buy_qty > 0 else 0
                realized_pnl = sell_value - buy_value
                unrealized_pnl = 0
            
            pnl_data[symbol] = {
                'symbol': symbol,
                'position': position,
                'current_price': current_price,
                'entry_price': avg_entry,
                'unrealized_pnl': unrealized_pnl,
                'realized_pnl': realized_pnl,
                'total_pnl': unrealized_pnl + realized_pnl,
                'pnl_percentage': ((unrealized_pnl + realized_pnl) / buy_value * 100) if buy_value > 0 else 0
            }
        
        # Calculate totals
        total_unrealized = sum(p['unrealized_pnl'] for p in pnl_data.values())
        total_realized = sum(p['realized_pnl'] for p in pnl_data.values())
        total_pnl = total_unrealized + total_realized
        total_investment = sum(
            t['value'] for t in self.trades if t['side'] == 'BUY'
        )
        
        return {
            'by_symbol': pnl_data,
            'total': {
                'unrealized_pnl': total_unrealized,
                'realized_pnl': total_realized,
                'total_pnl': total_pnl,
                'pnl_percentage': (total_pnl / total_investment * 100) if total_investment > 0 else 0,
                'total_investment': total_investment
            }
        }
    
    def calculate_win_rate(self, realized_trades: List[Dict]) -> Dict[str, Any]:
        """
        Calculate trading win rate
        
        Args:
            realized_trades: List of closed trades with P&L
            
        Returns:
            Win rate statistics
        """
        if not realized_trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0
            }
        
        winning = [t for t in realized_trades if t.get('pnl', 0) > 0]
        losing = [t for t in realized_trades if t.get('pnl', 0) < 0]
        
        win_rate = (len(winning) / len(realized_trades) * 100) if realized_trades else 0
        
        total_wins = sum(t.get('pnl', 0) for t in winning)
        total_losses = abs(sum(t.get('pnl', 0) for t in losing))
        
        avg_win = total_wins / len(winning) if winning else 0
        avg_loss = total_losses / len(losing) if losing else 0
        
        profit_factor = total_wins / total_losses if total_losses > 0 else 0
        
        return {
            'total_trades': len(realized_trades),
            'winning_trades': len(winning),
            'losing_trades': len(losing),
            'win_rate': round(win_rate, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'profit_factor': round(profit_factor, 2)
        }
    
    def get_trading_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive trading summary
        
        Returns:
            Summary statistics
        """
        if not self.trades:
            return {
                'total_trades': 0,
                'symbols_traded': [],
                'total_volume': 0,
                'total_value_traded': 0
            }
        
        buy_trades = [t for t in self.trades if t['side'] == 'BUY']
        sell_trades = [t for t in self.trades if t['side'] == 'SELL']
        
        total_volume = sum(t['quantity'] for t in self.trades)
        total_value = sum(t['value'] for t in self.trades)
        
        symbols = sorted(list(set(t['symbol'] for t in self.trades)))
        
        return {
            'total_trades': len(self.trades),
            'buy_trades': len(buy_trades),
            'sell_trades': len(sell_trades),
            'symbols_traded': symbols,
            'total_volume': round(total_volume, 8),
            'total_value_traded': round(total_value, 2),
            'avg_trade_size': round(total_value / len(self.trades), 2) if self.trades else 0,
            'oldest_trade': min((t['timestamp'] for t in self.trades), default=None),
            'latest_trade': max((t['timestamp'] for t in self.trades), default=None)
        }
