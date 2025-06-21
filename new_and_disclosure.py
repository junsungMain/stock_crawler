import requests
from datetime import datetime

def get_latest_disclosure(stock_code):
    URL = f"https://m.stock.naver.com/api/stock/{stock_code}/disclosure"
    PARAMS = {
        'pageSize': 1,
        'page': 1
    }
    response = requests.get(URL, params=PARAMS)
    response.raise_for_status()
    response_data = response.json()

    data = {}
    if response_data and len(response_data) > 0:
        latest_disclosure_data = response_data[0]
        dis_title = latest_disclosure_data.get('title', '')
        dis_datetime = latest_disclosure_data.get('datetime', '')
        if dis_datetime:
            try:
                dis_datetime = datetime.fromisoformat(dis_datetime.replace('Z', '+00:00')).strftime('%Y.%m.%d')
            except ValueError:
                dis_datetime = ''
        data = {
            '최신 공시': dis_title,
            '최신 공시 날짜':dis_datetime
        }
    return data


def get_latest_news(stock_code):
    URL = f"https://m.stock.naver.com/api/news/stock/{stock_code}"
    PARAMS = {
        'pageSize': 1,
        'page': 1
    }
    response = requests.get(URL, PARAMS)
    response.raise_for_status()
    response_data = response.json()
    
    data = {}
    if response_data and len(response_data) > 0:
        latest_news_data = response_data[0]['items'][0]
        news_title = latest_news_data.get('title', '')
        news_datetime = latest_news_data.get('datetime', '')
        if news_datetime and len(news_datetime) >= 12:
            news_datetime = f"{news_datetime[:4]}.{news_datetime[4:6]}.{news_datetime[6:8]} {news_datetime[8:10]}:{news_datetime[10:12]}"
        data = {
            '최신 뉴스': news_title,
            '최신 뉴스 날짜': news_datetime
        }

    return data