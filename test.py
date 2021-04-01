from selenium import webdriver
from datetime import datetime

import configparser
import os
import sys
import time

# 디바이스
current_device = 'pc'
if os.name == 'posix':
    # 리눅스
    current_device = 'linux'
elif os.name == 'nt':
    # PC
    current_device = 'pc'

print('[DEVICE] ' + current_device)

# 크롬 드라이버 로드
if current_device == 'pc':
    chromedriver_path = '../chromedriver.exe'
else :
    chromedriver_path = '/usr/local/bin/chromedriver'

# 크롬 불러오기
options = webdriver.ChromeOptions()
if current_device == 'linux':
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
else:
    # 유저 정보 추가
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36")

# 브라우저 설정
browser = webdriver.Chrome(
    executable_path=chromedriver_path,
    options= options
)

# 초이템 로그인
url = "http://choitemb2b.com/member/login.html"
browser.get(url)

# 지연 시간
delay_term = 1

# 로그인 정보 가져오기
config = configparser.ConfigParser()
config.read('./secure.ini')
login_id = config['choitem']['id']
login_pwd = config['choitem']['pwd']

# 로그인
input_id = browser.find_element_by_name('member_id')
if input_id is not None:
    input_id.send_keys(login_id)
    input_password = browser.find_element_by_name('member_passwd')
    input_password.send_keys(login_pwd)
    btn_login_submit = browser.find_element_by_css_selector("form[id^='member_form'] [onclick^='MemberAction.login']")
    btn_login_submit.click()

# 원하는 카테고리
category_list = [28]
# 1 ~ 6 페이지
page_list = range(1, 10)
for cate_no in category_list:
    # 브라우저 정보 기록
    browser_info = []
    # 페이지 이동 후 새탭 열기
    for _page in page_list:
        time.sleep(delay_term)
        link_cate = 'http://choitemb2b.com/product/list.html?cate_no={}&sort_method=5&page={}'.format(cate_no, _page)
        # 탭 이름
        tab_name = 'cate_no_{}_{}'.format(cate_no, _page)
        # 정보 추가
        browser_info.append(tab_name)
        # 새탭 열기
        script_str = "window.open(\"{}\", \"{}\", 'location=yes');".format(link_cate, tab_name)
        browser.execute_script(script_str)
        # 브라우저 정보 순서대로 윈도우 번호 호출
        move_tab_idx = browser_info.index(tab_name) + 1
        # 탭 변경
        browser.switch_to.window(browser.window_handles[move_tab_idx])
        # 상품 있는지 확인
        goods_items = browser.find_elements_by_css_selector('li.item.DB_rate')
        # 상품 없는 페이지 일경우
        if len(goods_items) == 0:
            # 브라우저 정보 삭제
            browser_info.remove(tab_name)
            browser.close()
            break

    # 페이지별 상품 링크 수집
    for tab_name in browser_info:
        time.sleep(delay_term)
        move_tab_idx = browser_info.index(tab_name) + 1
        browser.switch_to.window(browser.window_handles[move_tab_idx])

# browser.close()
sys.exit()