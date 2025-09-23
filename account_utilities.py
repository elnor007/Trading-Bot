import MetaTrader5 as mt
import time as time
import config as c
import trading_utilities as tu



def close_all_pending():
    length = len(mt.orders_get())
    for i in range(length):
        tu.close_order_pending()



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
        profit += mt.history_deals_get(from_, to_)[i].profit # Closed trades profit
    final_profit = profit + mt.account_info()._asdict()["profit"] # Close trades + open trades profit
    print(f"The total profit on this account over the last {hours} hours is {round(final_profit,2)}")



def close_all_open():
    for i in range(len(mt.positions_get())):
        tu.close_order(c.ticker, c.qty, c.sell_order, c.sell_price, 0)



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
                tu.close_order(c.ticker, c.qty, c.sell_order, mt.symbol_info_tick(c.ticker).bid, j)
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
                tu.close_order(c.ticker, c.qty, c.sell_order, mt.symbol_info_tick(c.ticker).bid, j)
                print(f"\nOrder {mt.positions_get()[j].ticket} has closed\n")
            else:
                j += 1
        except:
            i = False



def mod_all_tp(amount):
    # Modifies take profit for all open orders
    for pos in mt.positions_get():
        tu.mod_tp(pos.ticket, amount)



def mod_all_sl(amount):
    # Modifies stop loss for all open orders
    for pos in mt.positions_get():
        tu.mod_sl(pos.ticket, amount)