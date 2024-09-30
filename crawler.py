import requests
import chardet
from bs4 import BeautifulSoup
import re
import datetime
import sqlite3
import json
import pytz  # Import for timezone handling

# SQLite 데이터베이스 연결 및 테이블 생성
def create_db():
    conn = sqlite3.connect('crawled_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            조회_시간 TEXT,
            우현상품권 TEXT,
            우천상품권 TEXT
        )
    ''')
    conn.commit()
    conn.close()

# 우천상품권 (wooticket) 크롤링
def crawl_wooticket():
    url = "http://www.wooticket.com/price_status.php"
    response = requests.get(url)

    # 페이지 인코딩 감지 및 설정
    encoding = chardet.detect(response.content)['encoding']
    response.encoding = encoding

    # HTML 파싱
    soup = BeautifulSoup(response.text, 'html.parser')

    # 모든 td 태그를 찾음
    tds = soup.find_all('td')

    # '농협하나로상품권(10만원권)' 텍스트를 포함한 td 찾기
    for i, td in enumerate(tds):
        div = td.find('div')
        if div and '농협하나로상품권(10만원권)' in div.get_text():
            # 바로 다음 td에서 매입가 추출
            next_td = tds[i + 1]
            price_div = next_td.find('div')
            if price_div:
                # 공백과 줄바꿈을 모두 제거하고 연속된 공백을 하나로 축소
                price = re.sub(r'\s+', ' ', price_div.get_text()).strip()
                # (7%) 제거
                price = price.split(' ')[0]  # 첫 번째 부분만 취득 (가격만)
                print(f"우천상품권 가격: {price}")  # Debugging output
                return price  # 가격 반환
    print("우천상품권 정보를 찾을 수 없습니다.")  # Debugging output
    return None  # 정보 없음

# 우현상품권 (wooh.co.kr) 크롤링
def crawl_wooh():
    url = "https://www.wooh.co.kr/shop/item.php?it_id=1595825248"
    response = requests.get(url)

    # 페이지 인코딩 감지 및 설정
    encoding = chardet.detect(response.content)['encoding']
    response.encoding = encoding

    # HTML 파싱
    soup = BeautifulSoup(response.text, 'html.parser')

    # sit_ov_tbl 클래스 테이블 찾기
    table = soup.find('table', class_='sit_ov_tbl')

    # color="#1560ed"인 font 태그 찾기
    blue_font = table.find('font', color='#1560ed')
    if blue_font:
        blue_text = blue_font.get_text().strip().replace('원', '')  # '원' 제거
        # 바로 밑의 color="#494949"인 font 태그 찾기
        grey_font = blue_font.find_next('font', color='#494949')
        if grey_font:
            grey_text = grey_font.get_text().strip()
            print(f"우현상품권 가격: {blue_text}")  # Debugging output
            return blue_text  # 가격 반환
    print("우현상품권 정보를 찾을 수 없습니다.")  # Debugging output
    return None  # 정보 없음

# 데이터베이스 생성
create_db()

# 크롤링 결과
wooticket_result = crawl_wooticket()
wooh_result = crawl_wooh()

# 현재 날짜 및 시간 추가 (UTC+9로 변환)
utc_now = datetime.datetime.now(pytz.utc)  # 현재 UTC 시간
korea_now = utc_now + datetime.timedelta(hours=9)  # UTC+9
now = korea_now.strftime("%Y-%m-%d %H:%M")

# 결과를 데이터베이스에 저장
if wooticket_result and wooh_result:
    conn = sqlite3.connect('crawled_data.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO price_data (조회_시간, 우현상품권, 우천상품권) VALUES (?, ?, ?)',
                   (now, wooh_result, wooticket_result))
    conn.commit()
    conn.close()
    print("데이터베이스에 결과 저장 완료.")  # Debugging output
else:
    print("데이터베이스에 저장할 데이터가 없습니다.")  # Debugging output

# DB 데이터를 JSON으로 변환
def save_data_to_json():
    conn = sqlite3.connect('crawled_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM price_data')
    rows = cursor.fetchall()

    # 데이터 리스트 생성
    data = []
    for row in rows:
        data.append({
            'id': row[0],
            '조회_시간': row[1],
            '우현상품권': row[2],
            '우천상품권': row[3],
        })

    # JSON 파일로 저장
    with open('data.json', 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    conn.close()
    print(f"data.json 파일 저장 완료. 데이터 개수: {len(data)}")  # Debugging output

# 데이터 JSON으로 저장
save_data_to_json()
