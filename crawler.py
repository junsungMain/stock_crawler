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
import functools
import logging

def fetch_all_data_for_stock(stock_code, session):
    
    getters = {
        'stock_data': functools.partial(get_stock_data, session=session),
        'stock_extra_data': functools.partial(get_stock_extra_data, session=session),
        'financial_data': functools.partial(get_financial_data, session=session),
        'financial_extra_data': functools.partial(get_financial_extra_data, session=session),
        'latest_news': functools.partial(get_latest_news, session=session),
        'latest_disclosure': functools.partial(get_latest_disclosure, session=session),
    }

    combined_data = {'종목코드': stock_code}
    
    for key, getter in getters.items():
        try:
            data = retry_on_failure(getter)(stock_code)
            if data:
                combined_data.update(data)
        except Exception as e:
            logging.error(f"{stock_code}의 {key} 데이터 수집 중 오류 발생: {e}")
            
    return combined_data

def process_stock_list(excel_path):
    df = pd.read_excel(excel_path, engine='openpyxl', dtype={'종목코드': str})
    df['종목코드'] = df['종목코드'].str.zfill(6)
    
    stock_codes = df['종목코드'].tolist()
    
    results = []

    session = requests.Session()
    max_workers = min(os.cpu_count() * 2, 20)
    
    # HTTP 어댑터 설정 개선 - 더 보수적인 설정
    adapter = requests.adapters.HTTPAdapter(
        pool_connections=10,  # 연결 풀 크기를 줄여서 안정성 향상
        pool_maxsize=20,      # 최대 연결 수 제한
        max_retries=3,
        pool_block=False
    )
    session.mount('https://', adapter)
    session.mount('http://', adapter)

    # 세션 기본 타임아웃 설정
    session.timeout = (10, 15)  # (연결 타임아웃, 읽기 타임아웃)

    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    })
    
    # 초기 연결 테스트 (선택사항)
    try:
        test_response = session.get('https://navercomp.wisereport.co.kr', timeout=(5, 10))
        logging.info("네이버 컴패스 연결 테스트 성공")
    except Exception as e:
        logging.warning(f"네이버 컴패스 연결 테스트 실패: {e}")
        # 연결 실패해도 계속 진행

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        fetcher = functools.partial(fetch_all_data_for_stock, session=session)
        
        results = list(tqdm(executor.map(fetcher, stock_codes), total=len(stock_codes), desc="전체 데이터 수집 중"))

    session.close()
        
    if not results:
        logging.warning("수집된 데이터가 없습니다.")
        return

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
    
    logging.info(f"데이터가 {excel_path}에 저장되었습니다.")

if __name__ == "__main__":
    load_dotenv()
    input_excel = os.getenv('INPUT_EXCEL', 'stock_list.xlsx')
    setup_logging_and_cleanup()
    process_stock_list(input_excel)
    logging.info("종료")