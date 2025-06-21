import requests
from common import parse_num_value

def get_financial_data(stock_code):
    URL = f"https://m.stock.naver.com/api/stock/{stock_code}/finance/quarter"
    response = requests.get(URL)
    response.raise_for_status()
    response_data = response.json()['financeInfo']['rowList']
    
    data = {}     
    for key in response_data:
        if key['title'] == '매출액':
            revenue_data = key['columns']
            revenue_data = sorted(revenue_data.items(), key=lambda x: x[0])[:4]
            for i, (k, v) in enumerate(revenue_data):
                data[f'매출액(억) | {i+1}'] = float(parse_num_value(v['value']))
            continue
                    
        if key['title'] == '당기순이익':
            net_income_data = key['columns']
            net_income_data = sorted(net_income_data.items(), key=lambda x: x[0])[:4]
            for i, (k, v) in enumerate(net_income_data):
                data[f'당기순이익(억) | {i+1}'] = float(parse_num_value(v['value']))
            continue

        if key['title'] == '부채비율':
            debt_ratio_data = key['columns']
            debt_ratio_data = sorted(debt_ratio_data.items(), key=lambda x: x[0])[:4]
            for i, (k, v) in enumerate(debt_ratio_data):
                data[f'부채비율(%) | {i+1}'] = float(parse_num_value(v['value']))
            continue

        if key['title'] == 'ROE':
            roe_data = key['columns']
            roe_data = sorted(roe_data.items(), key=lambda x: x[0])[:4]
            data[f'ROE(%)'] = float(parse_num_value(roe_data[-1][1]['value']))
            continue

        if key['title'] == 'PBR':
            pbr_data = key['columns']
            pbr_data = sorted(pbr_data.items(), key=lambda x: x[0])[:4]
            data[f'PBR(배)'] = float(parse_num_value(roe_data[-1][1]['value']))
            continue
                            
        if key['title'] == 'PER':
            per_data = key['columns']
            per_data = sorted(per_data.items(), key=lambda x: x[0])[:4]
            data[f'PER(배)'] = float(parse_num_value(roe_data[-1][1]['value']))
    return data


def get_financial_extra_data(stock_code):
    URL = f'https://navercomp.wisereport.co.kr/company/chart/c1030001.aspx?cmp_cd={stock_code}&frq=Q&rpt=ISM&finGubun=MAIN&chartType=svg'
    response = requests.get(URL, timeout=5)
    response.raise_for_status()
    
    data = {}
    if response.status_code == 200:
        response_data = response.json()['chartData2']['series']
            
        for key in response_data:
            if key['name'] == '영업이익증가율':
                profit_data = key['data']
                for idx, value in enumerate(profit_data):
                    if idx == 4:
                        break
                    if value == 'null':
                        value = '0'
                    data[f'영업이익증가율(%) | {idx+1}'] = value
                break;

    return data
    