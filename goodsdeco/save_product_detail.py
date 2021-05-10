import datetime
from random import randrange

from selenium import webdriver

import configparser
import json
import os
import sys
import time
import requests
import re

from requests import get  # to make GET request

def download(url, file_name):
    with open(file_name, "wb") as file:   # open in binary mode
        response = get(url)               # get request
        file.write(response.content)      # write to file

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

# 처리할 파일
file_name = 'goodsdeco_202105110014.json'

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
# 파일 가져오기
file_path = "../_data/{}/".format(shop_code)
file_full_path = file_path + file_name

if os.path.exists(file_full_path) == False:
    print('대상 파일이 없습니다.')
    browser.close()
    sys.exit()

# json 데이터를 object 로
with open(file_full_path) as f:
    product_list = json.load(f)

# 고유 코드 생성
now = datetime.datetime.now()
PK_CODE = now.strftime("%Y%m%d%H%M%S")

# 상품 번호와 상품 URL 추출
product_idx = 0

post_url = 'http://parkstore.test/api/exist_pno/{}'.format(shop_code)
data = {'encrypt_key': 'e8b6a94f577bd529c2e67da6aa449219'}
response = requests.post(post_url, data=data)
exist_pno_list = json.loads(response.text)
exist_check_pno = []
for pno in exist_pno_list:
    exist_check_pno.append(int(pno['product_no']))

for product_no in product_list:
    # 제외할 상품 확인 후 continue 존재하는 상품 패스
    if int(product_no) in exist_check_pno:
        print('존재 상품 제외 {}'.format(product_no))
        continue

    print('상품 페이지로 이동:{}'.format(product_no))
    time.sleep(delay_term)
    browser.switch_to.window(browser.window_handles[0])
    
    # 상품링크
    product_link = product_list[product_no]
    # todo 테스트
    # product_link = 'http://www.goodsdeco.com/goods/goods_view.php?goodsNo=1000004168'
    # 상품 새탭 열기
    script_str = "window.open(\"{}\", \"{}\", 'location=yes');".format(product_link, 'product_detail')
    browser.execute_script(script_str)
    # 상품 페이지 활성화
    browser.switch_to.window(browser.window_handles[1])

    print('상품 데이터 추출 시작:{}'.format(product_no))

    # 대상 요소
    selector_p_name = '.item_detail_tit h3'
    selector_p_info = '.item_detail_list'
    el_product_name = browser.find_element_by_css_selector(selector_p_name)
    el_product_info = browser.find_element_by_css_selector(selector_p_info)

    # 상품명
    product_name = el_product_name.text
    # 상품정보 전체 텍스트
    product_info = el_product_info.text
    # 상품정보 전체 HTML
    product_info_html = el_product_info.get_attribute('innerHTML')

    # 메인 상품 이미지 파일 저장
    selector_main_img = 'ul.slider_goods_nav li img'
    img_file_list = browser.find_elements_by_css_selector(selector_main_img)
    img_idx = 1
    save_product_img = []
    for_in_seq = 1
    for el_img in img_file_list:
        # 테스트 용
        # break
        # time.sleep(delay_term)
        img_url = el_img.get_attribute('src')
        basename = os.path.basename(img_url)
        i_name, ext = os.path.splitext(basename)
        img_file_name = 'product_{}_{}.{}'.format(product_no, img_idx, ext)
        # img_dir = '{}/'.format(product_no)
        img_dir = ''
        img_full_dir = file_path + img_dir
        if os.path.exists(img_full_dir) == False:
            os.makedirs(img_full_dir)

        img_file_full_path = img_full_dir + img_file_name
        if os.path.exists(img_file_full_path) == True:
            os.remove(img_file_full_path)
        os.system('curl "{}" > "{}"'.format(img_url, img_file_full_path))
        img_idx = img_idx + 1
        save_product_img.append({'img_url': img_url, 'img_file_name': img_file_name, 'img_file_full_path': img_file_full_path, 'seq': for_in_seq})
        for_in_seq = for_in_seq + 1

    # 상품 정보 추출
    el_info_list = el_product_info.find_elements_by_css_selector('dl')
    save_product_info = []
    for_in_seq = 1
    for info_list in el_info_list:
        try:
            info_name = info_list.find_element_by_tag_name('dt').text
            info_value = info_list.find_element_by_tag_name('dd').text
            info_name=info_name.strip()
            info_value=info_value.strip()
            save_product_info.append({'info_name':info_name, 'info_value':info_value, 'seq':for_in_seq})
            # print(info_name, info_value)
            for_in_seq = for_in_seq + 1
        except:
            print('[예외 발생] {}'.format(info_list))
            continue

    # 옵션 정보
    selector_option_wrap = '.item_add_option_box dl'
    el_option_list = browser.find_elements_by_css_selector(selector_option_wrap)
    save_option_info = []
    for_in_seq = 1
    for option_list in el_option_list:
        try:
            # 옵션 명
            option_name = option_list.find_element_by_tag_name('dt').text
            option_name=option_name.strip()

            # 옵션 값
            el_option_value = option_list.find_element_by_tag_name('dd')
            option_value_html = el_option_value.get_attribute('innerHTML')
            select_option_list = el_option_value.find_elements_by_css_selector('select option')
            # 셀렉트 박스 형 옵션
            if len(select_option_list) > 0:
                for in_option in select_option_list:
                    option_value = in_option.get_attribute('innerHTML')
                    option_value = option_value.strip()
                    save_option_info.append({'option_name': option_name, 'option_value': option_value, 'seq': for_in_seq})
                    for_in_seq = for_in_seq + 1
            else:
                option_value = el_option_value.text
                option_value=option_value.strip()
                save_option_info.append({'option_name': option_name, 'option_value': option_value, 'seq': for_in_seq})
                for_in_seq = for_in_seq + 1

        except:
            print('[예외 발생] {}'.format(option_list))
            continue

    # 상세 정보
    selector_detail_wrap = '.detail_explain_box'
    el_product_detail_info = browser.find_element_by_css_selector(selector_detail_wrap)
    # 상세 정보 HTML
    product_detail_info_html = el_product_detail_info.get_attribute('innerHTML')

    # 상세 정보 이미지 다운로드
    detail_img_list = el_product_detail_info.find_elements_by_tag_name('img')
    img_idx = 1
    save_detail_img = []
    for_in_seq = 1
    img_nm = re.sub(r'[^가-힣a-zA-Z0-9 ]', ' ', product_name)
    for el_img in detail_img_list:
        # time.sleep(delay_term)
        img_url = el_img.get_attribute('src')
        basename = os.path.basename(img_url)
        i_name, ext = os.path.splitext(basename)
        img_full_url = '{}'.format(img_url)
        img_file_name = '{}_{}_{}.{}'.format(product_no, img_nm, img_idx, ext)
        img_dir = 'detail/'
        img_full_dir = file_path + img_dir
        if os.path.exists(img_full_dir) == False:
            os.makedirs(img_full_dir)

        img_file_full_path = img_full_dir + img_file_name
        if os.path.exists(img_file_full_path) == True:
            os.remove(img_file_full_path)
        # 상세 이미지는 우선 다운 받지 말고 정보만 추출
        # os.system('curl "{}" > "{}"'.format(img_full_url, img_file_full_path))
        img_idx = img_idx + 1
        save_detail_img.append({'img_url': img_url, 'img_file_name': img_file_name, 'img_file_full_path': img_file_full_path, 'seq': for_in_seq})
        for_in_seq = for_in_seq + 1

    product_idx = product_idx + 1

    # 카테고리 코드 가져오기
    try:
        browser.get('https://shopping.naver.com/')
        el_query = browser.find_element_by_name('query')
        el_query.send_keys(product_name)
        el_search_btn = browser.find_element_by_css_selector('.co_srh_btn')
        # 상품명 검색
        time.sleep(randrange(3, 6))
        el_search_btn.click()
        time.sleep(delay_term)
        # 카테고리 링크 정보
        el_cate_depth = browser.find_element_by_css_selector('[class^=basicList_depth]')
        cate_a = el_cate_depth.find_elements_by_tag_name('a')
        cate_depth = len(cate_a)
        cate_no = 0
        cate_depth_text = []
        if cate_depth > 0:
            # 링크에서 카테고리 번호만 추출
            cate_href = cate_a[cate_depth - 1].get_attribute('href')
            cate_no = re.findall("\d+", cate_href)[0]

            # 카테고리 명칭 가져오기
            for cate_info in cate_a:
                cate_txt = cate_info.text
                cate_depth_text.append(cate_txt)
    except:
        print('[예외 발생 네이버] {} {}'.format(product_no, product_name))

    # print(cate_no, cate_depth_text)
    # todo 테스트
    # exit()
    browser.close()

    # 데이터 저장
    # DB 저장될 데이터 취합
    # print(product_no)
    # 고유코드 저장
    save_product = {
        'shop_code': shop_code
        , 'product_no': product_no
        , 'product_link': product_link
        , 'product_name': product_name
        , 'product_info': product_info
        , 'product_info_html': product_info_html
        , 'product_detail_info_html': product_detail_info_html
        , 'product_info_list': save_product_info
        , 'product_option_list': save_option_info
        , 'product_img': save_product_img
        , 'category_code': cate_no
        , 'cate_depth_text': cate_depth_text
        , 'detail_img': save_detail_img
        , 'PK_CODE': PK_CODE
    }
    save_product = json.dumps(save_product)
    post_url = 'http://parkstore.test/api/product_save'
    data = {'encrypt_key': 'e8b6a94f577bd529c2e67da6aa449219', 'product': save_product}
    response = requests.post(post_url, data=data)
    # todo 저장 완료 여부 확인 및 처리
    print(response.text)

    # todo 테스트
    # break

# 고유 코드 엑셀 다운로드
url = 'http://parkstore.test/product/createExcel/{}'.format(PK_CODE)
file_path = "../_data/{}/".format(shop_code)
excel_full_path = '{}Excel_{}.xlsx'.format(file_path, PK_CODE)
download(url, excel_full_path)

browser.switch_to.window(browser.window_handles[0])
browser.close()
sys.exit()