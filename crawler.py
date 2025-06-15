# 대신증권 크레온 API (실시간)
import requests
from bs4 import BeautifulSoup
import pandas as pd
import concurrent.futures
from tqdm import tqdm
from openpyxl import load_workbook
from financial_data import get_last_year_quarters_financials

def get_stock_data(stock_code):
    URL = f"https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd={stock_code}"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36)"
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

def process_stock_list(excel_path):
    # 엑셀 파일 읽기 (기존 df)
    df = pd.read_excel(excel_path, engine='openpyxl')
    
    # 결과를 저장할 리스트
    results = []
    
    # 종목코드 리스트 준비
    stock_codes = [str(code).zfill(6) for code in df['종목코드']]
    
    # 멀티스레드로 데이터 수집
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # 주식 데이터와 재무 데이터를 병렬로 수집
        stock_futures = list(tqdm(
            executor.map(get_stock_data, stock_codes),
            total=len(stock_codes),
            desc="주식 데이터 수집 중"
        ))
        
        financial_futures = list(tqdm(
            executor.map(get_last_year_quarters_financials, stock_codes),
            total=len(stock_codes),
            desc="재무 데이터 수집 중"
        ))
        
        # 결과 병합
    for stock_code, stock_data, financial_data in zip(stock_codes, stock_futures, financial_futures):
    # 둘 중 하나라도 있으면 포함
        if stock_data or financial_data:
            combined_data = {}
        
        # stock_data가 있으면 추가
        if stock_data:
            combined_data.update(stock_data)
        
        # financial_data가 있으면 추가
        if financial_data:
            combined_data.update(financial_data)
        
        combined_data['종목코드'] = stock_code
        results.append(combined_data)
    
    # 크롤링 결과를 DataFrame으로 변환
    crawled_df = pd.DataFrame(results)
    
    # openpyxl로 워크북 열기
    wb = load_workbook(excel_path)
    ws = wb.active
    
    # 기존 컬럼 이름과 인덱스 매핑 생성
    headers = {cell.value: cell.column for cell in ws[1]}
    
    # 크롤링된 데이터의 컬럼들을 엑셀에 추가 또는 업데이트
    crawled_data_cols = [col for col in crawled_df.columns if col != '종목코드']
    
    for col_name in crawled_data_cols:
        if col_name not in headers:
            new_col_idx = ws.max_column + 1
            ws.cell(row=1, column=new_col_idx, value=col_name)
            headers[col_name] = new_col_idx
            
    # 각 종목코드에 대해 데이터 업데이트
    for r_idx, row in df.iterrows():
        stock_code_from_excel = str(row['종목코드']).zfill(6)
        
        # 크롤링된 데이터에서 해당 종목코드의 행 찾기
        matching_crawled_row = crawled_df[crawled_df['종목코드'] == stock_code_from_excel]
        
        if not matching_crawled_row.empty:
            crawled_data_dict = matching_crawled_row.iloc[0].to_dict()
            
            excel_row_num = r_idx + 2 

            for col_name in crawled_data_cols:
                if col_name in crawled_data_dict:
                    target_col_idx = headers.get(col_name)
                    if target_col_idx:
                        value_to_write = crawled_data_dict[col_name]
                        ws.cell(row=excel_row_num, column=target_col_idx, value=value_to_write)

    # 변경사항 저장
    wb.save(excel_path)
    print(f"데이터가 {excel_path}에 저장되었습니다.")

if __name__ == "__main__":
    input_excel = "stock_list.xlsx"  # 입력 엑셀 파일
    process_stock_list(input_excel)
    print("종료")
    # get_stock_data('000100')
    # financial_data.get_last_year_quarters_financials('000100')