# 대신증권 크레온 API (실시간)
import requests
from bs4 import BeautifulSoup

URL = "https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd=000100"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
RESPOSE = requests.get(URL, headers=HEADERS)
RESPOSE.raise_for_status()
SOUP = BeautifulSoup(RESPOSE.text, 'html.parser')

def get_yuhan_data():
    try:
        # 현재가
        real_price = SOUP.select_one('#cTB11 > tbody > tr:nth-child(1) > td > strong')
        if real_price:
            print("현재가:", real_price.text.strip())
        
        # 전일대비
        prev_price = SOUP.select_one('#cTB11 > tbody > tr:nth-child(1) > td > span:nth-child(2)')
        if prev_price:
            print("전일대비:", prev_price.text.strip())
            
        # 등락률
        change_rate = SOUP.select_one('#cTB11 > tbody > tr:nth-child(1) > td > span:nth-child(3)')
        if change_rate:
            print("등락률:", change_rate.text.strip())
            
        # 거래량
        volume = SOUP.select_one('#cTB11 > tbody > tr:nth-child(4) > td')
        if volume:
            volume = volume.text.split('주')[0].strip()
            print("거래량:", volume)
            
        # 시가총액
        market_cap = SOUP.select_one('#cTB11 > tbody > tr:nth-child(5) > td')
        if market_cap:
            print("시가총액:", market_cap.text.replace("억원", "").strip())

        # PER
        # ROE
        # PBR
                
        # 수익률
        spans = SOUP.select('#cTB11 > tbody > tr:nth-child(9) > td > span')
        if spans:
            return_data = [span.text.strip() for span in spans]
        
        return_1m = return_data[0]
        return_3m = return_data[1]
        return_6m = return_data[2]
        return_1y = return_data[3]

        print("수익률1개월:",return_1m)
        print("수익률3개월:",return_3m)
        print("수익률6개월:",return_6m)
        print("수익률1년:",return_1y)
            
    except Exception as e:
        return [f"에러 발생: {str(e)}"]

def get_financial_report(): 
    try:
        # 현재가
        real_price = SOUP.select_one('#cTB11 > tbody > tr:nth-child(1) > td > strong')
        if real_price:
            print("현재가:", real_price.text.strip())
        
        # 전일대비
        prev_price = SOUP.select_one('#cTB11 > tbody > tr:nth-child(1) > td > span:nth-child(2)')
        if prev_price:
            print("전일대비:", prev_price.text.strip())
            
        # 등락률
        change_rate = SOUP.select_one('#cTB11 > tbody > tr:nth-child(1) > td > span:nth-child(3)')
        if change_rate:
            print("등락률:", change_rate.text.strip())
            
        # 거래량
        volume = SOUP.select_one('#cTB11 > tbody > tr:nth-child(4) > td')
        if volume:
            volume = volume.text.split('주')[0].strip()
            print("거래량:", volume)
            
        # 시가총액
        market_cap = SOUP.select_one('#cTB11 > tbody > tr:nth-child(5) > td')
        if market_cap:
            print("시가총액:", market_cap.text.replace("억원", "").strip())

        # PER
        # ROE
        # PBR
                
        # 수익률
        spans = SOUP.select('#cTB11 > tbody > tr:nth-child(9) > td > span')
        if spans:
            return_data = [span.text.strip() for span in spans]
        
        return_1m = return_data[0]
        return_3m = return_data[1]
        return_6m = return_data[2]
        return_1y = return_data[3]

        print("수익률1개월:",return_1m)
        print("수익률3개월:",return_3m)
        print("수익률6개월:",return_6m)
        print("수익률1년:",return_1y)
            
    except Exception as e:
        return [f"에러 발생: {str(e)}"]


if __name__ == "__main__":
    get_yuhan_data()