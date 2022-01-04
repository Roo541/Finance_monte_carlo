import requests

eod_key = '***'

def ohlc(start, end, symbol):
    API_URL_1 = r"https://eodhistoricaldata.com/api/eod/%s" % symbol
    data_1 = {
                        'api_token': eod_key,
                        'period': 'd',
                        'order':'d',
                        'fmt':'json',
                        'from':start,
                        'to':end,            
                        }

    session = requests.Session()
    r = session.get(API_URL_1, params = data_1)
    ohlc = r.json()

    return ohlc

    