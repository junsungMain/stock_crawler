import requests
from bs4 import BeautifulSoup

def get(stock_code):
    URL = f"https://finance.naver.com/item/main.naver?code={stock_code}"
    HEADERS = {
        "User-Agent": "Mozilla/5.0"
    }
    RESPONSE = requests.get(URL, headers=HEADERS)
    RESPONSE.raise_for_status()
    SOUP = BeautifulSoup(RESPONSE.text, 'html.parser')
    tag = SOUP.select_one("#content > div.section.trade_compare > table > tbody > tr:nth-child(12) > td:nth-child(2)")
    print(tag.text)
    
get_financial_data('103590')