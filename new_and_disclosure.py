import requests
from datetime import datetime

def get_news_and_disclosure_latest(stock_code):     
    disclosure_url = f"https://m.stock.naver.com/api/stock/{stock_code}/disclosure"
    news_url = f"https://m.stock.naver.com/api/news/stock/{stock_code}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/json'
    }
    
    params = {
        'pageSize': 1,  
        'page': 1
    }
    
    try:
        disclosure_response = requests.get(disclosure_url, headers=headers, params=params)
        news_response = requests.get(news_url, headers=headers, params=params)
        disclosure_data = disclosure_response.json()
        news_data = news_response.json()

        # 뉴스 데이터 처리
        latest_news = ''
        latest_news_date = ''
        if news_data and len(news_data) > 0 and 'items' in news_data[0] and len(news_data[0]['items']) > 0:
            news_item = news_data[0]['items'][0]
            latest_news = news_item.get('title', '')
            datetime_str = news_item.get('datetime', '')
            if datetime_str and len(datetime_str) >= 12:
                latest_news_date = f"{datetime_str[:4]}.{datetime_str[4:6]}.{datetime_str[6:8]} {datetime_str[8:10]}:{datetime_str[10:12]}"

        # 공시 데이터 처리
        latest_disclosure = ''
        latest_disclosure_date = ''
        if disclosure_data and len(disclosure_data) > 0:
            disclosure_item = disclosure_data[0]
            latest_disclosure = disclosure_item.get('title', '')
            datetime_str = disclosure_item.get('datetime', '')
            if datetime_str:
                try:
                    latest_disclosure_date = datetime.fromisoformat(datetime_str.replace('Z', '+00:00')).strftime('%Y.%m.%d')
                except ValueError:
                    latest_disclosure_date = ''

        return {
            '최신 뉴스': latest_news,
            '최신 뉴스 날짜': latest_news_date,
            '최신 공시': latest_disclosure,
            '최신 공시 날짜': latest_disclosure_date
        }
        
    except Exception as e:
        print(f"에러: {e}")
        return None
    
