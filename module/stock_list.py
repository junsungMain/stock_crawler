import requests
from module.common import parse_num_value

def get_theme_list(session=None):
    URL = f"https://m.stock.naver.com/api/stocks/theme"
    page = 1
    page_size = 100
    data = {}
    _session = session or requests
    while True:
        PARAMS = {
            'page': page,
            'pageSize': page_size
        }
        response = _session.get(URL, params=PARAMS)
        response.raise_for_status()
        response_data = response.json()
        theme_data = response_data.get('groups', [])
        for theme in theme_data:
            stocks = get_stock_list(theme['no'], theme['name'], session=_session)
            for code, stock_info in stocks.items():
                if code not in data:
                    data[code] = stock_info
                else:
                    data[code]['테마'] += ', '+stock_info['테마']
        total_count = response_data.get('totalCount', 0)
        if page * page_size >= total_count:
            break
        page += 1
    return data

def get_stock_list(theme_no, theme_name, session=None):
    URL = f"https://m.stock.naver.com/api/stocks/theme/{theme_no}"
    page = 1
    page_size = 100
    data = {}
    _session = session or requests
    while True:
        PARAMS = {
            'page': page,
            'pageSize': page_size
        }
        response = _session.get(URL, params=PARAMS)
        response.raise_for_status()
        response_data = response.json()
        stocks_data = response_data.get('stocks', [])
        for stock in stocks_data:
            if stock['itemCode'] not in data:
                data[stock['itemCode']] = {
                    '종목명': stock['stockName'],
                    '테마': theme_name,
                    '현재가': float(parse_num_value(stock['closePrice'])),
                    '전일대비': float(parse_num_value(stock['compareToPreviousClosePrice'])),
                    '등락률': round(float(parse_num_value(stock['fluctuationsRatio'])) / 100, 4),
                    '거래량': float(parse_num_value(stock['accumulatedTradingVolume'])),
                    '시가 총액(억)': float(parse_num_value(stock['marketValue'])),
                }
        total_count = response_data.get('totalCount', 0)
        if page * page_size >= total_count:
            break
        page += 1
    return data