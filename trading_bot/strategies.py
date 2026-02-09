"""
Pre-built trading strategy templates
Provides common trading strategies for users
"""
from typing import Dict, Any, Optional
from .logger import logger


class Strategy:
    """Base strategy class"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def get_parameters(self) -> Dict[str, Dict[str, Any]]:
        """Get strategy parameters"""
        raise NotImplementedError
    
    def get_instructions(self) -> str:
        """Get strategy instructions"""
        raise NotImplementedError


class DCAStrategy(Strategy):
    """Dollar Cost Averaging Strategy"""
    
    def __init__(self):
        super().__init__(
            name="Dollar Cost Averaging (DCA)",
            description="Buy fixed amount at regular intervals to reduce timing risk"
        )
    
    def get_parameters(self) -> Dict[str, Dict[str, Any]]:
        return {
            'symbol': {
                'type': 'string',
                'description': 'Trading pair (e.g., BTCUSDT)',
                'default': 'BTCUSDT'
            },
            'buy_amount': {
                'type': 'float',
                'description': 'Amount in USDT to buy each interval',
                'default': 100.0
            },
            'interval_hours': {
                'type': 'int',
                'description': 'Hours between purchases',
                'default': 24
            },
            'total_purchases': {
                'type': 'int',
                'description': 'Total number of purchases',
                'default': 12
            }
        }
    
    def get_instructions(self) -> str:
        return """
Dollar Cost Averaging Strategy:
1. Set your target symbol and investment amount
2. Bot will place buy orders at fixed intervals
3. Helps reduce impact of price volatility
4. Best for long-term accumulation
5. Automates regular purchases without emotion

Benefits:
- Reduces emotional trading
- Lowers average entry price over time
- Works in both bullish and bearish markets
"""


class GridTradingStrategy(Strategy):
    """Grid Trading Strategy"""
    
    def __init__(self):
        super().__init__(
            name="Grid Trading",
            description="Place buy and sell orders at regular intervals to profit from volatility"
        )
    
    def get_parameters(self) -> Dict[str, Dict[str, Any]]:
        return {
            'symbol': {
                'type': 'string',
                'description': 'Trading pair (e.g., BTCUSDT)',
                'default': 'BTCUSDT'
            },
            'lower_price': {
                'type': 'float',
                'description': 'Lower boundary price',
                'default': 40000
            },
            'upper_price': {
                'type': 'float',
                'description': 'Upper boundary price',
                'default': 50000
            },
            'grid_levels': {
                'type': 'int',
                'description': 'Number of price levels',
                'default': 10
            },
            'quantity_per_level': {
                'type': 'float',
                'description': 'Quantity at each grid level',
                'default': 0.1
            }
        }
    
    def get_instructions(self) -> str:
        return """
Grid Trading Strategy:
1. Define upper and lower price boundaries
2. Bot places buy orders below current price
3. Bot places sell orders above current price
4. Profits from price oscillations between bounds
5. Automates the buy-low, sell-high principle

Benefits:
- Profits from sideways market movement
- Multiple profit-taking opportunities
- Reduced risk through diversification
- Works well in volatile markets
"""


class MomentumStrategy(Strategy):
    """Momentum Trading Strategy"""
    
    def __init__(self):
        super().__init__(
            name="Momentum Trading",
            description="Enter trades when strong price momentum is detected"
        )
    
    def get_parameters(self) -> Dict[str, Dict[str, Any]]:
        return {
            'symbol': {
                'type': 'string',
                'description': 'Trading pair (e.g., BTCUSDT)',
                'default': 'BTCUSDT'
            },
            'momentum_threshold': {
                'type': 'float',
                'description': 'Percentage change to trigger trade',
                'default': 2.0
            },
            'position_size': {
                'type': 'float',
                'description': 'Size of each position',
                'default': 0.5
            },
            'stop_loss_percent': {
                'type': 'float',
                'description': 'Stop loss percentage below entry',
                'default': 2.0
            },
            'take_profit_percent': {
                'type': 'float',
                'description': 'Take profit percentage above entry',
                'default': 5.0
            }
        }
    
    def get_instructions(self) -> str:
        return """
Momentum Trading Strategy:
1. Monitor price changes for momentum signals
2. Enter when price moves significantly
3. Set stop loss and take profit levels
4. Exit on target or stop loss hit
5. Ride the trend while managing risk

Benefits:
- Captures large price moves quickly
- Risk is defined with stop loss
- Works in trending markets
- Can generate quick profits
"""


class StategyTemplateManager:
    """Manage and provide trading strategy templates"""
    
    STRATEGIES = {
        'dca': DCAStrategy(),
        'grid': GridTradingStrategy(),
        'momentum': MomentumStrategy()
    }
    
    @classmethod
    def get_strategy(cls, name: str) -> Optional[Strategy]:
        """
        Get a strategy by name
        
        Args:
            name: Strategy name (lowercase)
            
        Returns:
            Strategy object or None
        """
        strategy = cls.STRATEGIES.get(name.lower())
        if strategy:
            logger.debug(f"Retrieved strategy: {name}")
        else:
            logger.warning(f"Strategy not found: {name}")
        return strategy
    
    @classmethod
    def list_strategies(cls) -> Dict[str, str]:
        """
        List all available strategies
        
        Returns:
            Dictionary of {name: description}
        """
        return {
            name: strategy.description
            for name, strategy in cls.STRATEGIES.items()
        }
    
    @classmethod
    def get_strategy_info(cls, name: str) -> Dict[str, Any]:
        """
        Get detailed information about a strategy
        
        Args:
            name: Strategy name
            
        Returns:
            Strategy details
        """
        strategy = cls.get_strategy(name)
        if not strategy:
            return {}
        
        return {
            'name': strategy.name,
            'description': strategy.description,
            'parameters': strategy.get_parameters(),
            'instructions': strategy.get_instructions()
        }
