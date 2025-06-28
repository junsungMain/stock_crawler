from module.common import parse_num_value
import concurrent.futures
from tqdm import tqdm
import logging
import os

def get_theme_list(session):
    url = f"https://m.stock.naver.com/api/stocks/theme"
    page = 1
    page_size = 100
    all_themes = []

    # 1. 모든 테마 정보 가져오기
    while True:
        params = {
            'page': page,
            'pageSize': page_size
        }

        response = session.get(url, params=params)
        response.raise_for_status()
        response_data = response.json()

        theme_data = response_data.get('groups', [])
        if not theme_data:
            break
        all_themes.extend(theme_data)
        
        total_count = response_data.get('totalCount', 0)
        if page * page_size >= total_count:
            break
        page += 1

    # 2. 각 테마별 종목 리스트 병렬로 가져오기
    data = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(os.cpu_count() * 2, 20)) as executor:
        future_to_theme = {executor.submit(get_stock_list, theme['no'], theme['name'], session=session): theme for theme in all_themes}
        results = []
        desc = "테마별 종목 수집 중"
        for future in tqdm(concurrent.futures.as_completed(future_to_theme), total=len(all_themes), desc=desc):
            try:
                results.append(future.result())
            except Exception as exc:
                theme = future_to_theme[future]
                logging.error(f"{theme['name']} 테마 에러: {exc}")

    # 3. 결과 취합 (쓰레드 안전성을 위해 병렬 처리 후 순차적으로 취합)
    for stock_list_result in results:
        for code, stock_info in stock_list_result.items():
            if code not in data:
                data[code] = stock_info
            else:
                if '테마' in data[code] and stock_info['테마'] not in data[code]['테마']:
                    data[code]['테마'] += ', ' + stock_info['테마']
    
    return data


def get_stock_list(theme_no, theme_name, session):
    url = f"https://m.stock.naver.com/api/stocks/theme/{theme_no}"
    page = 1
    page_size = 100
    data = {}

    while True:
        params = {
            'page': page,
            'pageSize': page_size
        }
        response = session.get(url, params=params)
        response.raise_for_status()
        response_data = response.json()
        
        stocks_data = response_data.get('stocks', [])
        if not stocks_data:
            break

        for stock in stocks_data:
            if stock['itemCode'] not in data:
                data[stock['itemCode']] = {
                    '종목명': stock['stockName'],
                    '테마': theme_name,
                    '현재가': float(parse_num_value(stock['closePrice'])),
                    '전일대비': float(parse_num_value(stock['compareToPreviousClosePrice'])),
                    '등락률': round(float(parse_num_value(stock['fluctuationsRatio'])) / 100, 4),
                    '거래량': float(parse_num_value(stock['accumulatedTradingVolume'])),
                    '시가 총액(억)': float(parse_num_value(stock['marketValue'])),
                }
        
        total_count = response_data.get('totalCount', 0)
        if page * page_size >= total_count:
            break
        page += 1
    return data