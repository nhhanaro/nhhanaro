import cloudscraper
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime

# 웹에서 데이터 크롤링
def crawl_wooticket():
    url = "http://www.wooticket.com/price_status.php"
    scraper = cloudscraper.create_scraper()  # Cloudflare 보호 우회
    response = scraper.get(url)
    response.encoding = 'euc-kr'  # 페이지 인코딩 설정
    soup = BeautifulSoup(response.text, 'html.parser')
    rows = soup.find_all('tr', attrs={'valign': 'middle'})
    for row in rows:
        tds = row.find_all('td')
        if len(tds) >= 4:
            name_td = tds[0]
            name_div = name_td.find('div')
            if name_div:
                name_text = name_div.get_text(strip=True)
                if "농협하나로상품권(10만원권)" in name_text:
                    price_td = tds[1]
                    price_div = price_td.find('div')
                    if price_div:
                        price_text = price_div.get_text(strip=True)
                        price = re.match(r'[\d,]+', price_text).group()  # 숫자만 추출
                        return price
    return None

# 데이터를 JSON 파일로 저장
def save_to_json(data):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # 타임스탬프 생성
    filename = f"data_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({"price": data}, f, ensure_ascii=False, indent=4)
    print(f"Data saved to {filename}")

# 실행
if __name__ == "__main__":
    price = crawl_wooticket()
    if price:
        save_to_json(price)
    else:
        print("Failed to retrieve data.")
