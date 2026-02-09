"""
Order history tracking and management
Persists order data to JSON for historical analysis
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from .logger import logger


class OrderHistoryManager:
    """Manage and track order history"""
    
    def __init__(self, history_file: str = 'data/order_history.json'):
        """
        Initialize order history manager
        
        Args:
            history_file: Path to store order history
        """
        self.history_file = Path(history_file)
        self.history_file.parent.mkdir(exist_ok=True, parents=True)
        self._load_history()
    
    def _load_history(self):
        """Load existing order history from file"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
                logger.debug(f"Loaded {len(self.history)} orders from history")
            else:
                self.history = []
                logger.debug("Starting new order history")
        except Exception as e:
            logger.error(f"Error loading order history: {e}")
            self.history = []
    
    def _save_history(self):
        """Save order history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
            logger.debug(f"Saved {len(self.history)} orders to history")
        except Exception as e:
            logger.error(f"Error saving order history: {e}")
    
    def add_order(self, order_data: Dict[str, Any]) -> None:
        """
        Add an order to history
        
        Args:
            order_data: Order information from Binance API
        """
        try:
            record = {
                'timestamp': datetime.now().isoformat(),
                'order_id': order_data.get('orderId'),
                'symbol': order_data.get('symbol'),
                'side': order_data.get('side'),
                'type': order_data.get('type'),
                'quantity': float(order_data.get('origQty', 0)),
                'price': float(order_data.get('price', 0)),
                'stop_price': float(order_data.get('stopPrice', 0)) if order_data.get('stopPrice') else None,
                'status': order_data.get('status'),
                'executed_qty': float(order_data.get('executedQty', 0)),
                'avg_price': float(order_data.get('avgPrice', 0)) if order_data.get('avgPrice') else None,
            }
            self.history.append(record)
            self._save_history()
            logger.info(f"Order {record['order_id']} added to history")
        except Exception as e:
            logger.error(f"Error adding order to history: {e}")
    
    def get_order_history(self, symbol: Optional[str] = None, side: Optional[str] = None) -> List[Dict]:
        """
        Get order history with optional filters
        
        Args:
            symbol: Filter by symbol (e.g., 'BTCUSDT')
            side: Filter by side ('BUY' or 'SELL')
            
        Returns:
            List of orders matching filters
        """
        filtered = self.history
        
        if symbol:
            filtered = [o for o in filtered if o['symbol'] == symbol.upper()]
        
        if side:
            filtered = [o for o in filtered if o['side'] == side.upper()]
        
        # Return newest first
        return sorted(filtered, key=lambda x: x['timestamp'], reverse=True)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Calculate order statistics
        
        Returns:
            Statistics about all orders
        """
        if not self.history:
            return {
                'total_orders': 0,
                'buy_orders': 0,
                'sell_orders': 0,
                'total_quantity_traded': 0,
                'avg_order_value': 0,
                'unique_symbols': []
            }
        
        buy_orders = [o for o in self.history if o['side'] == 'BUY']
        sell_orders = [o for o in self.history if o['side'] == 'SELL']
        
        total_quantity = sum(o['executed_qty'] or o['quantity'] for o in self.history)
        avg_value = sum(
            (o['executed_qty'] or o['quantity']) * (o['avg_price'] or o['price'])
            for o in self.history
        ) / len(self.history) if self.history else 0
        
        unique_symbols = list(set(o['symbol'] for o in self.history))
        
        return {
            'total_orders': len(self.history),
            'buy_orders': len(buy_orders),
            'sell_orders': len(sell_orders),
            'total_quantity_traded': round(total_quantity, 8),
            'avg_order_value': round(avg_value, 2),
            'unique_symbols': sorted(unique_symbols)
        }
    
    def get_symbol_statistics(self, symbol: str) -> Dict[str, Any]:
        """
        Get statistics for a specific symbol
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Statistics for the symbol
        """
        symbol = symbol.upper()
        symbol_orders = [o for o in self.history if o['symbol'] == symbol]
        
        if not symbol_orders:
            return {
                'symbol': symbol,
                'total_orders': 0,
                'buy_count': 0,
                'sell_count': 0,
                'total_bought': 0,
                'total_sold': 0
            }
        
        buy_orders = [o for o in symbol_orders if o['side'] == 'BUY']
        sell_orders = [o for o in symbol_orders if o['side'] == 'SELL']
        
        return {
            'symbol': symbol,
            'total_orders': len(symbol_orders),
            'buy_count': len(buy_orders),
            'sell_count': len(sell_orders),
            'total_bought': round(sum(o['executed_qty'] or o['quantity'] for o in buy_orders), 8),
            'total_sold': round(sum(o['executed_qty'] or o['quantity'] for o in sell_orders), 8),
        }
