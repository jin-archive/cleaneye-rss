import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import re
from urllib.parse import urljoin
import urllib3

# 공공기관 사이트 SSL 인증서 경고 무시
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def generate_rss():
    # 클린아이 잡플러스 채용공고 URL
    url = "https://job.cleaneye.go.kr/user/ypRecruitment.do"
    
    # 일반 브라우저로 위장하여 접근 차단 우회
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # RSS 피드 기본 정보 설정
    fg = FeedGenerator()
    fg.title('클린아이 잡플러스 채용공고')
    fg.link(href=url, rel='alternate')
    fg.description('지방 공공기관 채용정보(클린아이 잡플러스) 최신 공고 RSS 피드입니다.')
    fg.language('ko')
    
    # 채용공고 목록 추출 
    job_links = soup.select('a') 
    
    added_links = set() # 중복 방지용
    
    for a_tag in job_links:
        title = a_tag.get_text(strip=True)
        href = a_tag.get('href', '')
        onclick = a_tag.get('onclick', '')
        
        # 제목이 비어있거나 너무 짧은 링크(메뉴 등)는 제외
        if len(title) < 5:
            continue
            
        link = ""
        
        # 자바스크립트 함수로 이동하거나 특정 쿼리스트링이 포함된 경우 링크 파싱
        if 'javascript:' in href or onclick:
            target_str = href if 'javascript:' in href else onclick
            match = re.search(r"'(.*?)'", target_str)
            if match:
                post_id = match.group(1)
                link = f"https://job.cleaneye.go.kr/user/ypRecruitmentDetail.do?recrutPbancSn={post_id}"
        elif '/user/ypRecruitmentDetail' in href or 'Sn=' in href:
            link = urljoin("https://job.cleaneye.go.kr", href)
            
        # 오타 수정됨: 'not 세' -> 'not in'
        if link and link not in added_links:
            added_links.add(link)
            
            fe = fg.add_entry()
            fe.title(title)
            fe.link(href=link)
            fe.description(f"새로운 채용 공고가 등록되었습니다: {title}")
            fe.guid(link)
            
    # RSS 파일을 xml 포맷으로 저장
    fg.rss_file('rss.xml')
    print(f"rss.xml 파일이 성공적으로 생성되었습니다. (총 {len(added_links)}건)")

if __name__ == "__main__":
    generate_rss()
