# Trading Bot - Overview

Developed a trading bot using the MetaTrader5 Python API. The algorithm aims to place pending orders which are equally spaced from one another and also ensures that each order is placed at a unique price point. The amount of space between orders can be set at the start of the code.

Also contains many useful functions which automate tedious manual tasks, such as: Closing all the trades, calculating total profit made over x amount of hours, modifying the take profit/stop loss of all open trades, and many more.

In order to run this, you must download the MetaTrader5 application and the MT5 python library. You also need a stock exchange account compatible with MT5 (I used OANDA). I will soon upload a video to showcase what this code does.

<br>

## Before activation
<img width="2558" height="769" alt="Screenshot 2025-09-23 175814" src="https://github.com/user-attachments/assets/e86e0f80-5df8-4c92-a0a6-e612410fe403" />

The trade window is blank - no orders have been placed yet

<br><br>

## After activation
<img width="2558" height="768" alt="Screenshot 2025-09-23 175655" src="https://github.com/user-attachments/assets/e48a9892-3d5f-4cda-b7b9-8b0dae6b13ef" />

Immediately, the trade bot executes several orders per second, filling the screen with orders. Each green line indicates a seperate pending order, while each red line corresponds to either a take profit or stop loss of each pending order. The bot continues to place orders as the price goes up or down, or if a large enough gap appears in-between orders.
