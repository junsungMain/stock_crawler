from OpenDartReader import OpenDartReader
dart = OpenDartReader('f0cc093652086b8dadbaf87dcb3156c7fad9c78e')

# 네이버 2023년, 2024년 재무제표 가져오기
fs_2024 = dart.finstate('035420', 2024)
fs_2023 = dart.finstate('035420', 2023)

# 영업이익 증가율 직접 계산
operating_income_2024 = fs_2024.loc[fs_2024['항목'] == '영업이익', '2024'].values[0]
operating_income_2023 = fs_2023.loc[fs_2023['항목'] == '영업이익', '2023'].values[0]
growth_rate = ((operating_income_2024 - operating_income_2023) / operating_income_2023) * 100

