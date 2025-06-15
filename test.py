import requests
from bs4 import BeautifulSoup

def get_financial_data(stock_code):
    url = "https://navercomp.wisereport.co.kr/company/cF3002.aspx"
    params = {
        "cmp_cd": stock_code,
        "frq": "0",         # 0: 연간, 1: 분기
        "rpt": "0",         # 0: 포괄손익계산서, 1: 재무상태표, 2: 현금흐름표
        "finGubun": "MAIN", # 주재무제표
        "frqTyp": "0",      # 연간
        "cn": "",
        "encparam": ""      # 없어도 동작함
    }
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": f"https://navercomp.wisereport.co.kr/v2/company/c1030001.aspx?cmp_cd={stock_code}",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest"
    }
    res = requests.get(url, params=params, headers=headers)
    print('status_code:', res.status_code)
    print('length:', len(res.text))
    print(res.text[:500])  # 앞부분만 출력
    
get_financial_data('103590')