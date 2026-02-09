# Quick Reference Guide - New Features

## 📊 What's New?

Four powerful new modules have been added to enhance the trading bot:

---

## 1️⃣ Order History (`order_history.py`)

**What it does:** Tracks all your trades in a JSON file for future analysis.

**Quick Start:**
```python
from trading_bot.order_history import OrderHistoryManager

manager = OrderHistoryManager()
# Automatically saves to: data/order_history.json
```

**Key Methods:**
- `add_order(order)` - Save order to history
- `get_order_history()` - Retrieve all orders
- `get_statistics()` - Overall stats
- `get_symbol_statistics('BTCUSDT')` - Per-symbol stats

---

## 2️⃣ Portfolio Analytics (`analytics.py`)

**What it does:** Calculate profits, losses, and trading performance.

**Quick Start:**
```python
from trading_bot.analytics import PortfolioAnalytics

portfolio = PortfolioAnalytics()
portfolio.add_trade('BTCUSDT', 'BUY', 0.5, 42000)

# Calculate P&L
pnl = portfolio.calculate_pnl({'BTCUSDT': 43000})
```

**Key Metrics:**
- Profit & Loss (realized & unrealized)
- P&L percentage
- Win rate
- Profit factor
- Average trade size

---

## 3️⃣ Trading Strategies (`strategies.py`)

**What it does:** Provides ready-to-use trading strategy templates.

**Available Strategies:**

| Strategy | Best For | Key Params |
|----------|----------|-----------|
| **DCA** | Long-term accumulation | Buy amount, interval, count |
| **Grid** | Sideways markets | Price bounds, grid levels |
| **Momentum** | Trending markets | Entry %, stop loss, target |

**Quick Start:**
```python
from trading_bot.strategies import StategyTemplateManager

manager = StategyTemplateManager()
strategy = manager.get_strategy('dca')  # or 'grid', 'momentum'

# Get parameters and instructions
params = strategy.get_parameters()
instructions = strategy.get_instructions()
```

---

## 4️⃣ Error Handling (`error_handling.py`)

**What it does:** Automatically retries failed API calls and tracks errors.

**Quick Start:**
```python
from trading_bot.error_handling import retry, recovery_manager

# Auto-retry decorator
@retry(max_retries=3, backoff_factor=2.0)
def risky_operation():
    return api_call()

# Track errors
recovery_manager.log_error('api_timeout')
if recovery_manager.is_error_spike('api_error', threshold=10):
    print("Too many errors!")
```

**Features:**
- Automatic retry with exponential backoff
- Circuit breaker to prevent cascading failures
- Error spike detection
- Error summary and tracking

---

## 📦 Integration Points

All new features are **automatically integrated** into the bot:

```python
# In bot.py initialization
self.order_history = OrderHistoryManager()      # Auto-tracking
self.portfolio = PortfolioAnalytics()           # Auto-analytics

# All methods use @retry decorator
@retry(max_retries=3)
def place_market_order(...):  # Auto-retry on failure
    ...
```

---

## 📈 Usage in Main Bot

```python
from trading_bot.bot import BasicBot
from trading_bot.order_history import OrderHistoryManager
from trading_bot.analytics import PortfolioAnalytics
from trading_bot.strategies import StategyTemplateManager

# Initialize bot (with new features)
bot = BasicBot(api_key, api_secret)

# Place order (auto-tracked + auto-retried)
order = bot.place_market_order('BTCUSDT', 'BUY', 0.5)

# View history
history = bot.order_history.get_order_history()

# View stats
stats = bot.order_history.get_statistics()
print(f"Total trades: {stats['total_orders']}")

# Calculate P&L
pnl = bot.portfolio.calculate_pnl({'BTCUSDT': 43000})

# Get strategies
manager = StategyTemplateManager()
dca = manager.get_strategy('dca')
```

---

## 📁 New Files Created

```
trading_bot/
  ├── order_history.py      ✨ NEW - Order tracking
  ├── analytics.py           ✨ NEW - Performance metrics
  ├── strategies.py          ✨ NEW - Strategy templates
  ├── error_handling.py      ✨ NEW - Error recovery
  └── bot.py               ✏️  UPDATED - Integration

data/
  └── order_history.json    📊 Auto-created - Order data
```

---

## 🎯 Key Benefits

| Benefit | Module | Impact |
|---------|--------|--------|
| Never lose trade history | `order_history` | Analyze past performance |
| Know your P&L | `analytics` | Track profitability |
| Quick strategy setup | `strategies` | Reduce decision time |
| Automatic retries | `error_handling` | Fewer failed trades |
| Error tracking | `error_handling` | Better debugging |

---

## 💡 Example Workflows

### Track Daily Performance
```python
history = bot.order_history.get_statistics()
print(f"Today's trades: {history['total_orders']}")
print(f"Total quantity: {history['total_quantity_traded']}")
```

### Monitor Portfolio
```python
prices = get_current_prices()  # {'BTCUSDT': 43500, ...}
pnl = bot.portfolio.calculate_pnl(prices)
print(f"Total P&L: ${pnl['total']['total_pnl']}")
print(f"Return: {pnl['total']['pnl_percentage']}%")
```

### Choose a Strategy
```python
manager = StategyTemplateManager()
strategies = manager.list_strategies()
for name, desc in strategies.items():
    print(f"{name}: {desc}")

# Get DCA strategy details
dca_info = manager.get_strategy_info('dca')
print(dca_info['instructions'])
```

### Implement Strategy with Retry
```python
@retry(max_retries=5)
def execute_dca_buy():
    return bot.place_market_order('BTCUSDT', 'BUY', 0.1)

# Will automatically retry if network error
execute_dca_buy()
```

---

## ⚙️ Configuration

No configuration needed! All features:
- Work out of the box
- Use sensible defaults
- Are fully customizable

**Example Customizations:**
```python
# Custom retry policy
from trading_bot.error_handling import RetryPolicy
policy = RetryPolicy(max_retries=5, backoff_factor=3.0)

# Custom data file location
from trading_bot.order_history import OrderHistoryManager
history = OrderHistoryManager(history_file='custom/path/history.json')
```

---

## 🔍 Monitoring

Check the status of your bot:

```python
from trading_bot.error_handling import recovery_manager

# Get error summary
errors = recovery_manager.get_error_summary()
print(f"API errors: {errors.get('api_error', 0)}")

# Check for spikes
if recovery_manager.is_error_spike('api_timeout', threshold=5):
    print("Warning: API timeout spike detected!")
```

---

## 📊 Data Persistence

Order history is automatically saved to `data/order_history.json`:

```json
[
  {
    "timestamp": "2024-02-10T10:30:45",
    "order_id": 12345,
    "symbol": "BTCUSDT",
    "side": "BUY",
    "quantity": 0.5,
    "price": 42000,
    "status": "FILLED"
  }
]
```

---

## 🚀 Next Steps

1. **Start Trading** - Use the bot normally, new features work automatically
2. **Monitor History** - Check `data/order_history.json` for trade records
3. **Review Performance** - Use analytics to understand your trading
4. **Choose Strategy** - Pick a template for your next trading campaign
5. **Handle Errors** - Benefit from automatic retries and error tracking

---

## 📚 Full Documentation

For detailed information, see [ENHANCEMENTS.md](ENHANCEMENTS.md)

---

**Status:** ✅ Ready to use  
**Compatibility:** ✅ Backward compatible  
**Testing:** ✅ Production ready
