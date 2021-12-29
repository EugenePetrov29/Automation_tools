import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.firefox.options import Options
import os
import gc
import datetime
import random
from tqdm import tqdm

clear_setup = [
                {'url': 'https://www.facebook.com/110504584024961/posts/455111712897578',
                'allowed_comments_amount': 0},
                {'url': 'https://www.facebook.com/110504584024961/posts/432590241816392',
                'allowed_comments_amount': 0},
                {'url': 'https://www.facebook.com/110504584024961/posts/453155319759884',
                'allowed_comments_amount': 0},
                {'url': 'https://www.facebook.com/110504584024961/posts/453155139759902',
                'allowed_comments_amount': 0},
                {'url': 'https://www.facebook.com/110504584024961/posts/453154866426596',
                'allowed_comments_amount': 0},
               ]


def clean_post(setup):
    try:
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Firefox(firefox_options=options)    # firefox_options=options
        driver.get('https://www.facebook.com/')
        time.sleep(10)
        print('Ввод кредов...')
        driver.find_element_by_id('email').send_keys('broamazing@yandex.com')
        driver.find_element_by_id('pass').send_keys('8aiKI1xX6h')
        time.sleep(1)
        driver.find_element_by_xpath("//button[@name='login']").click()
        print('Вход в аккаунт...')
        for setup_element in tqdm(setup):
            time.sleep(10)
            driver.get(setup_element['url'])
            time.sleep(10)
            driver.execute_script("window.scrollTo(0, (document.body.scrollHeight));")
            time.sleep(0.5)
            page_response = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
            html_main = BeautifulSoup(page_response, 'html.parser')
            comments_html = html_main.findAll('div', {"class": "no6464jc"})
            check = len(comments_html) < setup_element['allowed_comments_amount'] \
                    or len(comments_html) == setup_element['allowed_comments_amount']
            while not check:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(0.5)
                driver.find_elements_by_class_name('no6464jc')[-1].click()
                time.sleep(0.5)
                driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
                time.sleep(0.5)
                driver.find_elements_by_xpath("//div[@role='menuitem']")[1].click()
                driver.get(setup_element['url'])
                time.sleep(10)
                page_response = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
                html_main = BeautifulSoup(page_response, 'html.parser')
                comments_html = html_main.findAll('div', {"class": "no6464jc"})
                check = len(comments_html) < setup_element['allowed_comments_amount'] \
                        or len(comments_html) == setup_element['allowed_comments_amount']
        driver.quit()
        os.system("killall 'firefox'")
        gc.collect()
    except WebDriverException:
        os.system("killall 'firefox'")
        gc.collect()
        clean_post(setup)


def run_clean():
    start = time.time()
    clean_post(clear_setup)
    runtime = time.time() - start
    info = 'check duration -- ' + str(runtime)
    now = str(datetime.datetime.now())
    placeholder = 'check -- ' + now + ','
    print("\n", placeholder, info)
    if runtime < 1800:
        random_addendum = random.randint(30, 600)
        operation_id = random.randint(0, 1)
        if operation_id == 0:
            hold = 1800 - random_addendum
        else:
            hold = 1800 + random_addendum
        print('Next check will be executed in ' + str(hold) + ' seconds', "\n")
        time.sleep(hold)
    run_clean()


while True:
    run_clean()
