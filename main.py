import json
import time
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_products_list(item_name='наушнки apple'):
    driver = uc.Chrome()
    driver.implicitly_wait(5)

    driver.get('https://ozon.ru/')
    time.sleep(10)

    find_input = driver.find_element(By.NAME, 'text')
    find_input.clear()
    find_input.send_keys(item_name)
    time.sleep(2)

    find_input.send_keys(Keys.ENTER)
    time.sleep(2)

    driver.close()
    driver.quit()


def main():
    get_products_list()



if __name__ == '__main__':
    main()
