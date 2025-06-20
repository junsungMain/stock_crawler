import pandas as pd
import concurrent.futures
from tqdm import tqdm
from openpyxl import load_workbook
from financial_data import *
from main_data import *
from new_and_disclosure import *
import time
import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

def retry_on_failure(func, max_retries=3, delay=1):
    def wrapper(*args, **kwargs):
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"Error in {func.__name__} for args {args}: {str(e)}")
                    return None
                print(f"재시도 중... (시도 {attempt + 1}/{max_retries})")
                time.sleep(delay)
        return None
    return wrapper

def process_stock_list(excel_path):
    # 엑셀 파일 읽기 (기존 df)
    df = pd.read_excel(excel_path, engine='openpyxl')
    
    # 결과를 저장할 리스트
    results = []
    
    # 종목코드 리스트 준비
    stock_codes = [str(code).zfill(6) for code in df['종목코드']]
    
    # 함수에 재시도 로직 적용
    get_stock_data_with_retry = retry_on_failure(get_stock_data)
    get_financials_with_retry = retry_on_failure(get_financial_data)
    get_disclosure_with_retry = retry_on_failure(get_latest_disclosure)
    get_news_with_retry = retry_on_failure(get_latest_news)
    get_finacial_extra_with_retry = retry_on_failure(get_financial_extra_data)
    
    with concurrent.futures.ThreadPoolExecutor(os.cpu_count() * 2) as executor:
        stock_futures = list(tqdm(
            executor.map(get_stock_data_with_retry, stock_codes),
            total=len(stock_codes),
            desc="주식 데이터 수집 중"
        ))

        financial_futures = list(tqdm(
            executor.map(get_financials_with_retry, stock_codes),
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
    session.get(main_url, timeout=5)

    with concurrent.futures.ThreadPoolExecutor(5) as executor:
        financial_extra_futures = list(tqdm(
            executor.map(get_finacial_extra_with_retry, stock_codes),
            total=len(stock_codes),
            desc="재무 기타 데이터 수집 중"
        ))

        new_futures = list(tqdm(
            executor.map(get_news_with_retry, stock_codes),
            total=len(stock_codes),
            desc="뉴스 데이터 수집 중"
        ))
        
        disclosure_futures = list(tqdm(
            executor.map(get_disclosure_with_retry, stock_codes),
            total=len(stock_codes),
            desc="공시 데이터 수집 중"
        ))

    # 결과 병합
    for stock_code, stock_data, financial_data, financial_extra_data, news_data, disclosure_data in zip(
        stock_codes, stock_futures, financial_futures,financial_extra_futures, new_futures, disclosure_futures):
        
        combined_data = {'종목코드': stock_code}          

        if stock_data:
            combined_data.update(stock_data)
        
        if financial_data:    
            combined_data.update(financial_data)

        if financial_extra_data:
            combined_data.update(financial_extra_data)
        
        if news_data:
            combined_data.update(news_data)

        if disclosure_data:
            combined_data.update(disclosure_data)
        
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

def setup_logging_and_cleanup(log_dir="logs", days_to_keep=7):
    # 로그 디렉토리 생성
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 오늘 날짜로 로그 파일명 생성
    log_filename = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")
    
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # 오래된 로그 파일 삭제
    now = datetime.now()
    for fname in os.listdir(log_dir):
        fpath = os.path.join(log_dir, fname)
        if os.path.isfile(fpath):
            try:
                # 파일명에서 날짜 추출
                date_str = fname.split(".")[0]
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                if now - file_date > timedelta(days=days_to_keep):
                    os.remove(fpath)
                    logging.info(f"오래된 로그 파일 삭제: {fname}")
            except Exception as e:
                logging.warning(f"로그 파일 삭제 중 오류: {fname}, {e}")

if __name__ == "__main__":
    load_dotenv()
    input_excel = os.getenv('INPUT_EXCEL', 'stock_list.xlsx')
    setup_logging_and_cleanup()
    process_stock_list(input_excel)
    print("종료")