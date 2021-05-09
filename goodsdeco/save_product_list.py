# 굿즈 데코 상품 목록 가져오기
# 굿즈 데코 상품 목록 가져오기
# 굿즈 데코 상품 목록 가져오기

from selenium import webdriver

import datetime
import configparser
import os
import sys
import time
import json

# 사이트 코드
shop_code = 'goodsdeco'
# 메인 URL
main_host = 'http://www.goodsdeco.com'
# 로그인 경로
login_page = '/member/login.php'
# 로그인 아이디 입력 폼 name
formName_Login = 'loginId'
# 로그인 비밀번호 입력 폼 name
formName_Password = 'loginPwd'
# 로그인 버튼 선택자
login_btn_selector = "#formLogin button[type='submit']"

# 목록 가져올 페이지
list_page_url = 'http://www.goodsdeco.com/goods/goods_list.php?cateCd=004001'
# 상품 element
product_list_selector = '.item_basket_type ul li .item_cont'
# 상품 정보 수정 영역 << 해당 영역 검색후 수정 필요

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
    chromedriver_path = '../../chromedriver.exe'
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

# 지연 시간
delay_term = 1

# 로그인
url = main_host + login_page
browser.get(url)

# 로그인 정보 가져오기
config = configparser.ConfigParser()
config.read('../secure.ini')
login_id = config[shop_code]['id']
login_pwd = config[shop_code]['pwd']

# 로그인
input_id = browser.find_element_by_name(formName_Login)
if input_id is not None:
    input_id.send_keys(login_id)
    input_password = browser.find_element_by_name(formName_Password)
    input_password.send_keys(login_pwd)
    # 일반 클릭
    # btn_login_submit = browser.find_element_by_css_selector(login_btn_selector)
    # btn_login_submit.click()
    # 클릭 로그인 불가시 스크립트
    login_script = '$(".login_input_sec button").click();'
    browser.execute_script(login_script)
    print('로그인 완료')

time.sleep(delay_term)
# 브라우저 정보 기록
browser_info = []
browser_info.clear()
browser.switch_to.window(browser.window_handles[0])

# 탭 이름
print('페이지 이동 {}'.format(list_page_url))
tab_name = 'list_page'
# 정보 추가
browser_info.append(tab_name)
# 새탭 열기
script_str = "window.open(\"{}\", \"{}\", 'location=yes');".format(list_page_url, tab_name)
browser.execute_script(script_str)
# 브라우저 정보 순서대로 윈도우 번호 호출
move_tab_idx = browser_info.index(tab_name) + 1
# 탭 변경
browser.switch_to.window(browser.window_handles[move_tab_idx])
# 상품 있는지 확인
goods_items = browser.find_elements_by_css_selector(product_list_selector)
# 상품 없는 페이지 일경우
if len(goods_items) == 0:
    # 브라우저 정보 삭제
    browser_info.remove(tab_name)
    print('상품이 없습니다')
    browser.close()

# 페이지별 상품 링크 수집
goods_links = {}
for tab_name in browser_info:
    # time.sleep(delay_term)
    move_tab_idx = browser_info.index(tab_name) + 1
    browser.switch_to.window(browser.window_handles[move_tab_idx])
    goods_wrap = browser.find_elements_by_css_selector(product_list_selector)
    print('상품 링크 수집 시작 {}'.format(move_tab_idx))
    # 상품 정보 수정 영역
    for goods_html in goods_wrap:
        try:
            # 링크
            el_product_link = goods_html.find_element_by_css_selector('a.btn_detail')
            product_link = el_product_link.get_attribute('href')
            # 상품번호
            product_no_attr = goods_html.find_element_by_css_selector('.item_link .btn_basket_cart')
            product_no = product_no_attr.get_attribute('data-goods-no')
            goods_links[product_no] = product_link
        except:
            continue

jsonString = json.dumps(goods_links)

# 파일로 저장
file_path = "../_data/{}/".format(shop_code)
if os.path.exists(file_path) == False:
    os.makedirs(file_path)
now = datetime.datetime.now()
w_time = now.strftime('%Y%m%d%H%M')
file_name = '{}_{}.json'.format(shop_code, w_time)
file_full_path = file_path + file_name
if os.path.exists(file_full_path) == True:
    os.remove(file_full_path)
f = open(file_full_path, 'w')
f.write(jsonString)
f.close()
print("[SAVE] {}".format(file_name))

# 새탭 브라우저 종료
for tab_info in browser_info:
    browser.switch_to.window(browser.window_handles[1])
    browser.close()

# 메인 브라우저 닫기
browser.switch_to.window(browser.window_handles[0])
browser.close()
# 드라이버 종료
browser.quit()
sys.exit()