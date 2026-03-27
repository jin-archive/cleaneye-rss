from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import time
import re

def generate_rss():
    url = "https://job.cleaneye.go.kr/user/ypRecruitment.do"
    
    # 가상 브라우저(Headless Chrome) 설정
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get(url)
        time.sleep(5) # 자바스크립트 로딩 대기
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        fg = FeedGenerator()
        fg.title('클린아이 잡플러스 맞춤 채용공고')
        fg.link(href=url, rel='alternate')
        fg.description('채용/모집/공고 포함, 서류/면접/합격 제외 필터가 적용된 피드입니다.')
        fg.language('ko')
        
        job_links = soup.select('a')
        added_titles = set()
        count = 0
        
        # 필터 키워드 정의
        include_keywords = ['채용', '모집', '공고']
        exclude_keywords = ['서류', '면접', '합격']
        
        for a_tag in job_links:
            title = a_tag.get_text(strip=True)
            href = a_tag.get('href', '')
            onclick = a_tag.get('onclick', '')
            
            # 1. 제목 길이가 너무 짧으면 패스
            if len(title) <= 5:
                continue

            # 2. [포함 키워드] 검사: 하나라도 없으면 패스
            if not any(keyword in title for keyword in include_keywords):
                continue
            
            # 3. [제외 키워드] 검사: 하나라도 있으면 패스
            if any(keyword in title for keyword in exclude_keywords):
                continue

            # 4. 중복 수집 방지
            if title in added_titles:
                continue
            added_titles.add(title)
            
            # 링크 추출 로직
            link = url
            target_str = href if 'javascript:' in href else onclick
            match = re.search(r"'(.*?)'", target_str)
            if match:
                post_id = match.group(1)
                link = f"https://job.cleaneye.go.kr/user/ypRecruitmentDetail.do?recrutPbancSn={post_id}"
            elif href.startswith('http') or href.startswith('/'):
                link = "https://job.cleaneye.go.kr" + href if href.startswith('/') else href

            # RSS 항목 추가
            fe = fg.add_entry()
            fe.title(title)
            fe.link(href=link)
            fe.description(f"새로운 공고: {title}")
            fe.guid(link)
            count += 1
                
        fg.rss_file('rss.xml')
        print(f"✅ rss.xml 생성 완료! (필터링 매칭: {count}건)")
        
    except Exception as e:
        print(f"크롤링 중 에러 발생: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    generate_rss()
