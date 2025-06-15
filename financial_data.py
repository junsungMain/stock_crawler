import yfinance as yf
import pandas as pd
from datetime import datetime

def get_last_year_quarters_financials(stock_code, quarters=[3, 6, 9, 12], delay=1):
    current_year = datetime.now().year
    last_year = current_year - 1
    
    if stock_code.isdigit():
        symbol = f"{stock_code}.KS"
    else:
        symbol = stock_code
    
    try:
        ticker = yf.Ticker(symbol)
        
        # 손익계산서 (매출액, 영업이익, 당기순이익)
        income_stmt = ticker.quarterly_income_stmt
        
        # 대차대조표 (부채비율 계산용)
        balance_sheet = ticker.quarterly_balance_sheet
        
        if income_stmt.empty or balance_sheet.empty:
            return None
        
        # 결과 저장할 딕셔너리
        financial_data = {}
        
        # 작년 지정된 분기만 필터링
        target_dates = []
        for date in income_stmt.columns:
            if date.year == last_year and date.month in quarters:
                target_dates.append(date)
        
        if not target_dates:
            print(f"{symbol} {last_year}년 {quarters} 분기 데이터 없음")
            return None
        
        # 날짜별로 데이터 정리
        for date in target_dates:
            try:
                # 1. 매출액 찾기
                revenue = None
                revenue_keywords = ['Total Revenue', 'Revenue', 'Net Sales', 'Operating Revenue']
                for keyword in revenue_keywords:
                    matching_rows = [row for row in income_stmt.index if keyword in str(row)]
                    if matching_rows:
                        revenue = income_stmt.loc[matching_rows[0], date]
                        break
                
                # 2. 영업이익 증가율
                operating_income = None
                operating_keywords = ['quarterly_income_stmt']
                for keyword in operating_keywords:
                    matching_rows = [row for row in income_stmt.index if keyword in str(row)]
                    if matching_rows:
                        operating_income = income_stmt.loc[matching_rows[0], date]
                        break
                
                # 3. 당기순이익 찾기
                net_income = None
                net_keywords = ['Net Income', 'Net Profit', 'Profit']
                for keyword in net_keywords:
                    matching_rows = [row for row in income_stmt.index if keyword in str(row)]
                    if matching_rows:
                        net_income = income_stmt.loc[matching_rows[0], date]
                        break
                
                # 4. 부채비율 계산 (총부채 / 총자산 * 100)
                debt_ratio = None
                if date in balance_sheet.columns:
                    total_debt_keywords = ['Total Debt', 'Total Liabilities']
                    total_assets_keywords = ['Total Assets']
                    
                    total_debt = None
                    total_assets = None
                    
                    for keyword in total_debt_keywords:
                        matching_rows = [row for row in balance_sheet.index if keyword in str(row)]
                        if matching_rows:
                            total_debt = balance_sheet.loc[matching_rows[0], date]
                            break
                    
                    for keyword in total_assets_keywords:
                        matching_rows = [row for row in balance_sheet.index if keyword in str(row)]
                        if matching_rows:
                            total_assets = balance_sheet.loc[matching_rows[0], date]
                            break
                    
                    if total_debt is not None and total_assets is not None and total_assets != 0:
                        debt_ratio = (total_debt / total_assets) * 100
                
                # 분기 결정 (월 기준)
                quarter_name = str(date.month // 3)
                
                # 데이터 저장
                financial_data.update({
                    '매출액(억) | '+quarter_name: round(revenue / 100_000_000, 1) if pd.notna(revenue) else None,
                    '영업이익증가율(%) (억) | '+quarter_name: round(operating_income, 1) if pd.notna(operating_income) else None,
                    '당기순이익(억) | '+quarter_name: round(net_income / 100_000_000, 1) if pd.notna(net_income) else None,
                    '부채비율(%) | '+quarter_name: round(debt_ratio, 2) if pd.notna(debt_ratio) else None
                })
                
            except Exception as e:
                print(f"{date} 데이터 처리 중 오류: {e}")
                continue
        
        return financial_data  
        
    except Exception as e:
        print(f"{symbol} 데이터 가져오기 실패: {e}")
        return None
