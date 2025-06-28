import requests
from bs4 import BeautifulSoup
    
def get_stock_extra_data(stock_code, session=None):
    url = f"https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd={stock_code}"
    _session = session or requests.Session()
    
    headers = {
        'Referer': 'https://navercomp.wisereport.co.kr/',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache'
    }
    
    response = _session.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    data = {}
    earning_rate_data = soup.select('#cTB11 > tbody > tr:nth-child(9) > td > span')
    if earning_rate_data:
        data.update({
            '수익률(1개월)': round(float(earning_rate_data[0].text.replace("%","").replace(",", "").strip()) / 100, 4),
            '수익률(3개월)': round(float(earning_rate_data[1].text.replace("%","").replace(",", "").strip()) / 100, 4),
            '수익률(6개월)': round(float(earning_rate_data[2].text.replace("%","").replace(",", "").strip()) / 100, 4),
            '수익률(1년)': round(float(earning_rate_data[3].text.replace("%","").replace(",", "").strip()) / 100, 4)            
        })

    return data
