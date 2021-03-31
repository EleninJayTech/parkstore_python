from selenium import webdriver
from datetime import datetime

import os
import sys

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

# 브라우저 설정
browser = webdriver.Chrome(
    executable_path=chromedriver_path,
    options= options
)

# 초이템 이동
url = "http://choitemb2b.com/"
browser.get(url)

# 로그인
btn_login = browser.find_elements_by_css_selector("a[href='/member/login.html']")
if( len(btn_login) > 0 ):
    btn_login[0].click()
    input_id = browser.find_element_by_name('member_id');
    input_id.send_keys('yes7436')
    input_password = browser.find_element_by_name('member_passwd');
    input_password.send_keys('ddangsun2da!z')
    btn_login_submit = browser.find_element_by_css_selector("form[id^='member_form'] [onclick^='MemberAction.login']");
    btn_login_submit.click()

script_str = "window.open(\"{}\", \"{}\", 'location=yes');".format(url, 'choi')
browser.execute_script(script_str)
browser.switch_to.window(browser.window_handles[1])

# browser.close()
sys.exit()