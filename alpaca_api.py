from math import floor
import alpaca_trade_api as tradeapi
import os
from datetime import datetime, timedelta
import pytz
import config

os.environ['APCA_API_BASE_URL'] = "https://paper-api.alpaca.markets"
os.environ['APCA_API_KEY_ID'] = config.alpacaKey
os.environ['APCA_API_SECRET_KEY'] = config.alpacaSecretKey


class Alpaca:
    def __init__(self):
        self.api = tradeapi.REST()
        self.forbiddenTickers = ["OF", "FOR", "A", "YOLO", "ALL", "IS", "TRUE", "ON", "AM", "DD", "YOU", "SUB", "U"]

    def get_api(self):
        return self.api

    def get_refined_ticker_list(self):
        """
        Used to get a list of all assets that this api can trade minus those in the forbiddenTickers
        :return: List of tickers that are tradeable
        :rtype: list of str
        """
        try:
            assetList = self.api.list_assets(status='active')
        except Exception as e:
            print(e)
            return []
        refinedAssetList = []
        for asset in assetList:
            if asset.easy_to_borrow and asset.symbol not in self.forbiddenTickers:
                refinedAssetList.append(asset.symbol)
        return refinedAssetList

    def get_open_positions(self):
        """
        Gets open positions
        :return: list of positons
        :rtype: list
        """
        try:
            return self.api.list_positions()
        except Exception as e:
            print(e)
            return False

    def close_position(self, symbol):
        """
        Closes positon
        :param symbol: symbol of position to close
        :type symbol: str
        """
        try:
            # First, cancel any existing orders so they don't impact our buying power.
            orders = self.api.list_orders(status="open")
            for order in orders:
                self.api.cancel_order(order.id)

            positions = self.api.list_positions()
            for position in positions:
                if position.side == 'long':
                    orderSide = 'sell'
                else:
                    orderSide = 'buy'
                qty = abs(float(position.qty))
                try:
                    self.api.submit_order(position.symbol, qty, orderSide, "market", "day")
                except Exception as e:
                    print(f"Could not close positon {position.symbol} {qty} {e}")
        except Exception as e:
            print(e)
            return False

    def get_market_open(self):
        """
        Used to see if market is open and tradeable or not
        :return: Bool if trades can be places
        :rtype: bool
        """
        try:
            return self.api.get_clock().is_open
        except Exception as e:
            print(e)
            return False

    def get_account(self):
        """
        Gives alpaca account
        :return: Alpaca account
        :rtype: alpaca account
        """
        try:
            return self.api.get_account()
        except Exception as e:
            print(e)
            return None

    def submit_market_buy_order(self, ticker):
        # Calculate the amount we have to buy
        try:
            price = self.api.get_last_trade(ticker).price
            buyingPower = 5000 # self.api.get_account().buying_power
            moneyToUse = float(buyingPower)
            qtyToBuy = moneyToUse / price
        except Exception as e:
            print(e)
            return

        try:
            self.api.submit_order(symbol=ticker,
                                qty=round(qtyToBuy, 2),
                                side='buy',
                                type='market',
                                time_in_force='day',
                                )
        except Exception as e:
            print(e)

    def submit_market_short_order(self, ticker):
        # Calculate the amount we have to buy
        try:
            price = self.api.get_last_trade(ticker).price
            buyingPower = 5000 # self.api.get_account().buying_power
            moneyToUse = float(buyingPower)
            qtyToBuy = floor(moneyToUse / price)
        except Exception as e:
            print(e)
            return

        try:
            self.api.submit_order(symbol=ticker,
                                qty=round(qtyToBuy, 2),
                                side='sell',
                                type='market',
                                time_in_force='day',
                                )
        except Exception as e:
            print(e)

    
    def submit_market_buy_to_close_order(self, ticker, qty):
        try:
            self.api.submit_order(symbol=ticker,
                                qty=round(qty, 2),
                                side='buy',
                                type='market',
                                time_in_force='day',
                                )
        except Exception as e:
            print(e)

    def submit_market_sell_order(self, ticker, qty):
        try:
            self.api.submit_order(symbol=ticker,
                                qty=round(qty, 2),
                                side='sell',
                                type='market',
                                time_in_force='day',
                                )
        except Exception as e:
            print(e)

    # def generate_during_trading_hour_times(dateString):
    #     validTimes = []
    #     hour = 4
    #     minute = 0
    #     for tick in range(0, 60 * 8 - 30):
    #         timeString = 'yyyy-MM-dd hh:mm:00-05:00'
    #         timeString = timeString.replace('yyyy-MM-dd', dateString)
    #
    #         if minute != 0 and minute % 60 == 0:
    #             minute = 0
    #             hour += 1
    #             if hour > 12:
    #                 hour = 1
    #         minString = str(minute)
    #         hourString = str(hour)
    #         if len(minString) == 1:
    #             minString = '0' + minString
    #         if len(hourString) == 1:
    #             hourString = '0' + hourString
    #         validTimes.append(timeString.replace('mm', minString).replace('hh', hourString))
    #         minute += 1
    #     return validTimes

    def get_all_trading_days(self, startDate, endDate):
        """
        Used to get a vector of all trading days between two dates (both inclusive)
        :param startDate: beginning date formatted by dd/mm/yyyy (inclusive)
        :param endDate: end date formatted by dd/mm/yyyy (inclusive)
        :type startDate: str
        :type endDate:str
        :return: A vector of dates formatted by dd/mm/yyyy
        :rtype: list of str
        """
        startDate = datetime.strptime(startDate, "%d/%m/%Y")
        endDate = datetime.strptime(endDate, "%d/%m/%Y")

        startDateWithTimeZone = startDate.replace(tzinfo=pytz.UTC)
        endDateWithTimeZone = endDate.replace(tzinfo=pytz.UTC)

        try:
            response = self.api.get_calendar(startDateWithTimeZone.isoformat(), endDateWithTimeZone.isoformat())
            datesList = []
            for r in response:
                day = datetime.strptime(str(r.date), '%Y-%m-%d %H:%M:%S')
                datesList.append(day.strftime('%d/%m/%Y'))
            return datesList
        except Exception as e:
            print(e)
            return []

    def get_minute_bars_by_time(self, ticker, strStartTime, strEndTime):
        """
        Used to get a list of all bars betweem two datetimes
        :param ticker: the ticker to get the bars for
        :param strStartTime: beginning datetime formatted by dd/mm/yyyy hh:mm (inclusive)
        :param strEndTime: end date formatted by dd/mm/yyyy hh:mm (inclusive)
        :type ticker: str
        :type strStartTime: str
        :type strEndTime:str
        :return: A list of alpaca bars
        :rtype: list of bars
        """
        try:
            startTime = datetime.strptime(strStartTime, "%d/%m/%Y %H:%M")
            endTime = datetime.strptime(strEndTime, "%d/%m/%Y %H:%M")
        except Exception as e:
            print(e, ':: date could not be converted from input values')
            return {}

        try:
            bars = self.api.get_bars(symbol=ticker,
                                     timeframe=tradeapi.rest.TimeFrame.Minute,
                                     start=startTime.isoformat('T') + 'Z',
                                     end=endTime.isoformat('T') + 'Z',
                                     adjustment='raw')
            return bars
        except Exception as e:
            print(e)
            return {}

    def get_trades_by_time(self, ticker, strStartTime, strEndTime):
        """
        Used to get a list of all trades by avoiding large message limit (I think 10k trades per call)
        :param ticker: the ticker to get the trades for
        :param strStartTime: beginning datetime formatted by dd/mm/yyyy hh:mm (inclusive)
        :param strEndTime: end date formatted by dd/mm/yyyy hh:mm (inclusive)
        :type ticker: str
        :type strStartTime: str
        :type strEndTime:str
        :return: A list of alpaca trades
        :rtype: list of trades
        """
        try:
            startTime = datetime.strptime(strStartTime, "%d/%m/%Y %H:%M")
            totalEndTime = datetime.strptime(strEndTime, "%d/%m/%Y %H:%M")
        except Exception as e:
            print(e, ':: date could not be converted from input values')
            return {}

        try:
            trades = []
            endTime = startTime + timedelta(minutes=10)
            while endTime < totalEndTime:
                for trade in self.api.get_trades(symbol=ticker,
                                            start=startTime.isoformat('T') + 'Z',
                                            end=endTime.isoformat('T') + 'Z',
                                            limit=30000):
                    trades.append(trade)
                startTime = endTime
                endTime = startTime + timedelta(minutes=10)
                
            return trades
        except Exception as e:
            print(e)
            return {}