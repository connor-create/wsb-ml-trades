import alpaca_api
import time
from datetime import datetime

alpaca = alpaca_api.Alpaca()

pos_times = {}

while True:
    for position in alpaca.get_open_positions():
        if position.symbol not in pos_times.keys():
            pos_times[position.symbol] = datetime.now().timestamp()
        else:
            start_time = pos_times[position.symbol]
            if (datetime.now().timestamp() - start_time) > 3600:
                print("Closing on time", position)
                alpaca.close_position(position.symbol)
                pos_times.pop(position.symbol, None)
        if float(position.unrealized_pl) > 50 or float(position.unrealized_pl) < -50:
            print("Closing on pl", position)
            alpaca.close_position(position.symbol)
            pos_times.pop(position.symbol, None)
    time.sleep(2)



