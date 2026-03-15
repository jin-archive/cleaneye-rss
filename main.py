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
    chrome_options.add_argument('--headless') # 화면을 띄우지 않음
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # 웹페이지 접속
        driver.get(url)
        # 자바스크립트로 데이터가 불러와질 때까지 5초 대기
        time.sleep(5) 
        
        # 로딩이 끝난 후의 HTML 소스 가져오기
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # RSS 기본 설정
        fg = FeedGenerator()
        fg.title('클린아이 잡플러스 채용공고')
        fg.link(href=url, rel='alternate')
        fg.description('지방 공공기관 채용정보(클린아이 잡플러스) 최신 공고 RSS 피드입니다.')
        fg.language('ko')
        
        # <a> 태그를 모두 탐색하여 공고 제목 추출
        job_links = soup.select('a')
        added_titles = set()
        count = 0
        
        for a_tag in job_links:
            title = a_tag.get_text(strip=True)
            href = a_tag.get('href', '')
            onclick = a_tag.get('onclick', '')
            
            # 텍스트에 '채용', '공고', '모집' 등이 포함된 링크만 선별
            if len(title) > 8 and any(keyword in title for keyword in ['채용', '공고', '모집', '채용공고']):
                
                # 중복 수집 방지
                if title in added_titles:
                    continue
                added_titles.add(title)
                
                # 링크 파싱 (정확한 ID를 추출하거나, 실패 시 메인 페이지로 연결)
                link = url
                target_str = href if 'javascript:' in href else onclick
                match = re.search(r"'(.*?)'", target_str)
                if match:
                    # 추출한 ID 번호로 직접 연결되는 URL 조합 (사이트 구조에 따라 다를 수 있음)
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
                
        # 파일 저장
        fg.rss_file('rss.xml')
        print(f"✅ rss.xml 생성 완료! (총 {count}개의 공고를 찾았습니다.)")
        
    except Exception as e:
        print(f"크롤링 중 에러 발생: {e}")
    finally:
        driver.quit() # 브라우저 종료 필수

if __name__ == "__main__":
    generate_rss()
