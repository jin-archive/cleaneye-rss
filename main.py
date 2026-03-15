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
    # (주의: 실제 웹사이트의 HTML 구조를 보고 'table tbody tr' 또는 'ul.job_list li' 등으로 변경해야 할 수 있습니다)
    # 아래는 리스트형/테이블형을 모두 포괄할 수 있도록 포괄적인 a 태그를 탐색하는 방식입니다.
    job_links = soup.select('a') 
    
    added_links = set() # 중복 방지용
    
    for a_tag in job_links:
        title = a_tag.get_text(strip=True)
        href = a_tag.get('href', '')
        onclick = a_tag.get('onclick', '')
        
        # 제목이 비어있거나 너무 짧은 링크(메뉴 등)는 제외
        if len(title) < 5:
            continue
            
        # 채용 공고 상세페이지로 이동하는 링크 패턴 찾기
        # 주로 javascript 함수로 이동하거나 특정 쿼리스트링이 포함됨
        link = ""
        
        if 'javascript:' in href or onclick:
            # 예: fn_view('2024001') 같은 자바스크립트 함수에서 ID값 추출
            target_str = href if 'javascript:' in href else onclick
            match = re.search(r"'(.*?)'", target_str)
            if match:
                post_id = match.group(1)
                # 실제 상세페이지 URL 구조에 맞게 조합 (예시)
                link = f"https://job.cleaneye.go.kr/user/ypRecruitmentDetail.do?recrutPbancSn={post_id}"
        elif '/user/ypRecruitmentDetail' in href or 'Sn=' in href:
            link = urljoin("https://job.cleaneye.go.kr", href)
            
        # 공고 링크로 추정되고, 아직 추가하지 않은 항목이면 RSS에 추가
        if link and link not 세 added_links:
            added_links.add(link)
            
            fe = fg.add_entry()
            fe.title(title)
            fe.link(href=link)
            # 본문에 제목을 한 번 더 노출 (필요 시 기관명 파싱 로직 추가 가능)
            fe.description(f"새로운 채용 공고가 등록되었습니다: {title}")
            fe.guid(link)
            
    # RSS 파일을 xml 포맷으로 저장
    fg.rss_file('rss.xml')
    print("rss.xml 파일이 성공적으로 생성되었습니다. (총 {}건)".format(len(added_links)))

if __name__ == "__main__":
    generate_rss()
