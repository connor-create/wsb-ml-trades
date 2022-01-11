from datetime import datetime
from dateutil import tz
import datetime as dt

import praw
from psaw import PushshiftAPI

import alpaca_api

r = praw.Reddit(
    client_id="",
    client_secret="",
    password="",
    user_agent="",
    username="",
)
api = PushshiftAPI(r)

alpaca = alpaca_api.Alpaca()

def get_wsb_posts_for_day(date : str) -> list:
    """
    Used to get a list of all submissions from wallstreetbets
    :param date: datetime formatted by dd/mm/yyyy
    :type date: str
    :return: A list of praw submissions
    :rtype: list
    """
    day = int(date[0:2])
    month = int(date[3:5]) 
    year = int(date[6:])
    epoch = int(dt.datetime(year, month, day).timestamp())
    res = list(api.search_submissions(after=epoch,
                                    before=epoch + (60 * 60 * 24),
                                    subreddit='wallstreetbets',
                                    filter=['url','author', 'title', 'subreddit'],
                                    limit=10000))
    return res

def get_tickers_from_title(title : str) -> list:
    """
    Used to get a list of tickers from a wsb title
    :param title: title of wsb post you want to search for tickers within
    :type title: str
    :return: A list of tickers
    :rtype: list[str]
    """
    # Could have used regex for this but I don't know how to use that stuff
    tickers = []
    while " " in title or "$" in title:
        index = -1
        if "$" in title and " " in title:
            index = title.index(" ") if title.index(" ") < title.index("$") else title.index("$")
        elif " " in title:
            index = title.index(" ")
        elif "$" in title:
            index = title.index("$")
        title = title[index:]
        ticker = ""
        for i in range(len(title)):
            if i == 0:
                continue
            elif title[i] in " .,?!$)(&^@\"\'[]" or i == len(title) - 1:
                if i == len(title) - 1:
                    ticker = ticker + title[i]
                if len(ticker) and ticker.upper() in alpaca.get_refined_ticker_list():
                    tickers.append(ticker)
                break
            else:
                ticker = ticker + title[i]
        title = title[1:]
    return tickers

def get_tradeable_periods(timestamp : int) -> dict:
    """
    Used to get a list of valid trading timeframes for this post
    Returns a dict like javascript which is terrible but don't judge
    :param timestamp: timestamp unix int
    :type timestamp: int
    :return: A dict of tradeable timeframes with boolean od whether or not they are tradeable
    :rtype: dict
    """
    adjustedDatetime = datetime.fromtimestamp(timestamp)
    adjustedDatetime.replace(tzinfo=tz.tzutc())
    adjustedDatetime = adjustedDatetime.astimezone(tz.gettz('America/New_York'))
    
    ret_dict = {"10min": False, "30min": False, "1hour": False}
    # check to see if the date is in a good range so we can check for winners
    if (int(adjustedDatetime.strftime('%H')) * 100) + int(adjustedDatetime.strftime('%M')) < 930:
        return ret_dict
    if (int(adjustedDatetime.strftime('%H')) * 100) + int(adjustedDatetime.strftime('%M')) < 1455:
        ret_dict["1hour"] = True
    if (int(adjustedDatetime.strftime('%H')) * 100) + int(adjustedDatetime.strftime('%M')) < 1525:
        ret_dict["30min"] = True
    if (int(adjustedDatetime.strftime('%H')) * 100) + int(adjustedDatetime.strftime('%M')) < 1545:
        ret_dict["10min"] = True 
        
    return ret_dict
