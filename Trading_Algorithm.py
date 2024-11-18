import MetaTrader5 as mt
from datetime import datetime
import pandas as pd
import time as time

mt.initialize()

# Below is example usage of inserting login details 

password = "password123"
server = "OANDATMS-MT5"
login = 12345678
mt.login(login, password, server)


# Set the values below before starting

###############################################################################
                                                                              #              
pip_size = 0.0001          # Generally the digit in the 4th decimal place     #
                           # of a price                                       #
                                                                              #                                                                              
increment_size = 20        # Select the pip space in-between orders           #                                                                  
                                                                              #
###############################################################################


# Input is pip amount, output is the pip equivalent in specified currency
def pip(amount):
    money = amount * pip_size
    return round(float(money), 5)

tolerance = pip(increment_size) * 0.05    # Set to 5% as default. Refers to the % error that the price of an order 
                                          # may be within price bounds of a nearby order, i.e. If orders are spaced
                                          # 20 pips, some orders may be within 19 pips of one another

timeframe = mt.TIMEFRAME_M1 
date_from = time.time() - 3600*24*30   # Last 30 days
action = mt.TRADE_ACTION_PENDING
ticker = "GBPCHF.pro"
qty = 0.01
buy_order = mt.ORDER_TYPE_BUY
sell_order = mt.ORDER_TYPE_SELL
buy_stop_order = mt.ORDER_TYPE_BUY_STOP
buy_limit_order = mt.ORDER_TYPE_BUY_LIMIT
sell_stop_order = mt.ORDER_TYPE_SELL_STOP
sell_limit_order = mt.ORDER_TYPE_SELL_LIMIT
b_sl_points = 0.001
b_tp_points = 0.001
buy_price = mt.symbol_info_tick(ticker).ask
sell_price = mt.symbol_info_tick(ticker).bid


tmp = pip_size
i = True
pip_dec = 0


# Finds the decimal place of a single pip for specified currency
while i:
    tmp *= 10
    pip_dec += 1
    if tmp == 1.0:
        i = False
    

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
    if order_type == buy_limit_order:
        order = "buy limit order"
    else:
        order = "buy stop order"

    if result.volume != 0:
        print(f"\nA {order} has been placed at a price of {price}!\n")


def close_order_pending():
    close_stop_order = {
        "action": mt.TRADE_ACTION_REMOVE,
        "order": mt.orders_get()[0].ticket
               }
    mt.order_send(close_stop_order)


def close_all_pending():
    length = len(mt.orders_get())
    for i in range(length):
        close_order_pending()


def calculate_profit(hours):
    # Finds combined profit from closed trades and from 
    # currently open trades over the last {hours} hours

    # MT5 charts are 2 hours ahead of time returned by time.time() function, so
    # a 7200 second offset is added

    from_ = ((time.time() + 7200) - (hours*3600))
    to_ = time.time() + 7200
    total = mt.history_deals_total(from_, to_)
    profit = 0
    for i in range(0,total):
        profit += mt.history_deals_get(from_, to_)[i].profit                 # Closed trades profit
    final_profit = profit + mt.account_info()._asdict()["profit"]            # Closed trades + open trades profit
    print(f"The total profit on this account over the last {hours} hours is {round(final_profit,2)}")


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


def close_all_open():
    for i in range(len(mt.positions_get())):
        close_order(ticker, qty, sell_order, sell_price, 0)

def close_all():
    try:
        while(True):
            close_all_open()
            close_all_pending()
    except:
        pass


def take_profit():
    # Closes all open positions that are at a profit

    length = len(mt.positions_get())
    print(f"\n there are a total of {length} open buy positions\n")
    i = True
    j = 0
    while (i == True):
        try:
            if mt.positions_get()[j].profit > 0:
                close_order(ticker, qty, sell_order, mt.symbol_info_tick(ticker).bid, j)
                print(f"\nOrder {mt.positions_get()[j].ticket} has closed\n")
            else:
                j += 1
        except:
            i = False


def stop_loss():
    # Closes all open positions that are at a loss

    length = len(mt.positions_get())
    print(f"\n there are a total of {length} open BUY positions\n")
    i = True
    j = 0
    while (i == True):
        print(f"Position no. {j}")
        try:
            if mt.positions_get()[j].profit < 0:
                close_order(ticker, qty, sell_order, mt.symbol_info_tick(ticker).bid, j)
                print(f"\nOrder {mt.positions_get()[j].ticket} has closed\n")
            else:
                j += 1
        except:
            i = False


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


def mod_all_tp(amount):
    # Modifies take profit for all open orders

    for pos in mt.positions_get():
        mod_tp(pos.ticket, amount)


def mod_all_sl(amount):
    # Modifies stop loss for all open orders
    for pos in mt.positions_get():
        mod_sl(pos.ticket, amount)


def Trade_Bot():
    while(True):

        # Populates dataframe with pricing history between specified dates
        # and stores it in variable "prices". "current_close" holds the
        # current value of currency.

        date_to = time.time() + 7200
        prices = pd.DataFrame(mt.copy_rates_range(ticker, timeframe, date_from, date_to))
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
                buy_sl = stop_price - b_sl_points
                buy_tp = stop_price + b_tp_points
                result = create_order(action, ticker, qty, buy_stop_order, stop_price, buy_sl, buy_tp)
                # print(result)
                
            if ((not limit_skip1) and (not limit_skip2)):
                buy_sl = limit_price - b_sl_points
                buy_tp = limit_price + b_tp_points
                result = create_order(action, ticker, qty, buy_limit_order, limit_price, buy_sl, buy_tp)
                # print(result)

        # time.sleep(1)

        # time.sleep(1) and print(result) used for debugging code


# List of useful functions below:

######################

#mod_all_tp(0.95340)
#mod_all_sl(0.5)

#calculate_profit()
#take_profit()
#stop_loss()
#close_all()


######################

# Turn on trading bot
Trade_Bot()


