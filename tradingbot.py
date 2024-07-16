from lumibot.brokers import Alpaca #broker class
from lumibot.backtesting import YahooDataBacktesting #framework for backtesting
from lumibot.strategies.strategy import Strategy #trading bot
from lumibot.traders import Trader #trader class
from datetime import datetime
from alpaca_trade_api import REST
from datetime import datetime, timedelta

#https://lumibot.lumiwealth.com/getting_started.html

API_KEY = "PKJVOU1ZYALYUBXKRHR1"
API_SECRET = "NZT2LgA0nz7XwaPhNdgmjDjNsxuCpw1HkjdT77JY"
BASE_URL = "https://paper-api.alpaca.markets/v2"

ALPACA_CREDS = {
    "API_KEY" : API_KEY,
    "API_SECRET" : API_SECRET,
    "PAPER": True
}

class MLtrader(Strategy): #trading logic
    def initialize(self, symbol:str="SPY", cash_at_risk: float=.5):
        self.symbol = symbol
        self.sleeptime = "24H" #how freq we trade
        self.last_trade = None
        self.cash_at_risk = cash_at_risk 
        self.api = REST(base_url=BASE_URL, key_id= API_KEY, secret_key=API_SECRET)

    def position_sizing(self):
        cash = self.get_cash()
        last_price = self.get_last_price(self.symbol)
        quantity = cash * self.cash_at_risk / last_price #how much cash we want to risk and the divide tells how much per units we r getting
        return cash, last_price, quantity

    def get_dates(self):
        today = self.get_datetime()
        three_days_prior = today - timedelta(days=3) #get 3 days ahead using the import
        return today.strftime('%Y-%m-%d'), three_days_prior.strftime('%Y-%m-%d')

    def get_sentiment(self):
        today, three_days_prior = self.get_dates()
        news = self.api.get_news(symbol=self.symbol, 
                                 start=three_days_prior, 
                                 end=today)
        news = [ev.__dict__["_raw"]["headline"] for ev in news] #format news
        return news

    def on_trading_iteration(self):
        cash, last_price, quantity = self.position_sizing()

        if cash > last_price: #make sure we got cash
            if self.last_trade is None:
                news = self.get_new()
                print(news)
                order = self.create_order(
                    self.symbol, 
                    10, 
                    "buy", 
                    type="bracket", 
                    take_profit_price = last_price * 1.2, #we make more than 20%
                    stop_loss_price = last_price * .95 #we lose more than 5%
                     )
                self.submit_order(order)
                self.last_trade = "buy"


broker = Alpaca(ALPACA_CREDS)
strat = MLtrader(name = 'mlstrat', broker=broker, parameters={"symbol" : "SPY", "cash_at_risk" : ".5"})

strat.backtest(YahooDataBacktesting, datetime(2023,12,15), datetime(2023,12,31), parameters={})

