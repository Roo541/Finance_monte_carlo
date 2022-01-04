import requests

eod_key = '***'
def fundamental_data(symbol):
    API_URL = r'https://eodhistoricaldata.com/api/fundamentals/%s.US?' %symbol

    data_1 = {
                'api_token': eod_key,         
            }

    session = requests.Session()
    r = session.get(API_URL, params = data_1)
    data = r.json()
    
    return data


