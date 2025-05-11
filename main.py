import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd


def setup_driver():
    # Настройка опций Chrome
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")  # Максимизировать окно браузера
    options.add_argument("--disable-blink-features=AutomationControlled")  # Скрытие автоматизации
    options.add_experimental_option("excludeSwitches", ["enable-automation"])  # Отключение автоматизации

    # Инициализация драйвера
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    return driver


def search_products(driver, search_query):
    # Переход на главную страницу Ozon
    driver.get("https://www.ozon.ru/")

    try:
        # Ожидание появления поисковой строки
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "text"))
        )

        # Ввод поискового запроса
        search_input.clear()
        search_input.send_keys(search_query)
        search_input.send_keys(Keys.RETURN)
        time.sleep(2)

        # Ожидание загрузки результатов поиска
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".widget-search-result-container"))
        )

        # Прокрутка страницы для загрузки всех товаров
        for _ in range(3):  # Прокручиваем 3 раза
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

    except Exception as e:
        print(f"Ошибка при поиске товаров: {e}")
        return False

    return True


def parse_products(driver):
    products = []

    try:
        # Находим все элементы товаров
        items = driver.find_elements(By.CSS_SELECTOR, ".widget-search-result-container div[data-widget='searchResultsV2'] > div > div")

        for item in items:
            try:
                # Название товара
                name = item.find_element(By.CSS_SELECTOR, "a[title]").get_attribute("title")
                
                # Цена товара
                price_element = item.find_element(By.CSS_SELECTOR, ".ui-s9 span[class*='price']")
                price = price_element.text.replace("₽", "").replace(" ", "").strip()

                # Ссылка на товар
                link = item.find_element(By.CSS_SELECTOR, "a[href]").get_attribute("href")
                
                # Добавляем товар в список
                products.append({
                    "name": name,
                    "price": price,
                    "link": link
                })

            except Exception as e:
                print(f"Ошибка при парсинге товара: {e}")
                continue

    except Exception as e:
        print(f"Ошибка при поиске элементов товаров: {e}")

    return products


def save_to_csv(products, filename="ozon_products.csv"):
    try:
        df = pd.DataFrame(products)
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        print(f"Данные успешно сохранены в файл {filename}")
    except Exception as e:
        print(f"Ошибка при сохранении данных: {e}")


def main():
    # Ввод поискового запроса
    search_query = input("Введите название товара для поиска на Ozon: ")

    # Настройка драйвера
    driver = setup_driver()

    try:
        # Поиск товаров
        if search_products(driver, search_query):
            # Парсинг товаров
            products = parse_products(driver)

            if products:
                # Сохранение результатов
                save_to_csv(products, f"ozon_{search_query}.csv")
                print(f"Найдено {len(products)} товаров")
            else:
                print("Не удалось найти товары")

    except Exception as e:
        print(f"Произошла ошибка: {e}")

    finally:
        # Закрытие браузера
        driver.quit()
        print("Работа завершена")


if __name__ == "__main__":
    main()
