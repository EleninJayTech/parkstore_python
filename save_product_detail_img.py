from selenium import webdriver

import configparser
import json
import os
import sys
import time
import requests

from requests import get  # to make GET request

def download(url, file_name):
    with open(file_name, "wb") as file:   # open in binary mode
        response = get(url)               # get request
        file.write(response.content)      # write to file

shop_code = 'choitem'
cate_no = 28

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
target_host = 'http://choitemb2b.com'
url = "http://choitemb2b.com/member/login.html"
browser.get(url)

# 지연 시간
delay_term = 1

# 로그인 정보 가져오기
config = configparser.ConfigParser()
config.read('./secure.ini')
login_id = config['choitem']['id']
login_pwd = config['choitem']['pwd']
encrypt_key = config['choitem']['encrypt_key']

# 로그인
input_id = browser.find_element_by_name('member_id')
if input_id is not None:
    input_id.send_keys(login_id)
    input_password = browser.find_element_by_name('member_passwd')
    input_password.send_keys(login_pwd)
    btn_login_submit = browser.find_element_by_css_selector("form[id^='member_form'] [onclick^='MemberAction.login']")
    btn_login_submit.click()
    print('로그인 완료')

PK_CODE = '20210503011059'

# 이미지 다운받을 상품 목록 추출
post_url = 'http://parkstore.test/api/detail_img/{}'.format(PK_CODE)
data = {'encrypt_key': 'e8b6a94f577bd529c2e67da6aa449219'}
response = requests.post(post_url, data=data)
product_list = json.loads(response.text)

for product_no in product_list:
    print('상품 페이지로 이동:{}'.format(product_no))
    time.sleep(delay_term)
    browser.switch_to.window(browser.window_handles[0])
    
    # 상품링크
    product_link = product_list[product_no]
    # 상품 새탭 열기
    script_str = "window.open(\"{}\", \"{}\", 'location=yes');".format(product_link, 'product_detail')
    browser.execute_script(script_str)
    # 상품 페이지 활성화
    browser.switch_to.window(browser.window_handles[1])

    print('상품 상세 이미지 추출 시작:{}'.format(product_no))

    # 대상 요소
    el_product_name = browser.find_element_by_css_selector('.detailArea .item_name')

    # 상품명
    product_name = el_product_name.text

    # 상세 정보
    el_product_detail_info = browser.find_element_by_css_selector('#prdDetail > .cont')

    # 상세 정보 이미지 다운로드
    detail_img_list = el_product_detail_info.find_elements_by_tag_name('img')
    img_idx = 1
    save_detail_img = []
    for_in_seq = 1
    for el_img in detail_img_list:
        # time.sleep(delay_term)
        img_url = el_img.get_attribute('ec-data-src')
        img_full_url = '{}{}'.format(target_host, img_url)
        img_file_name = '{}_{}.jpg'.format(product_no, img_idx)
        img_dir = 'detail/'
        file_path = "./_data/"
        img_full_dir = file_path + img_dir
        if os.path.exists(img_full_dir) == False:
            os.makedirs(img_full_dir)

        img_file_full_path = img_full_dir + img_file_name
        if os.path.exists(img_file_full_path) == True:
            os.remove(img_file_full_path)
        # 상세 이미지는 우선 다운 받지 말고 정보만 추출
        os.system("curl {} > {}".format(img_full_url, img_file_full_path))
        img_idx = img_idx + 1
        save_detail_img.append({'img_url': img_url, 'img_file_name': img_file_name, 'img_file_full_path': img_file_full_path, 'seq': for_in_seq})
        for_in_seq = for_in_seq + 1

    # print(cate_no, cate_depth_text)
    # exit()
    browser.close()

    # break # 테스트 한개만

browser.switch_to.window(browser.window_handles[0])
browser.close()
sys.exit()