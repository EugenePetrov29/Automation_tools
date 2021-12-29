import datetime
from selenium import webdriver
from selenium.webdriver.common import keys
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
from tqdm import tqdm
import datetime

class AppsflyerScraper(object):
    def __init__(self, driver):
        self.driver = driver


    def parse(self, login, password, name):
        self.go_to_offers_page(login, password, name)
        
    
    def go_to_offers_page(self, login, password, name):
        now = datetime.datetime.now()
        self.driver.get('https://hq1.appsflyer.com/auth/login')
        time.sleep(2)
        self.driver.find_element_by_id('user-email').click()
        self.driver.find_element_by_id('user-email').send_keys(login)
        self.driver.find_element_by_id('user-email').send_keys(Keys.TAB)
        self.driver.find_element_by_id('password-field').send_keys(password)
        self.driver.find_element_by_id('password-field').send_keys(Keys.TAB)
        self.driver.find_element_by_id('password-field').send_keys(Keys.ENTER)
        time.sleep(10)
        self.driver.get('https://hq1.appsflyer.com/dashboard/overview/id1021256908')
        time.sleep(10)
        self.driver.find_element_by_xpath('//button[@id="reportrange"]').click()
        time.sleep(7)
        self.driver.find_element_by_xpath('//div[@class="ranges"]').find_elements_by_tag_name('button')[0].click()
        time.sleep(10)
        self.driver.find_element_by_xpath('//h2[contains(., "Additional insights")]').click()
        self.driver.implicitly_wait(5)
        self.driver.save_screenshot("/home/nik/work/Eugene/scraper/screenshots/screenshot_" + str(now) + ".png")
        



def main():
    driver = webdriver.Firefox()
    parser = AppsflyerScraper(driver)
    accs_cred = {'name':'Agency', 'login':'julia@theiris.io', 'password':'`S=uH8?t$Hn{]qNH?'}
    boole = True
    
    while boole == True:
        login = accs_cred['login']
        password = accs_cred['password']
        name = accs_cred['name']
        parser.parse(login, password, name)
        time.sleep(3550)

if __name__ == '__main__':
    main()