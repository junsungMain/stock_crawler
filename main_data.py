import requests
from bs4 import BeautifulSoup

def get_stock_data(stock_code):
    URL = f"https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd={stock_code}"
    HEADERS = {
        "User-Agent": "Mozilla/5.0"
    }
    RESPONSE = requests.get(URL, headers=HEADERS)
    RESPONSE.raise_for_status()
    SOUP = BeautifulSoup(RESPONSE.text, 'html.parser')
    
    try:
        data = {}
        
        # 현재가
        real_price = SOUP.select_one('#cTB11 > tbody > tr:nth-child(1) > td > strong')
        if real_price:
            data['현재가'] = int(real_price.text.replace(",","").strip())
        
        # 전일대비
        prev_price = SOUP.select_one('#cTB11 > tbody > tr:nth-child(1) > td > span:nth-child(2)')
        if prev_price:
            price_text = prev_price.text.strip()
            price_text = price_text.replace('원', '').replace('-', '▼').replace('+', '▲')
            data['전일대비'] = price_text

        # 등락률
        change_rate = SOUP.select_one('#cTB11 > tbody > tr:nth-child(1) > td > span:nth-child(3)')
        if change_rate:
            data['등락률'] = round(float(change_rate.text.replace("%","").strip()) / 100, 4)
        
        # 거래량
        volume = SOUP.select_one('#cTB11 > tbody > tr:nth-child(4) > td')
        if volume:
            data['거래량'] = int(volume.text.split('주')[0].replace(",","").strip())
        
        # 시가총액
        market_cap = SOUP.select_one('#cTB11 > tbody > tr:nth-child(5) > td')
        if market_cap:
            data['시가 총액(억)'] = int(market_cap.text.replace("억원", "").replace(",","").strip())

                
        # 수익률
        spans = SOUP.select('#cTB11 > tbody > tr:nth-child(9) > td > span')
        if spans:
            return_data = [span.text.strip() for span in spans]
            data['수익률(1개월)'] = round(float(return_data[0].replace("%","").strip()) / 100, 4)
            data['수익률(3개월)'] = round(float(return_data[1].replace("%","").strip()) / 100, 4)
            data['수익률(6개월)'] = round(float(return_data[2].replace("%","").strip()) / 100, 4)
            data['수익률(1년)'] = round(float(return_data[3].replace("%","").strip()) / 100, 4)
            
        return data
            
    except Exception as e:
        print(f"에러 발생 (종목코드: {stock_code}): {str(e)}")
        return None
    
def get_stock_extra_data(stock_code):
    URL = f"https://finance.naver.com/item/main.naver?code={stock_code}"
    HEADERS = {
        "User-Agent": "Mozilla/5.0"
    }
    RESPONSE = requests.get(URL, headers=HEADERS)
    RESPONSE.raise_for_status()
    SOUP = BeautifulSoup(RESPONSE.text, 'html.parser')

    try:
        data = {}
        
        # ROE(%)
        roe = SOUP.select_one('#content > div.section.trade_compare > table > tbody > tr:nth-child(12) > td:nth-child(2)')
        if roe:
            roe_text = roe.text.strip()
            if roe_text:
                data['ROE(%)'] = float(roe_text)
            else:
                data['ROE(%)'] = None

        # PER(배)
        per = SOUP.select_one('#content > div.section.trade_compare > table > tbody > tr:nth-child(13) > td:nth-child(2)')
        if per:
            per_text = per.text.replace(",","").strip()
            if per_text:
                data['PER(배)'] = float(per_text)
            else:
                data['PER(배)'] = None

        # PBR(배)
        pbr = SOUP.select_one('#content > div.section.trade_compare > table > tbody > tr:nth-child(14) > td:nth-child(2)')
        if pbr:
            pbr_text = pbr.text.replace(",","").strip()
            if pbr_text:
                data['PBR(배)'] = float(pbr_text)
            else:
                data['PBR(배)'] = None
        return data
            
    except Exception as e:
        print(f"에러 발생 (종목코드: {stock_code}): {str(e)}")
        return None
      