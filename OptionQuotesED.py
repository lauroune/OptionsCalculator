import bs4 as bs
import datetime as dt
import os
import pickle
import requests
from wallstreet import Stock, Call, Put

def save_weekly_earnings():
    resp = requests.get('https://www.earningswhispers.com/calendar')
    soup = bs.BeautifulSoup(resp.text, "lxml")
    ul = soup.find('ul', {'class': 'allcal standardview earningsday'})
    tickers = []
    for row in ul.findAll('div',{'class':'vote'}):
        for tag in row.findAll(True,{'id':True}):
            tickers.append(tag['id'])
            
        with open("saveweekly.pickle","wb") as f:
            pickle.dump(tickers,f)

    print(tickers)
    return tickers

save_weekly_earnings()

def get_quotes_from_yahoo(reload_weekly=False):
    if reload_weekly:
        tickers = save_weekly_earnings()
    else:
        with open("saveweekly.pickle","rb") as f:
            tickers = pickle.load(f)

    for ticker in tickers:
        print(ticker)
        g = Stock(ticker, source='yahoo')
        price = g.price

        PutATM = Put(ticker, strike=price, source='yahoo')
        b = PutATM.price

        CallATM = Call(ticker, strike=price, source='yahoo')
        a = CallATM.price

        print("Put ATM:",a,"Call ATM:",b)

        iv = (a+b)
        poms = PutATM.strike
        pom = poms-iv
        coms = CallATM.strike
        com = coms+iv

        PutIV = Put(ticker, strike=pom, source='yahoo')
        PutIV2 = Put(ticker, strike=pom-3, source='yahoo')
        pl = PutIV.price
        pl2 = PutIV2.price
        pis = PutIV.strike 
        pis2 = PutIV2.strike
        
        CallIV = Call(ticker,strike=com, source='yahoo')
        CallIV2 = Call(ticker,strike=com+3, source='yahoo')
        cl = CallIV.price
        cl2 = CallIV2.price
        cis = CallIV.strike
        cis2 = CallIV2.strike

        MaxLossP = pis - pis2
        MaxLossC = cis - cis2
        ProfitP = 100*(pl-pl2)/(MaxLossP+0.00001)
        ProfitC = 100*(cl2-cl)/(MaxLossC+0.00001)
        
        print("Implied Volatility:",iv,"Puts Outside of IV:", pl,"Calls Outside of IV:", cl)
        print("Profit from selling puts at", pis, "and buying at", pis2,":",ProfitP,"%")
        print("Profit from selling calls at", cis, "and buying at", cis2,":",ProfitC,"%")
        

        
get_quotes_from_yahoo()
