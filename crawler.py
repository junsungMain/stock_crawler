import pandas as pd
import concurrent.futures
from tqdm import tqdm
from openpyxl import load_workbook
from financial_data import get_financial_extra_data, get_financial_data
from main_data import get_stock_data, get_stock_extra_data
from new_and_disclosure import get_latest_disclosure, get_latest_news
import os
from dotenv import load_dotenv
from common import retry_on_failure, setup_logging_and_cleanup
import requests

def process_stock_list(excel_path):
    df = pd.read_excel(excel_path, engine='openpyxl')
    
    results = []
    
    stock_codes = [str(code).zfill(6) for code in df['종목코드']]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(os.cpu_count() * 2, 30)) as executor:
        stock_futures = list(tqdm(
            executor.map(retry_on_failure(get_stock_data), stock_codes),
            total=len(stock_codes),
            desc="주식 데이터 수집 중"
        ))

        stock_basic_futures = list(tqdm(
            executor.map(retry_on_failure(get_stock_extra_data), stock_codes),
            total=len(stock_codes),
            desc="주식 추가 데이터 수집 중"
        ))

        financial_futures = list(tqdm(
            executor.map(retry_on_failure(get_financial_data), stock_codes),
            total=len(stock_codes),
            desc="재무 데이터 수집 중"
        ))

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0'
    })
    main_url = 'https://navercomp.wisereport.co.kr/'
    session.get(main_url, timeout=10)

    with concurrent.futures.ThreadPoolExecutor(5) as executor:
        financial_extra_futures = list(tqdm(
            executor.map(retry_on_failure(get_financial_extra_data), stock_codes),
            total=len(stock_codes),
            desc="재무 기타 데이터 수집 중"
        ))

        new_futures = list(tqdm(
            executor.map(retry_on_failure(get_latest_news), stock_codes),
            total=len(stock_codes),
            desc="뉴스 데이터 수집 중"
        ))
        
        disclosure_futures = list(tqdm(
            executor.map(retry_on_failure(get_latest_disclosure), stock_codes),
            total=len(stock_codes),
            desc="공시 데이터 수집 중"
        ))
       
    session.close()
        
    for stock_code, *data_sources in zip(stock_codes, stock_futures, financial_futures, 
                                    financial_extra_futures, new_futures, disclosure_futures, stock_basic_futures):
        
        combined_data = {'종목코드': stock_code}

        for data in data_sources:
            if data:
                combined_data.update(data)
        
        results.append(combined_data)
    
    crawled_df = pd.DataFrame(results)
    
    wb = load_workbook(excel_path)
    ws = wb.active
    
    headers = {cell.value: cell.column for cell in ws[1]}
    
    crawled_data_cols = [col for col in crawled_df.columns if col != '종목코드']
    
    for col_name in crawled_data_cols:
        if col_name not in headers:
            new_col_idx = ws.max_column + 1
            ws.cell(row=1, column=new_col_idx, value=col_name)
            headers[col_name] = new_col_idx
            
    for r_idx, row in df.iterrows():
        stock_code_from_excel = str(row['종목코드']).zfill(6)
        
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

    wb.save(excel_path)
    print(f"데이터가 {excel_path}에 저장되었습니다.")

if __name__ == "__main__":
    load_dotenv()
    input_excel = os.getenv('INPUT_EXCEL', 'stock_list.xlsx')
    setup_logging_and_cleanup()
    process_stock_list(input_excel)
    print("종료")