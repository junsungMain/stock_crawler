import requests

def get_financial_data(stock_code):
    URL = f"https://m.stock.naver.com/api/stock/{stock_code}/finance/quarter"
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/json'
    }
    response = requests.get(URL, headers=headers)
    response.raise_for_status()
    
    row_list = response.json()['financeInfo']['rowList']
    data = {}
    
    for key in row_list:
        if key['title'] == '매출액':
            revenue_data = key['columns']
            revenue_data = sorted(revenue_data.items(), key=lambda x: x[0])[:4]
            # 매출액 값을 숫자로 변환하고 키를 순서대로 변경
            for i, (k, v) in enumerate(revenue_data):
                value = v['value']
                if value == '-':
                    value = '0'
                data[f'매출액(억) | {i+1}'] = float(value.replace(',', ''))
                
        if key['title'] == '당기순이익':
            net_income_data = key['columns']
            net_income_data = sorted(net_income_data.items(), key=lambda x: x[0])[:4]
            # 당기순이익 값을 숫자로 변환하고 키를 순서대로 변경
            for i, (k, v) in enumerate(net_income_data):
                value = v['value']
                if value == '-':
                    value = '0'
                data[f'당기순이익(억) | {i+1}'] = float(value.replace(',', ''))
                
        if key['title'] == '부채비율':
            debt_ratio_data = key['columns']
            debt_ratio_data = sorted(debt_ratio_data.items(), key=lambda x: x[0])[:4]
            # 부채비율 값을 숫자로 변환하고 키를 순서대로 변경
            for i, (k, v) in enumerate(debt_ratio_data):
                value = v['value']
                if value == '-':
                    value = '0'
                data[f'부채비율(%) | {i+1}'] = float(value.replace(',', ''))

        if key['title'] == 'ROE':
            roe_data = key['columns']
            roe_data = sorted(roe_data.items(), key=lambda x: x[0])[:4]
            value = roe_data[-1][1]['value']
            if value == '-':
                value = '0'
            data[f'ROE(%)'] = float(value.replace(',', ''))

        if key['title'] == 'PBR':
            pbr_data = key['columns']
            pbr_data = sorted(pbr_data.items(), key=lambda x: x[0])[:4]
            value = pbr_data[-1][1]['value']
            if value == '-':
                value = '0'
            data[f'PBR(배)'] = float(value.replace(',', ''))
                        
        if key['title'] == 'PER':
            per_data = key['columns']
            per_data = sorted(per_data.items(), key=lambda x: x[0])[:4]
            value = per_data[-1][1]['value']
            if value == '-':
                value = '0'
            data[f'PER(배)'] = float(value.replace(',', ''))

    return data

def get_financial_extra_data(stock_code):
    data = {}
    try:
        URL = f'https://navercomp.wisereport.co.kr/company/chart/c1030001.aspx?cmp_cd={stock_code}&frq=Q&rpt=ISM&finGubun=MAIN&chartType=svg'
        
        response = requests.get(URL, timeout=5)
        
        if response.status_code == 200:
            row_list = response.json()['chartData2']['series']
            
            for key in row_list:
                if key['name'] == '영업이익증가율':
                    profit_data = key['data']
                    for idx, value in enumerate(profit_data):
                        if idx == 4:
                            break
                        if value == 'null':
                            value = '0'
                        data[f'영업이익증가율(%) | {idx+1}'] = value
                    break;
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
        return data
    