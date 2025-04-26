import MetaTrader5 as mt
import time as time
from account_utilities import pip


# Enter account details below

password = "password123"
server = "OANDATMS-MT5"
login = 12345678



# Set the values below before starting

###############################################################################
                                                                                            
pip_size = 0.0001           # Generally the digit in the 4th decimal place     
                            # of a price                                       
                                                                                                                                                            
increment_size = 20         # Select the pip space in-between orders                                                                           
                                                                            

tol_percent = 5             # Set to 5% as default. Refers to the % error of pip spacing tolerated between orders.
                            # i.e. If orders are spaced 20 pips, then all orders will be spaced at a minimum of 19 
                            # pips apart. If the tolerance is too strict, the program may struggle to fill in "gaps" or
                            # spaces between orders, and if it is too loose, then orders might be placed too close
                            # to one another.

###############################################################################


timeframe = mt.TIMEFRAME_M1 
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


