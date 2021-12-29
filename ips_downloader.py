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

class AppsflyerScraper(object):
    def __init__(self, driver):
        self.driver = driver


    def parse(self, login, password, geo, today, quantity):
        self.go_to_offers_page(login, password, geo, today, quantity)

    
    def os_activity(self, geo, today, quantity_per_part, reports):    

        prev = datetime.datetime.now()
        delta = datetime.timedelta(days=7)
        prev_time = prev - delta
        prev_time = prev_time.strftime("%d_%m_%Y")
        
        curent_ip_path = F"/home/nik/work/Eugene/IPs/{geo}_{prev_time}/All_{geo}_{prev_time}.csv"
        new_ip_parts_path = '/home/nik/work/Eugene/new_reports/' + geo + str(today) + '/'
        data = range(1,reports + 1)
                                    

        new_ip_from_reposts = []
        curent_ip = pd.read_csv(
            os.path.join(curent_ip_path),
            )
        curent_ip = curent_ip['user_connection_ip'].to_list()

        print('Загрузка и объединение репортов:')
        
        for i in tqdm(data):
            try:
                list_ip = pd.read_csv(
                    os.path.join(new_ip_parts_path + str(i) + ".csv"),
                    )
                new_ip_from_reposts.append(list_ip['user_connection_ip'].to_list())
            except:
                continue

        print('Идет обработка данных...')

        def listmerge3(lstlst):
            all=[]
            for lst in lstlst:
                all.extend(lst)
            return all

        result = listmerge3(new_ip_from_reposts)

        new_ip_without_validation = set(result)
        print('Загружено новых уникальных IP адресов: ' + str(len(result)), end='   ::::::   ')


        new_ip_list = list(set(new_ip_without_validation) - set(curent_ip))
        print('Новых IP адресов после проверки: ' + str(len(new_ip_list)))

        new_curent_ip = []
        new_curent_ip.append(curent_ip)
        new_curent_ip.append(new_ip_list)
        new_curent_ip = listmerge3(new_curent_ip)


        print('Всего было IP адресов: ' + str(len(curent_ip)), end='   ::::::   ')
        print('Всего стало IP адресов: ' + str(len(new_curent_ip)))


        parts = [new_ip_list[i:i+quantity_per_part] for i in range(0,len(new_ip_list),quantity_per_part)]
        print('Всего пачек: ' + str(len(parts)))



        output_dir_name = geo + today
        parts_output_dir_name = output_dir_name + '/' + str(len(parts)) + '_parts_per_' + str(quantity_per_part) + '_ips'



        os.mkdir(output_dir_name)
        os.mkdir(parts_output_dir_name)


        print('Запись файла со всеми IP адресами:')
        with open(output_dir_name + '/' + 'All_' + geo + today +'.csv', 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            new_curent_ip.insert(0, 'user_connection_ip')
            for item in tqdm(new_curent_ip):
                csv_writer.writerow([item])

        print('Запись файла с новыми IP адресами:')
        with open(output_dir_name + '/' + geo + today +'.csv', 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            new_ip_list.insert(0, 'user_connection_ip')
            for item in tqdm(new_ip_list):
                csv_writer.writerow([item])

        print('Разделение новых IP адресов на части...')
        a = 1
        for part in parts:
            with open(parts_output_dir_name + '/part' + str(a) + '.csv', 'w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                for item in part:
                    csv_writer.writerow([item])
            a += 1

        print('Готово!')
        
    
    def go_to_offers_page(self, login, password, geo, today, quantity):
        now = datetime.datetime.now()
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
        print('Выгрузка из базы ' + geo + '...')
        for n in tqdm(range(quantity)):
            dd = datetime.timedelta(days=n)
            day = today - dd
            day = day.strftime("%Y-%m-%d")
            self.driver.find_element_by_xpath('//div[@class="ace_content"]').click()
            time.sleep(0.5)
            self.driver.find_element_by_xpath('//textarea[@class="ace_text-input"]').send_keys(Keys.BACK_SPACE * 10000)
            string = F"SELECT user_connection_ip, COUNT(*) as quantity FROM clicks WHERE publisher_id in ('639', '640') and time>'{day} 00:00:00' and time<'{day} 23:59:59' and user_device_os='iOS' and user_geo_country='{geo}' GROUP BY user_connection_ip ORDER BY COUNT(*) as quantity DESC"
            self.driver.find_element_by_xpath('//div[@class="ace_content"]').click()          
            self.driver.find_element_by_xpath('//textarea[@class="ace_text-input"]').send_keys(string)
            time.sleep(0.5)
            self.driver.find_element_by_xpath('//span[.="Run"]').click()
            try:
                element = WebDriverWait(self.driver, 50).until(
                    EC.presence_of_element_located((By.XPATH, '//a[@class="ant-btn superset-button css-1n37w2-button"]'))
                )
                time.sleep(3)
                element.click()
            except:
                continue
        self.driver.quit()

    def new_name(self, downloadDir):          
        ext = "csv"
        i = 1
        for file in os.listdir(downloadDir):
            if file.endswith(ext):
                os.rename(f'{downloadDir}/{file}', f'{downloadDir}/{i}.{ext}')
                i = i + 1
        
def main():
    accs_cred = {'login':'admin', 'password':'6101.Pet'}
    
    login = accs_cred['login']
    password = accs_cred['password']
    today = datetime.datetime.now()
    day = today.strftime("_%d_%m_%Y")
    geos = ('DE', 'FR', 'US') #, 
    quantity_per_part = 100000
    reports = 7
    quantity = 7

    for geo in geos:
        output_dir_name = '/home/nik/work/Eugene/new_reports/' + geo + str(day)
        os.mkdir(output_dir_name)
        os.environ['MOZ_HEADLESS'] = '1'
        fp = webdriver.FirefoxProfile()
        fp.set_preference("browser.download.folderList", 2)
        fp.set_preference("browser.download.manager.showWhenStarting", False)
        fp.set_preference("browser.download.dir", output_dir_name)
        fp.set_preference("browser.helperApps.neverAsk.saveToDisk",
                            "text/plain, application/octet-stream, application/binary, text/csv, attachment/csv, application/csv, application/excel, text/comma-separated-values, text/xml, application/xml")
        driver = webdriver.Firefox(firefox_profile=fp)
        parser = AppsflyerScraper(driver)
        parser.parse(login, password, geo, today, quantity)
        parser.new_name(output_dir_name)
        parser.os_activity(geo, day, quantity_per_part, reports)

if __name__ == '__main__':
    main()