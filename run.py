import os
import requests
import glob
from selenium import webdriver
from selenium.webdriver.common import keys
from selenium.webdriver.common.keys import Keys
import time
import datetime
import pandas as pd
from tqdm import tqdm
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class AppsflyerScraper(object):
    def __init__(self, driver):
        self.driver = driver
        

    def parse(self, login, password, name):
        self.go_to_offers_page(login, password, name)
        
    
    def on_one_dock(self):
        today = datetime.datetime.now()
        day = today.strftime("_%d_%m_%Y")
        os.chdir("Reports")
        extension = 'csv'
        all_filenames = [i for i in glob.glob('*.{}'.format(extension))]
        combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames ])
        for f in all_filenames:
            os.remove(f)
        combined_csv.to_csv( 'All' + day + '.csv', index=False, encoding='utf-8-sig')


    def go_to_offers_page(self, login, password, name):
        today = datetime.datetime.now()
        day = today.strftime("_%d_%m_%Y")
        print(name + '...', end = ' ')
        today1 = today.strftime("%d-%m-%Y")
        dd = datetime.timedelta(days=1)
        yesterday = today - dd
        yesterday = yesterday.strftime("%d-%m-%Y")
        self.driver.get('https://hq1.appsflyer.com/auth/login')
        element = WebDriverWait(self.driver, 50).until(
                    EC.presence_of_element_located((By.ID, 'user-email'))
                )
        element.click()
        element.send_keys(login)
        element.send_keys(Keys.TAB)
        self.driver.find_element_by_id('password-field').send_keys(password)
        self.driver.find_element_by_id('password-field').send_keys(Keys.TAB)
        self.driver.find_element_by_id('password-field').send_keys(Keys.ENTER)
        slide_elements = WebDriverWait(self.driver, 50).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'card-title'))
                )
        app_names = []
        for i in slide_elements:
            app_name = i.get_attribute('title')
            app_names.append(app_name)
        slide_bundles = WebDriverWait(self.driver, 50).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'card-subtitle'))
                )
        app_ids = []
        for i in slide_bundles:
            app_id = i.get_attribute('title')
            app_ids.append(app_id)
        data = []
        print(len(app_ids))

    

        for i, (app, bundle) in tqdm(enumerate(zip(app_names, app_ids))):
            srt = '//div[@title="' + bundle + '"]'
            element = WebDriverWait(self.driver, 50).until(
                    EC.presence_of_element_located((By.XPATH, srt))
                )
            element.click()
            datime = [1, 0]
            for t in datime:
                diction = {}
                app_name = app
                app_id = bundle
                slov = {'media_source':name, 'app_name':app_name, 'app_id':app_id}
                diction.update(slov)
                dat = {0:today1, 1:yesterday}
                element = WebDriverWait(self.driver, 50).until(
                    EC.presence_of_element_located((By.XPATH, '//button[@id="reportrange"]'))
                )
                element.click()
                element = WebDriverWait(self.driver, 50).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@class="ranges"]'))
                )
                element.find_elements_by_tag_name('button')[t].click()

                values = WebDriverWait(self.driver, 50).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'af-kpi-box-piece'))
                )
                time.sleep(2.3)
                for value in values:
                    key = value.find_elements_by_tag_name('h5')[0].text
                    val = value.find_element_by_tag_name('text').text
                    d = {key:val}
                    diction.update(d)
                dt = dat[t]
                d1 = {'date':dt}
                diction.update(d1)
                # print(diction)
                data.append(diction)
            self.driver.back()
            # break
            # self.driver.find_element_by_xpath('//a[@title="AppsFlyer"]').click()
        df = pd.DataFrame.from_dict(data, orient='columns')
        file_name = name + day + '.csv'
        df.to_csv('Reports/' + file_name)
        # self.driver.close()



def main():
    driver = webdriver.Firefox()
    parser = AppsflyerScraper(driver)
    accs_cred = [
        {'name':'PAU', 'login':'paulina@theiris.io', 'password':'-`@-g4J3N7XLc[c>U'},
        # {'name':'OSI', 'login':'osiris.check@gmail.com', 'password':'-7,/dEYbVubqug~}L'},
        # {'name':'ADV', 'login':'info@advictos.com', 'password':'QM?hqU%"_7Ld\c6_G'},
        # {'name':'MOB', 'login':'info@mobiviolet.com', 'password':'J-Uh5q6=Sjt#~3Zf^'},
        # {'name':'WOT', 'login':'start@wotobia.com', 'password':"\{V4RuN>jQE'v.NeN"},
        # {'name':'IRM', 'login':'start@irma-agency.com', 'password':'S.3cMvU:86LN!T~[Q'},
        # {'name':'EVO', 'login':'appsflyer@evvolution.com', 'password':'$Evvolution123$'},
        # {'name':'WQCPA', 'login':'tracking.appsflyer@weq.com', 'password':'$Weq2018$'},
        # {'name':'WQ', 'login':'tracking@weq.com', 'password':'$Weq2018$'},
    ]

    for i in accs_cred:
        login = i['login']
        password = i['password']
        name = i['name']
        parser.parse(login, password, name)
    
    parser.on_one_dock()

if __name__ == '__main__':
    main()