from pytickersymbols import PyTickerSymbols
import csv
import requests
import bs4 as bs



def loadTickers(update=False):

    '''
    scrapes dow jones, nasdaq and 
    scrapes the list of the S&P 500 stocks
    params @update - if set to true it scrapes them
        otherwise loads from csv file

    '''
    # scrape dow jones and nasdaq for more tickers
    stockData = PyTickerSymbols()
    dIJA = stockData.get_dow_jones_nyc_google_tickers('DOW JONES')
    tickers = [ticker.split(':')[1] + ' US Equity' for ticker in dIJA]
    nasdaq = stockData.get_nasdaq_100_nyc_google_tickers('NASDAQ 100')
    tickers = set(tickers).union(set([ticker.split(':')[1] + ' US Equity' for ticker in nasdaq]))

    # scrape S&P 500 List from wikipedia
    if update:
        resp = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')        
        soup = bs.BeautifulSoup(resp.text, 'html.parser')        
        table = soup.find('table', {'class': 'wikitable sortable'})       

        tix = []

        for row in table.findAll('tr')[1:]:
            ticker = row.findAll('td')[0].text + ' US Equity'
            tix.append(ticker)

        tix = [ticker.replace('\n', '') for ticker in tix]

        with open('sAndP.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            for ticker in tix:
                writer.writerow([ticker])
                tickers.add(ticker)

    # load S&P 500 list from csv file
    else:
        with open('sAndP.csv', 'r', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                tickers.add(row[0])

    tickers = list(tickers)
    tickers.sort()

    return tickers

def getSlope(macD, prices, delta='one', p='na'):

    '''
    
        Gets the slopes of the given macD set based on params
        param prices: the prices corresponding to the macD values
            chronologically in order
        param delta: one returns one day slope, max searches the interval
            to find either the slope from recent high or low
        param p: marks whether slope from recent high or low should be computed

    '''
    if delta == 'max':
        todayMacD = macD[len(macD) - 1]
        prices = prices[0:len(prices) - 1]
        macD = macD[0:len(macD) - 1]
        if p == 'low':
            minPrice = float('inf')
            minMD = 0
            minInd = -1
            for i, (price, mD) in enumerate(zip(prices, macD)):
                if price < minPrice:
                    minPrice = price
                    minMD = mD
                    minInd = i

            # notice len(macD) is 2 shorter then it should be, but len() adds 1 so only add 1
            return (todayMacD - minMD) / ((len(macD) + 1) - minInd)
        elif p == 'high':
            maxPrice = float('-inf')
            maxPrice = 0
            maxInd = -1
            for i, (price, mD) in enumerate(zip(prices, macD)):
                if price > maxPrice:
                    maxPrice = price
                    maxMD = mD
                    maxInd = i
            return (todayMacD - maxMD) / (len(macD) - maxInd)
    else:
        return macD[len(macD) - 1]  - macD[len(macD) - 2]

def validDay(dt, valid_days):
    # Helper function to determine if market was open on that day

    valid = False
    for v in valid_days:
        valid = valid or (dt == v.date())

    return valid
