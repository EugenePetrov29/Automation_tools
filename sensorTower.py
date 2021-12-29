from selenium import webdriver
from selenium.webdriver.common import keys
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import pandas as pd
from tqdm import tqdm
import datetime
import os
import csv

class SupersetScraper(object):
    def __init__(self, driver):
        self.driver = driver


    def parse(self, login, password, today):
        self.go_to_offers_page(login, password, today)
        
    
    def go_to_offers_page(self, login, password, today):
        self.driver.get('http://iris.superset.swaarm.com/superset/sqllab/')
        time.sleep(2)
        self.driver.find_element_by_id('username').click()
        self.driver.find_element_by_id('username').send_keys(login)
        self.driver.find_element_by_id('username').send_keys(Keys.TAB)
        self.driver.find_element_by_id('password').send_keys(password)
        self.driver.find_element_by_id('password').send_keys(Keys.TAB)
        self.driver.find_element_by_id('password').send_keys(Keys.ENTER)
        time.sleep(0.5)
        self.driver.get('http://iris.superset.swaarm.com/superset/sqllab/')
        time.sleep(2)
        self.driver.find_element_by_xpath('//a[@class="ant-dropdown-trigger"]').click()
        time.sleep(0.5)
        self.driver.find_element_by_xpath('//a[.="100 000"]').click()
        self.driver.find_element_by_xpath('//div[@class="ace_content"]').click()
        time.sleep(0.5)
        self.driver.find_element_by_xpath('//textarea[@class="ace_text-input"]').send_keys(Keys.BACK_SPACE * 2000)
        string = F"SELECT app_store_id, COUNT(*) as quantity FROM offers WHERE status='ACTIVE' GROUP BY app_store_id ORDER BY COUNT(*) as quantity DESC"
        self.driver.find_element_by_xpath('//div[@class="ace_content"]').click()          
        self.driver.find_element_by_xpath('//textarea[@class="ace_text-input"]').send_keys(string)
        time.sleep(0.5)
        self.driver.find_element_by_xpath('//span[.="Run"]').click()
        element = WebDriverWait(self.driver, 50).until(
            EC.presence_of_element_located((By.XPATH, '//a[@class="ant-btn superset-button css-1n37w2-button"]'))
        )
        element.click()


    def new_name(self, downloadDir):          
        ext = "csv"
        i = 1
        for file in os.listdir(downloadDir):
            if file.endswith(ext):
                os.rename(f'{downloadDir}/{file}', f'{downloadDir}/report.{ext}')
        

    def scrape_stats_from_sensor(self, dir):
        def auth():
            driver = webdriver.Firefox()
            driver.get('https://sensortower.com/')
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'app-search-input'))
            )
            return driver

        input_file = csv.DictReader(open(dir + "/report.csv"))
        input_file = list(input_file)

        data = []
        for dict in tqdm(input_file):
            try:
                driver = auth()
            except:
                d = {'installs' : 'scraper error'}
                dict.update(d)
                driver.quit()
                driver = auth()
                continue
            try:
                driver.find_element_by_id('app-search-input').click()
                driver.find_element_by_id('app-search-input').send_keys(dict['app_store_id'])
                element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//span[@class="autocomplete-name"]'))
                )
                driver.find_element_by_id('app-search-input').send_keys(Keys.ENTER)
            except:
                d = {'installs' : 'application is not available'}
                dict.update(d)
                driver.quit()
                driver = auth()
                continue
            try:
                element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//span[@class="dl-rev-value"]'))
                )
                text = driver.find_element_by_xpath('//span[@class="dl-rev-value"]').get_attribute("innerHTML")
                if text[-1] == 'm':
                    text = text.rsplit('m')
                    d = {'installs' : text[0] + '000000'}
                elif text[-1] == 'k':
                    text = text.rsplit('k')
                    d = {'installs' : text[0] + '000'}    
                dict.update(d)
            except:
                d = {'installs' : 'application is not available'}
                dict.update(d)
                driver.quit()
                driver = auth()
                continue
            driver.quit()
            print(dict)
            data.append(dict)
            time.sleep(10)
        df = pd.DataFrame.from_dict(data, orient='columns')
        df.to_csv(dir + '/scraped_data.csv')




def main():
    accs_cred = {'login':'admin', 'password':'6101.Pet'}
    
    login = accs_cred['login']
    password = accs_cred['password']
    today = datetime.datetime.now()
    day = today.strftime("_%d_%m_%Y")

    output_dir_name = '/home/nik/work/Repetitive store/data/' + str(day)
    os.mkdir(output_dir_name)
    #os.environ['MOZ_HEADLESS'] = '1'
    fp = webdriver.FirefoxProfile()
    fp.set_preference("browser.download.folderList", 2)
    fp.set_preference("browser.download.manager.showWhenStarting", False)
    fp.set_preference("browser.download.dir", output_dir_name)
    fp.set_preference("browser.helperApps.neverAsk.saveToDisk",
                        "text/plain, application/octet-stream, application/binary, text/csv, attachment/csv, application/csv, application/excel, text/comma-separated-values, text/xml, application/xml")
    driver = webdriver.Firefox(firefox_profile=fp)
    parser = SupersetScraper(driver)
    parser.parse(login, password, day)
    parser.new_name(output_dir_name)
    parser.scrape_stats_from_sensor(output_dir_name)

    

if __name__ == '__main__':
    main()