import alpaca_api

class WSBPost:
    def __init__(self) -> None:
        self.postId = ""
        self.ticker = ""
        self.title = ""
        self.description = ""
        self.tenMinuteWinner = False
        self.thirtyMinuteWinner = False
        self.oneHourWinner = False
        self.postTime = -1
 