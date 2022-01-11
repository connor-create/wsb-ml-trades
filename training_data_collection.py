import database
import alpaca_api
import time
from datetime import datetime
from datetime import timedelta
from dateutil import tz
import wsb_reddit
import wsb_post

db = database.Database()
alpaca = alpaca_api.Alpaca()

def calculateIfWinner(trades, beginPrice, winPrice, losePrice):
    """ 
    Takes input values and trades list to calculate if a trade would be a winner or not
    :param trades: list of trades over timeframe
    :param beginPrice: start price of trade period
    :param winPrice: price at which a trade is considered a win in period
    :param losePrice: price at which a trade is considered a loss in period
    :type trades: list of trades
    :type beginPrice: float
    :type winPrice: float
    :type losePrice: float
    :return: bool representing win status
    :rtype: bool
    """
    for trade in trades:
        if float(trade.p) >= winPrice:
            return True
        elif float(trade.p) <= losePrice:
            return False
    if float(trades[-1].p) > beginPrice:
        return True
    else:
        return False

def get_tenMinuteWinner(ticker, postDateTime):
    """
    Gathers trades for the ticker after the postDateTime and calculates whether it's a winning trade/article or not
    :param ticker: stock ticker to process
    :param postDateTime: beginning datetime formatted by dd/mm/yyyy hh:mm (inclusive)
    :type ticker: str
    :type postDateTime: str
    :return: bool representing win status
    :rtype: bool
    """
    startTime = datetime.strptime(postDateTime, "%d/%m/%Y %H:%M")
    endTime = startTime + timedelta(minutes=10)

    # Get the trades for this section
    trades = alpaca.get_trades_by_time(ticker, startTime.strftime("%d/%m/%Y %H:%M"), endTime.strftime("%d/%m/%Y %H:%M"))
    if len(trades) < 3:
        return False

    # Calculate our win condition
    beginPrice = float(trades[0].p)
    winPrice = beginPrice + (beginPrice * .01)
    losePrice = beginPrice - (beginPrice * .01)

    # Calculate if it's a winner or not by iterating over our trades
    return calculateIfWinner(trades, beginPrice, winPrice, losePrice)

def get_thirtyMinuteWinner(ticker, postDateTime):
    """
    Gathers trades for the ticker after the postDateTime and calculates whether it's a winning trade/article or not
    :param ticker: stock ticker to process
    :param postDateTime: beginning datetime formatted by dd/mm/yyyy hh:mm (inclusive)
    :type ticker: str
    :type postDateTime: str
    :return: bool representing win status
    :rtype: bool
    """
    startTime = datetime.strptime(postDateTime, "%d/%m/%Y %H:%M")
    endTime = startTime + timedelta(minutes=30)

    # Get the trades for this section
    trades = alpaca.get_trades_by_time(ticker, startTime.strftime("%d/%m/%Y %H:%M"), endTime.strftime("%d/%m/%Y %H:%M"))
    if len(trades) < 3:
        return False

    # Calculate our win condition
    beginPrice = float(trades[0].p)
    winPrice = beginPrice + (beginPrice * .01)
    losePrice = beginPrice - (beginPrice * .01)

    # Calculate if it's a winner or not by iterating over our trades
    return calculateIfWinner(trades, beginPrice, winPrice, losePrice)

def get_oneHourWinner(ticker, postDateTime):
    """
    Gathers trades for the ticker after the postDateTime and calculates whether it's a winning trade/article or not
    :param ticker: stock ticker to process
    :param postDateTime: beginning datetime formatted by dd/mm/yyyy hh:mm (inclusive)
    :type ticker: str
    :type postDateTime: str
    :return: bool representing win status
    :rtype: bool
    """
    startTime = datetime.strptime(postDateTime, "%d/%m/%Y %H:%M")
    endTime = startTime + timedelta(minutes=60)

    # Get the trades for this section
    trades = alpaca.get_trades_by_time(ticker, startTime.strftime("%d/%m/%Y %H:%M"), endTime.strftime("%d/%m/%Y %H:%M"))
    if len(trades) < 3:
        return False

    # Calculate our win condition
    beginPrice = float(trades[0].p)
    winPrice = beginPrice + (beginPrice * .01)
    losePrice = beginPrice - (beginPrice * .01)

    # Calculate if it's a winner or not by iterating over our trades
    return calculateIfWinner(trades, beginPrice, winPrice, losePrice)


def collect_daily_data():
    """
    Will collect, process, and store data for the given ticker and day in database
    :param ticker: stock ticker to process
    :return: none
    """
    days = alpaca.get_all_trading_days('01/11/2021', '1/1/2022')
    if not len(days):
        print('No trading days in this range.')
        return
    for dayDate in days:
        print(dayDate)
        for submission in wsb_reddit.get_wsb_posts_for_day(dayDate):
            print(submission.score)
            tickers = wsb_reddit.get_tickers_from_title(submission.title)
            for ticker in tickers:
                p = wsb_post.WSBPost()
                p.postId = submission.id
                p.ticker = ticker.upper()
                p.title = submission.title
                p.title = p.title.replace("\'", "")
                p.title = p.title.replace("\"", "")
                p.description = submission.selftext
                p.description = p.description.replace("\'", "")
                p.description = p.description.replace("\"", "")
                p.postTime = submission.created_utc

                # Check for winners
                adjustedDatetime = datetime.fromtimestamp(p.postTime)
                adjustedDatetime.replace(tzinfo=tz.tzutc())
                adjustedDatetime = adjustedDatetime.astimezone(tz.gettz('America/New_York'))

                # See what timeframes are valid
                valid_timeframes = wsb_reddit.get_tradeable_periods(adjustedDatetime.timestamp())
                if valid_timeframes["10min"]:
                    p.tenMinuteWinner = get_tenMinuteWinner(ticker, adjustedDatetime.strftime('%d/%m/%Y %H:%M'))
                if valid_timeframes["30min"]:
                    p.thirtyMinuteWinner = get_thirtyMinuteWinner(ticker, adjustedDatetime.strftime('%d/%m/%Y %H:%M'))
                if valid_timeframes["1hour"]:
                    p.oneHourWinner = get_oneHourWinner(ticker, adjustedDatetime.strftime('%d/%m/%Y %H:%M'))

                # Save this to the database
                if valid_timeframes["1hour"] or valid_timeframes["30min"] or valid_timeframes["10min"]:
                    print(ticker, p.tenMinuteWinner, p.thirtyMinuteWinner, p.oneHourWinner)
                    print("Saved")
                    db.add_post_record(p)
        time.sleep(.2)

collect_daily_data()