import MetaTrader5 as mt
import config as c

import time as time
import pandas as pd
import math as math

# Input is pip amount, output is the pip equivalent in specified currency

def pip(amount):
    money = amount * c.pip_size
    return round(float(money), 5)

increment_size = c.increment_size
tolerance = pip(increment_size) * (c.tol_percent / 100)


def create_order(action, ticker, qty, order_type, price, sl, tp):
    request ={
        "action" : action,
        "symbol" : ticker,
        "price" : price,
        "sl" : sl,
        "tp" : tp,
        "type" : order_type,
        "volume" : qty,
        "type_time" : mt.ORDER_TIME_GTC,
        "type_filling" : mt.ORDER_FILLING_IOC,
        "magic" : 5678,
        "comment" : "Open python position"
}
    result = mt.order_send(request)
    if order_type == c.buy_limit_order:
        order = "buy limit order"
    else:
        order = "buy stop order"

    if result.volume != 0:
        print(f"\nA {order} has been placed at a price of {price}!\n")



def close_order(ticker, qty, order_type, price, index):
    close_req = {
        "action" : mt.TRADE_ACTION_DEAL,
        "symbol" : ticker,
        "price" : price,
        "type" : order_type,
        "volume" : qty,
        "type_time" : mt.ORDER_TIME_GTC,
        "type_filling" : mt.ORDER_FILLING_FOK,
        "comment" : "close python position",
        "position" : mt.positions_get()[index].ticket
    }
    mt.order_send(close_req)



def close_order_pending():
    close_stop_order = {
        "action": mt.TRADE_ACTION_REMOVE,
        "order": mt.orders_get()[0].ticket
               }
    mt.order_send(close_stop_order)



def mod_sl(position, amount):
        # Modifies stop loss of a position

        for pos in mt.positions_get():
            if pos.ticket == position:
                tp = pos.tp
        mod_sl = {
            "action" : mt.TRADE_ACTION_SLTP,
            "position" : position,
            "sl" : amount,
            "tp" : tp
                }
        mt.order_send(mod_sl)



def mod_tp(position, amount):
    # Modifies take profit of a position

    for pos in mt.positions_get():
            if pos.ticket == position:
                sl = pos.sl
    mod_tp = {
        "action" : mt.TRADE_ACTION_SLTP,
        "position" : position,
        "sl" : sl,
        "tp" : amount
            }
    mt.order_send(mod_tp)



def Trade_Bot():

    # Finds the decimal place of a single pip for specified currency

    tmp = c.pip_size
    pip_dec = 0

    while(True):
        tmp *= 10
        pip_dec += 1
        if tmp == 1.0:
            break


    while(True):

        # Populates dataframe with pricing history between specified dates
        # and stores it in variable "prices". "current_close" holds the
        # current value of currency.

        date_from = time.time() + 7200 - 3600*24*30   # Last 30 days
        date_to = time.time() + 7200                  # MT5 is 2 hours behind
        prices = pd.DataFrame(mt.copy_rates_range(c.ticker, c.timeframe, date_from, date_to))
        prices["time"] = pd.to_datetime(prices["time"], unit = "s")
        current_close = list(prices[-1:]["close"])[0]

        # For-loop specifies how many orders to place above and below current price

        for j in range(10):
            stop_skip1 = False
            stop_skip2 = False
            limit_skip1 = False
            limit_skip2 = False

            # Rounds current price to nearest pip and stores in "rounded_close"

            rounded_close = math.ceil(current_close * (10.0 ** pip_dec)) / (10.0 ** pip_dec)
            stop_price = rounded_close + pip(increment_size) * j
            stop_price = round(stop_price, pip_dec)
            limit_price = rounded_close - pip(increment_size) * j
            limit_price = round(limit_price, pip_dec)

            # Ensures pending orders are not placed within a specified range of one another
            
            for k in range(len(mt.orders_get())):
                try:
                    opening_price = mt.orders_get()[k].price_open
                except:
                    print("No pending buy orders (Tuple index out of range)")
                
                opening_price = round(opening_price, 4)

                if ((opening_price < stop_price + (pip(increment_size) - tolerance) ) and (opening_price > stop_price - (pip(increment_size) - tolerance) )):
                    stop_skip1 = True
                if ((opening_price < limit_price + (pip(increment_size) - tolerance) ) and (opening_price > limit_price - (pip(increment_size) - tolerance) )):
                    limit_skip1 = True


            # Ensures pending orders are not placed within a specified range of currently open positions

            for z in range(len(mt.positions_get())):
                try:
                    position_price = mt.positions_get()[z].price_open
                except:
                    print("No pending buy positions (Tuple index out of range)")

                if ((position_price < stop_price + (pip(increment_size) - tolerance) ) and (position_price > stop_price - (pip(increment_size) - tolerance) )):
                    stop_skip2 = True
                    
                if ((position_price < limit_price + (pip(increment_size) - tolerance) ) and (position_price > limit_price - (pip(increment_size) - tolerance) )):
                    limit_skip2 = True 
                    
                

            if ((not stop_skip1) and (not stop_skip2)):
                buy_sl = stop_price - c.b_sl_points
                buy_tp = stop_price + c.b_tp_points
                result = create_order(c.action, c.ticker, c.qty, c.buy_stop_order, stop_price, buy_sl, buy_tp)
                #print(result)
                
            if ((not limit_skip1) and (not limit_skip2)):
                buy_sl = limit_price - c.b_sl_points
                buy_tp = limit_price + c.b_tp_points
                result = create_order(c.action, c.ticker, c.qty, c.buy_limit_order, limit_price, buy_sl, buy_tp)
                #print(result)

        #time.sleep(1)

        # time.sleep(1) and print(result) used for debugging code

