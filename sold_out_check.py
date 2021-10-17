import re

from selenium import webdriver
from datetime import datetime

import configparser
import os
import sys
import time
import json
import requests

# 디바이스
current_device = 'pc'
if os.name == 'posix':
    # 리눅스
    current_device = 'linux'
elif os.name == 'nt':
    # PC
    current_device = 'pc'

print('[DEVICE] {}'.format(current_device))

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
    print('로그인 완료')

# 상품 목록 추출
post_url = 'http://parkstore.test/shop_manage/shop_sold_out'
response = requests.post(post_url)
shop_sold_check_list = json.loads(response.text)
browser_info = []
browser_info.clear()
tab_no = 0
for product_info in shop_sold_check_list:
    time.sleep(delay_term)
    tab_no = tab_no + 1
    print(tab_no)

    product_code = product_info['product_code']

    # 사이트 접속하여 품절 확인
    link_cate = 'https://choitemb2b.com/product/search.html?banner_action=&keyword={}'.format(product_code)
    # 탭 이름
    tab_name = 'tab_no_{}'.format(tab_no)
    # 정보 추가
    browser_info.append(tab_name)
    # 새탭 열기
    script_str = "window.open(\"{}\", \"{}\", 'location=yes');".format(link_cate, tab_name)
    browser.execute_script(script_str)
    # 브라우저 정보 순서대로 윈도우 번호 호출
    move_tab_idx = browser_info.index(tab_name) + 1
    # 탭 변경
    browser.switch_to.window(browser.window_handles[1])

    # 상품 있는지 확인
    goods_items = browser.find_elements_by_css_selector('li.item.DB_rate')
    # 상품 없는 페이지 일경우
    if len(goods_items) == 0:
        # 브라우저 정보 삭제
        browser_info.remove(tab_name)
        browser.switch_to.window(browser.window_handles[1])
        browser.close()
        browser.switch_to.window(browser.window_handles[0])
        continue

    good_info = goods_items[0]
    goods_link_btn = good_info.find_element_by_css_selector('.name a')
    goods_link_btn.click()

    sold_out = False
    el_product_option_li = browser.find_elements_by_css_selector('select[product_type="product_option"]')
    if len(el_product_option_li) > 0 :
        for product_option in el_product_option_li:
            p_t = product_option.text
            # 품절
            품절 = re.findall("품절", p_t)
            if len(품절) > 0 :
                # 품절임
                sold_out = True
                break

    if sold_out == True :
        # 스토어 품절로 교체
        post_url = 'http://parkstore.test/shop_manage/set_shop_sold_out/{}/y'.format(product_code)
        response = requests.post(post_url)
        shop_sold_out_return = json.loads(response.text)
        _print = '{} {}'.format(product_code, shop_sold_out_return['result'])
        print(_print)

    browser.switch_to.window(browser.window_handles[1])
    browser.close()
    browser.switch_to.window(browser.window_handles[0])

# 새탭 브라우저 종료
# for tab_info in browser_info:
#     browser.switch_to.window(browser.window_handles[1])
#     browser.close()

# 메인 브라우저 닫기
browser.switch_to.window(browser.window_handles[0])
browser.close()
browser.quit()

# 도매처 품절이지만 스토어 품절 아닌 상품 목록
post_url = 'http://parkstore.test/shop_manage/fetch_product_list'
response = requests.post(post_url)
fetch_product_list = json.loads(response.text)
print("[품절 확인 필요 상품 코드]")
for fetch_list in fetch_product_list:
    _print = '{}'.format(fetch_list['product_code'])
    print(_print)

# 종료
sys.exit()