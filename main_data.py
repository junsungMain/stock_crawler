import requests
from bs4 import BeautifulSoup

def get_stock_data(stock_code):
    URL = f"https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd={stock_code}"
    HEADERS = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(URL, headers=HEADERS)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    data = {}
    try:
        # 현재가
        real_price = soup.select_one('#cTB11 > tbody > tr:nth-child(1) > td > strong')
        if real_price:
            data['현재가'] = int(real_price.text.replace(",","").strip())
        
        # 전일대비
        prev_price = soup.select_one('#cTB11 > tbody > tr:nth-child(1) > td > span:nth-child(2)')
        if prev_price:
            price_text = prev_price.text.strip()
            price_text = price_text.replace('원', '').replace('-', '▼').replace('+', '▲')
            data['전일대비'] = price_text

        # 등락률
        change_rate = soup.select_one('#cTB11 > tbody > tr:nth-child(1) > td > span:nth-child(3)')
        if change_rate:
            data['등락률'] = round(float(change_rate.text.replace("%","").replace(",","").strip()) / 100, 4)
        
        # 거래량
        volume = soup.select_one('#cTB11 > tbody > tr:nth-child(4) > td')
        if volume:
            data['거래량'] = int(volume.text.split('주')[0].replace(",","").strip())
        
        # 시가총액
        market_cap = soup.select_one('#cTB11 > tbody > tr:nth-child(5) > td')
        if market_cap:
            data['시가 총액(억)'] = int(market_cap.text.replace("억원", "").replace(",","").strip())

                
        # 수익률
        spans = soup.select('#cTB11 > tbody > tr:nth-child(9) > td > span')
        if spans:
            return_data = [span.text.strip() for span in spans]
            data['수익률(1개월)'] = round(float(return_data[0].replace("%","").replace(",", "").strip()) / 100, 4)
            data['수익률(3개월)'] = round(float(return_data[1].replace("%","").replace(",", "").strip()) / 100, 4)
            data['수익률(6개월)'] = round(float(return_data[2].replace("%","").replace(",", "").strip()) / 100, 4)
            data['수익률(1년)'] = round(float(return_data[3].replace("%","").replace(",", "").strip()) / 100, 4)
            
        return data
            
    except Exception as e:
        print(f"에러 발생 (종목코드: {stock_code}): {str(e)}")
        return data
      