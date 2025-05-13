import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def setup_driver():
    """Настройка ChromeDriver с автоматическим подбором версии."""
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # options.add_argument("--headless=new")  # Раскомментировать для фонового режима

    # Добавляем дополнительные опции для лучшего обнаружения элементов
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-notifications")
    options.add_argument("--lang=ru-RU")

    # Автоматическая загрузка ChromeDriver
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver


def search_products(driver, search_query):
    """Поиск товаров на Ozon."""
    driver.get("https://www.ozon.ru/")

    try:
        # Ожидание и ввод запроса
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Искать на Ozon']"))
        ).send_keys(search_query + Keys.RETURN)

        # Ждем загрузки результатов
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-widget='searchResultsV2']"))
        )

        # Прокрутка для загрузки всех товаров
        last_height = driver.execute_script("return document.body.scrollHeight")
        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        return True
    except Exception as e:
        print(f"🚨 Ошибка при поиске: {e}")
        return False


def parse_products(driver):
    """Парсинг товаров из HTML."""
    products = []
    try:
        # Новые селекторы для Ozon 2024
        items = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[data-widget='searchResultsV2'] div[data-widget='megaPaginator'] div > div > div"))
        )
        print(f"🔍 Найдено {len(items)} товаров")

        for item in items:
            try:
                name = item.find_element(By.CSS_SELECTOR, "a span[title]").get_attribute("title")
                price = item.find_element(By.CSS_SELECTOR, "span[data-widget='megaPaginator'] span[aria-label='Цена']").text.replace("₽", "").strip()
                link = item.find_element(By.CSS_SELECTOR, "a[href]").get_attribute("href")

                products.append({
                    "name": name,
                    "price": price,
                    "link": link
                })
            except Exception as e:
                print(f"⚠️ Ошибка парсинга товара: {e}")

    except Exception as e:
        print(f"🚨 Ошибка при парсинге: {e}")

    return products


def save_to_json(data, filename="ozon_products.json"):
    """Сохранение данных в JSON."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"💾 Данные сохранены в {filename}")


def main():
    search_query = input("🔎 Введите товар для поиска: ")
    driver = setup_driver()

    try:
        if search_products(driver, search_query):
            products = parse_products(driver)
            if products:
                save_to_json(products, f"ozon_{search_query}.json")
                print(f"🎉 Успешно собрано {len(products)} товаров!")
            else:
                print("❌ Товары не найдены. Попробуйте изменить селекторы.")
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")
    finally:
        driver.quit()
        print("✅ Работа завершена")


if __name__ == "__main__":
    main()