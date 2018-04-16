"""
Short algo that basically just takes advantage of the beta decay, or slippage, from a couple of 3x leveraged etfs. The 2 stocks it's
trading here are JNUG and JDST, however, this could be used with any 3x or 2x pair where both gradually lose value over time. 
The algo shorts an equal amount of your portfolio (25%) of both the stocks and rebalances every day. 
It also accounts for commission, here it uses the commission of Interactive Brokers. 
"""
def initialize(context):
    context.stocks = [sid(45570),sid(45571)]
    set_commission(commission.PerShare(cost=0.014, min_trade_cost=1.4))
    schedule_function(my_rebalance, date_rules.every_day(), time_rules.market_open(hours=1))
    schedule_function(record_vars, date_rules.every_day(), time_rules.market_open(minutes=90))

def my_rebalance(context,data):
    try:
        for stock in context.stocks:
            if stock == sid(45570):
                order_target_percent(stock, -0.25)
            elif stock == sid(45571):
                order_target_percent(stock, -0.25)
    except Exception as e:
        print(str(e))

def record_vars(context,data):
    #record(JNUG=context.portfolio.positions[sid(45570)].amount*data.current(sid(45570),'price'),JDST=context.portfolio.positions[sid(45571)].amount*data.current(sid(45571))
    record(Leverage=context.account.leverage)
