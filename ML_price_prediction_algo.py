"""
This algo will no longer work on Quantopian as they have removed the get_fundamentals function from their backend
"""

from quantopian.algorithm import attach_pipeline, pipeline_output
from quantopian.pipeline import Pipeline
from quantopian.pipeline.data.builtin import USEquityPricing
from quantopian.pipeline.factors import AverageDollarVolume
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC, LinearSVC, NuSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import SGDClassifier
from sklearn import preprocessing
from collections import Counter
import numpy as np
import math
import pandas as pd
import statsmodels.api as sm

def initialize(context):

    context.security = symbol('SPY')
    context.historical_bars = 100
    context.feature_window = 10
    context.limit = 10

    schedule_function(rebalance, date_rule=date_rules.every_day())

def before_trading_start(context, data):
    fundamental_df = get_fundamentals(
        query(
            fundamentals.valuation_ratios.pe_ratio,
            fundamentals.valuation_ratios.peg_ratio,
            fundamentals.asset_classification.financial_health_grade,
            fundamentals.asset_classification.morningstar_sector_code)
            .filter(fundamentals.asset_classification.morningstar_sector_code == 207 or fundamentals.asset_classification.morningstar_industry_code == 20534083 or fundamentals.asset_classification.morningstar_industry_group_code == 10320)
            .order_by(fundamentals.valuation_ratios.pe_ratio.desc()).limit(10)
    )
    context.stocks = [stock for stock in fundamental_df]
    context.fundamental_df = fundamental_df[context.stocks]
def rebalance(context,data):
    for stock in context.portfolio.positions:
        if stock not in context.fundamental_df and context.portfolio.positions[stock].amount > 0:
            order_target_percent(stock, 0)
    prices = data.history(context.stocks, fields = 'price', bar_count = context.historical_bars, frequency = '1d')
    this = data.history(context.security, fields = 'price', bar_count = context.historical_bars, frequency = '1d')
    that = data.history(context.security, fields = 'price', bar_count = 2, frequency = '1d')
    for stock in context.stocks:
        try:
            price_hist1 = data.history(stock, 'price', 25, '1d')
            ma1 = price_hist1.mean()
            price_hist2 = data.history(stock, 'price', 200, '1d')
            ma2 = price_hist2.mean()
            p = data.history(stock, 'price', 2, '1d')
            p_list = p.tolist()
            p_e = p_list[(1)]
            p_b = p_list[(0)]
            that_list = that.tolist();
            that_e = that_list[(1)]
            that_b = that_list[(0)]
            take1 = (((p_e-p_b)/p_b)*100) + 0.50
            take2 = (((that_e-that_b)/that_b)*100) + 0.50
            toke = take1/take2
            
            price_list = prices[stock].tolist()
            this_list = this.tolist()

            x = []
            y = []

            for j in range(0, context.historical_bars-1):
                try:
                    end_price = price_list[j+1]
                    begin_price = price_list[j]
                    this_end = this_list[j+1]
                    this_begin = this_list[j]

                    s = (((end_price-begin_price)/begin_price)*100) + 0.50
                    t = (((this_end-this_begin)/this_begin)*100) + 0.50
                    totes = s/t
                    if totes <= 0.3 and totes >= -0.3:
                        label = 1
                    else:
                        label = -1

                    x.append(totes)
                    y.append(label)

                except Exception as e:
                    print(('feature creation', str(e)))

            clf3 = SGDClassifier()
            clf4 = LogisticRegression()

            x = preprocessing.scale(x)
            
            clf3.fit(x.reshape(len(x), 1), y)
            clf4.fit(x.reshape(len(x), 1), y)

            p3 = clf3.predict(toke)[0]
            p4 = clf4.predict(toke)[0]

            if p3 == 1 or p4 == 1:
                p = 1
            elif p3 == -1 and p4 == -1:
                p = -1
            else:
                p = 0

            print(('Prediction', p))

            try:
                if p == 1 and ma1 > ma2:
                    #(ma1 > ma2 or context.fundamentals_df[stock]['peg_ratio'] > 0.5)
                    order_target_percent(stock, 0.02)

                elif p == -1 and ma1 < ma2:
                    order_target_percent(stock, -0.02)
            except Exception as d:
                print(str(d))
        except Exception as e:
            print(str(e))
