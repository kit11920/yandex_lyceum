# парсер ranobelib
# Так как на сайте есть защита, то придется использовать selenium

from seleniumwire import webdriver
import requests
from selenium.webdriver.common.by import By
import time
import random
from user_agent import choice_user_agent
import os
from zipfile import ZipFile
import shutil
from bs4 import BeautifulSoup


# получение текста новеллы
# count - кол-во глав для загрузки
def ranobelib_parser(url, count=1):
    options = webdriver.ChromeOptions()
    # передача в options user-agent
    options.add_argument(f"user-agent={choice_user_agent()}")
    # убираем режим webdriver, это поможет сделать видимость, что запрос отправялет человек
    options.add_argument("--disable-blink-features=AutomationControlled")

    # Запуск в фоновом режиме(оконо chrome не будет открываться)
    options.add_argument("--headless")

    # это нужно, так как нужен абсолютный путь к chromedriver.exe
    chromedriver_path = os.path.abspath("chromedriver.exe")
    driver = webdriver.Chrome(
        executable_path=chromedriver_path,
        options=options)

    title = url.split("/")[3]
    postfix = url.split("/")[4] + url.split("/")[5].split("?")[0]
    zip_dir = f'data\\novel_zip\\{title}-{postfix}.zip'
    with ZipFile(f'data\\novel_zip\\{title}-{postfix}.zip', 'w') as myzip:
        for _ in range(count):
            options.add_argument(f"user-agent={choice_user_agent()}")
            driver.get(url=url)
            time.sleep(random.randint(1, 3))
            content = BeautifulSoup(driver.page_source, "lxml")
            text = content.find("div", class_="container_center")
            title = url.split("/")[3]
            postfix = url.split("/")[4] + url.split("/")[5].split("?")[0]
            name_dir = f"data\\{title}-{postfix}.txt"
            with open(name_dir, mode="w", encoding="utf-8") as file:
                file.write(f"Том {url.split('/')[4][1:]}, Глава {url.split('/')[5].split('?')[0][1:]}\n")
            with open(name_dir, mode="a", encoding="utf-8") as file:
                for i in text:
                    file.write(i.text + "\n")
            myzip.write(name_dir)
            os.remove(name_dir)
            print("end")

            next_chapter_url = content.find("a", class_="button_label_right").get("href")
            url = next_chapter_url
            time.sleep(random.randint(8, 15))

    return zip_dir


if __name__ == "__main__":
    print(ranobelib_parser("https://ranobelib.me/ascendance-of-a-bookworm-novel/v15/c361?bid=6873"))
