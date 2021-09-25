import json
import requests
import logging
from datetime import date, timedelta
logging.basicConfig(level=logging.ERROR)


class EODAPI:
    BASE_URL = "https://eodhistoricaldata.com/api/"
    NUM_RETRIES = 3

    def __init__(self, apiToken):
        self.apiToken = apiToken

    # Do basic API call to EOD API and retry if fail
    def doRequest(self, url, params={}):
        # Use API key and JSON format as default
        defaultParams = {"fmt":"json", "api_token":self.apiToken}
        # Overwrite with given parameters
        requestParams = {**defaultParams, **params}
        retries = 1
        while retries <= self.NUM_RETRIES:
            try:
                req = requests.get(url, params=requestParams)
                print(req.url)
                if req.status_code == 200:
                    return json.loads(req.content.decode("utf-8"))
                else:
                    logging.error('Error, status code: {0}'.format(req.status_code))
                    if req.status_code in [402, 403, 422]:
                        # Not authorized or no API calls left
                        return None
            except Exception as e:
                logging.error(str(e))
            retries = retries + 1
        return None

    # Get information about API limit
    def getUserData(self):
        return self.doRequest(self.BASE_URL+'user')

    # Get the fundamentals of a stock
    def getFundamentals(self, symbol, exchange):
        return self.doRequest(self.BASE_URL+'fundamentals/{0}.{1}'.format(symbol, exchange))
    
    # Get all available exchanges
    def getExchangeList(self):
        return self.doRequest(self.BASE_URL+'exchanges-list')
    
    # Get all tickers of an exchange
    def getTickers(self, exchange):
        return self.doRequest(self.BASE_URL+'exchange-symbol-list/{0}'.format(exchange))

    # Get information about trading hours and holidays
    def getExchangeDetails(self, exchange, start="", end=""):
        params = {"from":start, "to":end}
        return self.doRequest(self.BASE_URL+'exchange-details/{0}'.format(exchange), params)

    # Get 15-20 minutes delayed 1m price data
    # Provide symbols with exchanges: VOW3.F,AAPL.US,MO.US
    def getRealTimeData(self, symbols):
        params = {}
        if type(symbols) == list:
            if len(symbols) > 1:
                # Use s parameter for more than one symbol
                params = {"s":symbols[1:]}
                symbol = symbols[0]
            else:
                # One symbol in a list
                symbol = symbols[0]
        else:
            # A symbol as string
            symbol = symbols
        return self.doRequest(self.BASE_URL+'real-time/{0}'.format(symbol), params)

    # Get options for a stock
    def getOptions(self, symbol, exchange):
        return self.doRequest(self.BASE_URL+'options/{0}.{1}'.format(symbol, exchange))
    
    # All dividends for a symbol
    def getAllDividends(self, symbol, exchange):
        return self.doRequest(self.BASE_URL+'div/{0}.{1}'.format(symbol, exchange))

    # All splits for a symbol
    def getAllSplits(self, symbol, exchange):
        return self.doRequest(self.BASE_URL+'splits/{0}.{1}'.format(symbol, exchange))
    
    # Get historical quotes
    # Default: Get all available data
    def getHistoricalData(self, symbol, exchange, start="1970-01-01", end="2050-12-31"):
        params = {"period":"d", "from":start, "to":end}
        return self.doRequest(self.BASE_URL+'eod/{0}.{1}'.format(symbol, exchange), params)
    
    # Get bulk data for one exchange
    # Default: Get only quotes
    # You can also request splits and dividends.
    # Returned data {"quotes":[], "splits":[], "dividends":[]}
    def getBulk(self, exchange, quotes=True, splits=False, dividends=False, date=None):
        quotesData = []
        splitsData = []
        dividendsData = []
        params = {}
        if date != None:
            params["date"] = date
        if quotes:
            quotesData = self.doRequest(self.BASE_URL+'eod-bulk-last-day/{0}'.format(exchange), params)
        if splits:
            params["type"] = "splits"
            splitsData = self.doRequest(self.BASE_URL+'eod-bulk-last-day/{0}'.format(exchange), params)
        if dividends:
            params["type"] = "dividends"
            dividendsData = self.doRequest(self.BASE_URL+'eod-bulk-last-day/{0}'.format(exchange), params)
        # Return combined data
        return {"quotes":quotesData, "splits":splitsData, "dividends":dividendsData}
    
    # Get IPOs
    # Maximum 10 years data request in one API call
    def getIPOs(self, start, end):
        params = {"from":start, "to":end}
        return self.doRequest(self.BASE_URL+'calendar/ipos', params)
    
    # Get only upcoming IPOs
    def getUpcomingIPOs(self):
        dateFrom = date.today()
        dateTo = dateFrom + timedelta(days=364*10)  # Add nearly 10 years
        todayString = dateFrom.strftime("%Y-%m-%d")
        endString = dateTo.strftime("%Y-%m-%d")
        return self.getIPOs(todayString, endString)