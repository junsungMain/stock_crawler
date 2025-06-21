import requests
from bs4 import BeautifulSoup
from common import parse_num_value

def get_stock_data(stock_code):
    URL = f"https://polling.finance.naver.com/api/realtime/domestic/stock/{stock_code}"
    response = requests.get(URL)
    response.raise_for_status()
    response_data = response.json()['datas'][0]

    data = {
        '현재가': float(parse_num_value(response_data['closePrice'])),
        '전일대비': float(parse_num_value(response_data['compareToPreviousClosePrice'])) ,
        '등락률': round(float(parse_num_value(response_data['fluctuationsRatio'])) / 100, 4),
        '거래량': float(parse_num_value(response_data['accumulatedTradingVolume']))
    }

    return data

    
def get_stock_extra_data(stock_code):
    URL = f"https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd={stock_code}"
    response = requests.get(URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    data = {}
    market_cap = soup.select_one('#cTB11 > tbody > tr:nth-child(5) > td')
    if market_cap:
        data['시가 총액(억)'] = int(market_cap.text.replace("억원", "").replace(",","").strip())

    earning_rate_data = soup.select('#cTB11 > tbody > tr:nth-child(9) > td > span')
    if earning_rate_data:
        data = {
            '수익률(1개월)': round(float(earning_rate_data[0].text.replace("%","").replace(",", "").strip()) / 100, 4),
            '수익률(3개월)': round(float(earning_rate_data[1].text.replace("%","").replace(",", "").strip()) / 100, 4),
            '수익률(6개월)': round(float(earning_rate_data[2].text.replace("%","").replace(",", "").strip()) / 100, 4),
            '수익률(1년)': round(float(earning_rate_data[3].text.replace("%","").replace(",", "").strip()) / 100, 4)            
        }

    return data
