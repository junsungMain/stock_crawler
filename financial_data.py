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