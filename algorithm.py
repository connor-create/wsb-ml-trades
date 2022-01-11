import praw
from datetime import datetime
import sms

import model
import wsb_reddit
import alpaca_api

alpaca = alpaca_api.Alpaca()

r = praw.Reddit(
    client_id="",
    client_secret="",
    password="",
    user_agent="",
    username="",
)

hour_model = model.build_hour_model()
if hour_model is None:
    print("no model found")
    exit(1)

subreddit = r.subreddit("wallstreetbets")
for submission in subreddit.stream.submissions():
    # Only process if less than 60 seconds ago
    if datetime.now().timestamp() - submission.created_utc < 60:
        print(datetime.now().timestamp() - submission.created_utc, submission.title)
        for ticker in wsb_reddit.get_tickers_from_title(submission.title):
            res = hour_model.predict([model.preprocess_text(submission.title + submission.selftext, ticker)])
            print(ticker, res)
            if ticker.isupper():
                if res[0] == '1hourWinner':
                    alpaca.submit_market_buy_order(ticker)
                elif res[0] == 'not1Hour':
                    alpaca.submit_market_short_order(ticker)