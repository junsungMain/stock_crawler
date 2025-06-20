import requests
import time

def get_financial_data(stock_code):
    URL = f"https://m.stock.naver.com/api/stock/{stock_code}/finance/quarter"
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/json'
    }
    response = requests.get(URL, headers=headers)
    response.raise_for_status()
    
    row_list = response.json()['financeInfo']['rowList']
    financial_dict = {}
    
    for key in row_list:
        if key['title'] == '매출액':
            revenue_data = key['columns']
            revenue_data = sorted(revenue_data.items(), key=lambda x: x[0])[:4]
            # 매출액 값을 숫자로 변환하고 키를 순서대로 변경
            for i, (k, v) in enumerate(revenue_data):
                value = v['value']
                if value == '-':
                    value = '0'
                financial_dict[f'매출액(억) | {i+1}'] = float(value.replace(',', ''))
                
        if key['title'] == '당기순이익':
            net_income_data = key['columns']
            net_income_data = sorted(net_income_data.items(), key=lambda x: x[0])[:4]
            # 당기순이익 값을 숫자로 변환하고 키를 순서대로 변경
            for i, (k, v) in enumerate(net_income_data):
                value = v['value']
                if value == '-':
                    value = '0'
                financial_dict[f'당기순이익(억) | {i+1}'] = float(value.replace(',', ''))
                
        if key['title'] == '부채비율':
            debt_ratio_data = key['columns']
            debt_ratio_data = sorted(debt_ratio_data.items(), key=lambda x: x[0])[:4]
            # 부채비율 값을 숫자로 변환하고 키를 순서대로 변경
            for i, (k, v) in enumerate(debt_ratio_data):
                value = v['value']
                if value == '-':
                    value = '0'
                financial_dict[f'부채비율(%) | {i+1}'] = float(value.replace(',', ''))

        if key['title'] == 'ROE':
            roe_data = key['columns']
            roe_data = sorted(roe_data.items(), key=lambda x: x[0])[:4]
            value = roe_data[-1][1]['value']
            if value == '-':
                value = '0'
            financial_dict[f'ROE(%)'] = float(value.replace(',', ''))

        if key['title'] == 'PBR':
            pbr_data = key['columns']
            pbr_data = sorted(pbr_data.items(), key=lambda x: x[0])[:4]
            value = pbr_data[-1][1]['value']
            if value == '-':
                value = '0'
            financial_dict[f'PBR(배)'] = float(value.replace(',', ''))
                        
        if key['title'] == 'PER':
            per_data = key['columns']
            per_data = sorted(per_data.items(), key=lambda x: x[0])[:4]
            value = per_data[-1][1]['value']
            if value == '-':
                value = '0'
            financial_dict[f'PER(배)'] = float(value.replace(',', ''))

    return financial_dict

def get_financial_extra_data(stock_code):
    session = requests.Session()

    # 브라우저처럼 보이도록 헤더 설정
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
    try:
        main_url = 'https://navercomp.wisereport.co.kr/'
        session.get(main_url, timeout=5)        
        
        target_url = f'https://navercomp.wisereport.co.kr/company/chart/c1030001.aspx?cmp_cd={stock_code}&frq=Q&rpt=ISM&finGubun=MAIN&chartType=svg'
        
        session.headers.update({
            'Referer': main_url
        })
        
        response = session.get(target_url, timeout=5)
        
        if response.status_code == 200:
            row_list = response.json()['chartData2']['series']
            financial_dict = {}
            
            for key in row_list:
                if key['name'] == '영업이익증가율':

                    revenue_data = key['data']
                    for idx, value in enumerate(revenue_data):
                        if idx == 4:
                            break
                        if value == 'null':
                            value = '0'
                        financial_dict[f'영업이익증가율(%) | {idx+1}'] = value
                    break;
            return financial_dict
        else:
            print(f"실패: 상태코드 {response.status_code}")
            print("응답 헤더:", dict(response.headers))

    except requests.exceptions.Timeout:
        print("타임아웃 오류 발생")
    except requests.exceptions.ConnectionError:
        print("연결 오류 발생")
    except Exception as e:
        print(f"기타 오류: {e}")
    finally:
        session.close()
