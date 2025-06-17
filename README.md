# Stock Financial Data Crawler

주식 재무 데이터를 수집하는 파이썬 패키지입니다.

## 설치 방법

```bash
pip install stock-crawler
```

## 사용 방법

```python
from stock_crawler import crawl_financial_data

# 종목코드 리스트
stock_codes = ['005930', '035720', '035420']  # 삼성전자, 카카오, NAVER

# 데이터 수집
crawl_financial_data(stock_codes)
```

## 기능

- 주식 재무 데이터 수집 (매출액, 당기순이익, 부채비율)
- 데이터를 엑셀 파일로 저장
- API 호출 간격 자동 조절

## 의존성

- Python 3.6 이상
- pandas
- requests
- openpyxl

## 라이선스

MIT License
