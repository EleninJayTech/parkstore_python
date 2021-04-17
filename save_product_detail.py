from selenium import webdriver

import configparser
import json
import os
import sys
import time
import requests

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

# 파일 가져오기
file_path = "./_data/"
file_name = 'cate_no_{}.json'.format(cate_no)
file_full_path = file_path + file_name

if os.path.exists(file_full_path) == False:
    print('대상 파일이 없습니다.')
    browser.close()
    sys.exit()

# json 데이터를 object 로
with open(file_full_path) as f:
    product_list = json.load(f)

# 상품 번호와 상품 URL 추출
product_idx = 0
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

    print('상품 데이터 추출 시작:{}'.format(product_no))

    # 대상 요소
    el_product_name = browser.find_element_by_css_selector('.detailArea .item_name')
    el_product_info = browser.find_element_by_css_selector('.detailArea .infoArea')

    # 상품명
    product_name = el_product_name.text
    # 상품정보 전체 텍스트
    product_info = el_product_info.text
    # 상품정보 전체 HTML
    product_info_html = el_product_info.get_attribute('innerHTML')

    # 메인 상품 이미지 파일 저장
    img_file_list = browser.find_elements_by_css_selector('.listImg img')
    img_idx = 1
    save_product_img = []
    for_in_seq = 1
    for el_img in img_file_list:
        # 테스트 용
        # break
        # time.sleep(delay_term)
        img_url = el_img.get_attribute('src')
        img_file_name = 'product_{}_{}.jpg'.format(product_no, img_idx)
        # img_dir = '{}/'.format(product_no)
        img_dir = ''
        img_full_dir = file_path + img_dir
        if os.path.exists(img_full_dir) == False:
            os.makedirs(img_full_dir)

        img_file_full_path = img_full_dir + img_file_name
        if os.path.exists(img_file_full_path) == True:
            os.remove(img_file_full_path)
        os.system("curl {} > {}".format(img_url, img_file_full_path))
        img_idx = img_idx + 1
        save_product_img.append({'img_url': img_url, 'img_file_name': img_file_name, 'img_file_full_path': img_file_full_path, 'seq': for_in_seq})
        for_in_seq = for_in_seq + 1

    # 상품 정보 추출
    el_info_list = el_product_info.find_elements_by_css_selector('table tr')
    save_product_info = []
    for_in_seq = 1
    for info_list in el_info_list:
        try:
            info_name = info_list.find_element_by_tag_name('th').text
            info_value = info_list.find_element_by_tag_name('td').text
            info_name=info_name.strip()
            info_value=info_value.strip()
            save_product_info.append({'info_name':info_name, 'info_value':info_value, 'seq':for_in_seq})
            # print(info_name, info_value)
            for_in_seq = for_in_seq + 1
        except:
            print('[예외 발생] {}'.format(info_list))
            continue

    # 옵션 정보
    el_option_list = browser.find_elements_by_css_selector('.infoArea table.xans-product-option tr')
    save_option_info = []
    for_in_seq = 1
    for option_list in el_option_list:
        try:
            # 옵션 명
            option_name = option_list.find_element_by_tag_name('th').text
            option_name=option_name.strip()

            # 옵션 값
            el_option_value = option_list.find_element_by_tag_name('td')
            option_value_html = el_option_value.get_attribute('innerHTML')
            select_option_list = el_option_value.find_elements_by_css_selector('option')
            if len(select_option_list) > 0:
                for in_option in select_option_list:
                    option_value = in_option.text
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
    el_product_detail_info = browser.find_element_by_css_selector('#prdDetail > .cont')
    # 상세 정보 HTML
    product_detail_info_html = el_product_detail_info.get_attribute('innerHTML')

    # 상세 정보 이미지 다운로드
    detail_img_list = el_product_detail_info.find_elements_by_tag_name('img')
    img_idx = 1
    save_detail_img = []
    for_in_seq = 1
    for el_img in detail_img_list:
        # time.sleep(delay_term)
        img_url = el_img.get_attribute('ec-data-src')
        img_full_url = '{}{}'.format(target_host, img_url)
        img_file_name = 'product_{}_detail_{}.jpg'.format(product_no, img_idx)
        img_dir = ''
        img_full_dir = file_path + img_dir
        if os.path.exists(img_full_dir) == False:
            os.makedirs(img_full_dir)

        img_file_full_path = img_full_dir + img_file_name
        if os.path.exists(img_file_full_path) == True:
            os.remove(img_file_full_path)
        os.system("curl {} > {}".format(img_full_url, img_file_full_path))
        img_idx = img_idx + 1
        save_detail_img.append({'img_url': img_url, 'img_file_name': img_file_name, 'img_file_full_path': img_file_full_path, 'seq': for_in_seq})
        for_in_seq = for_in_seq + 1

    # 상품 구매 기타 정보 추출
    prd_info_list = browser.find_elements_by_css_selector(".prd_info.-section")
    save_etc_info = []
    for_in_seq = 1
    for prd_info in prd_info_list:
        info_title = prd_info.find_element_by_css_selector('.titleArea2').text
        info_desc = prd_info.find_element_by_css_selector('.info_text').text
        info_title = info_title.strip() # 기타 정보
        info_desc = info_desc.strip() # 기타 정보
        save_etc_info.append({'info_title': info_title, 'info_desc': info_desc, 'seq': for_in_seq})
        for_in_seq = for_in_seq + 1

    product_idx = product_idx + 1
    browser.close()

    # 데이터 저장
    # DB 저장될 데이터 취합
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
        , 'product_etc_info': save_etc_info
        , 'product_img': save_product_img
        , 'detail_img': save_detail_img
    }
    save_product = json.dumps(save_product)
    post_url = 'http://parkstore.test/api/product/save'
    data = {'encrypt_key': 'e8b6a94f577bd529c2e67da6aa449219', 'product': save_product}
    response = requests.post(post_url, data=data)
    # todo 저장 완료 여부 확인 및 처리
    print(response.text)

    # break # 테스트 한개만

browser.switch_to.window(browser.window_handles[0])
browser.close()
sys.exit()