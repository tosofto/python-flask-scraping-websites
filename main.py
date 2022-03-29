import undetected_chromedriver as webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import requests
import re

if __name__ == '__main__':

    chrome_options = Options()
    driver = webdriver. Chrome(options=chrome_options)
    driver.get("https://www.e-food.gr/delivery/menu/aroma-caffe")
    time.sleep(10)
    print(driver.page_source)
    data = driver.page_source.encode('utf8').decode('ascii', 'ignore')
    search_result = re.search(r'[^�]*\"shopID\"\: ([\d]+)[^�]*',data )
    print(search_result.group(1))
    driver.close()
