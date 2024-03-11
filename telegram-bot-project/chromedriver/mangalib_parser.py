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


HEADERS = {
        'User-Agent': choice_user_agent(),
        'accept': '*/*',
        'path': '/f/AGSKWxX5DCelNV50_TQnazSCzoTHwq9hqhkgqu8JIi5x2DuieNPQ22VWtkYtsabsu0wtR4MfqvDn35ptlYQwqw7-c2MvgvS79vEV4UkSIAlfwJznXd--TRq_rF-K-lPYM7VGHwQm2ZjgfMY0x6nExhx8AowAzd0IQH-S-h4b-leLKOCoWoJQjvBRB6jAIIRT?fccs=W1siQUtzUm9sOHpRb1pwdHlndHhIWl93NVVzLVBSNy1DOGZvN0ptVDZXekNKdDFpRUJJRnpQdTFMa2RpWnM3ZVU1eUJiMUJ5VjdLQVd1czJ1NVVrdDRwb3FwSWRraW1UYTJjdWFJTE9PRTdBZW9JZ0FKMm13TjQ5SzRqeXI0aGJIZjRxUi1GUmc1TTBFMHVlUklVTjFpZ0ZSdFFmWjZWS28wTktBPT0iXSxudWxsLG51bGwsbnVsbCxudWxsLG51bGwsWzE2NDc2ODUxMzgsMzgwMDAwMDBdLG51bGwsbnVsbCxudWxsLFtudWxsLFs3LDZdLG51bGwsbnVsbCxudWxsLG51bGwsbnVsbCxudWxsLG51bGwsbnVsbCxudWxsLDFdLCJodHRwczovL21hbmdhcG9pc2sucnUvbWFuZ2EvdmFucGFuY2htZW4vY2hhcHRlci8zMC0yMDIiLG51bGwsW11d'
    }


# Парср сайта mangalib
# получение страниц манги
# count - колво глав для загрузки
def mangalib_parser(url, count=1):
    # опции для зпроса, если я правильно понял
    # Возможно, это аналог headers из requests
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

    url = url.split("=")

    title = url[0].split("/")[3]
    postfix = url[0].split("/")[4]
    name_main_dir = f"data\\manga\\{title}-{postfix}"
    os.mkdir(name_main_dir)
    zip_dir = f'data\\manga_zip\\{title}-{postfix}.zip'
    with ZipFile(f'data\\manga_zip\\{title}-{postfix}.zip', 'w') as myzip:
        for _ in range(count):
            options.add_argument(f"user-agent={choice_user_agent()}")
            driver.get(url="=".join(url))
            time.sleep(3)
            # получаем кол-во страниц в главе
            pages_count = int(driver.find_element(By.TAG_NAME, "option").get_attribute("text").split()[-1])
            pic_urls = []

            for page_num in range(1, pages_count + 1):
                # print("ready")
                # print("=".join([url[0], str(page_num)]))
                driver.get(url="=".join([url[0], str(page_num)]))
                time.sleep(random.randint(5, 10))
                array = list(map(lambda x: x.get_attribute("src"), driver.find_elements(By.TAG_NAME, "img")))
                pic_url = [i for i in array if i is not None][0]
                pic_urls.append(pic_url)

            page_number = 1
            title = url[0].split("/")[3]
            postfix = url[0].split("/")[4] + url[0].split("/")[5]
            postfix = postfix.replace('?', '')
            name_dir = f"data\\{title}-{postfix}"
            os.mkdir(name_dir)
            # zip_dir = f'{title}-{postfix.replace("?", "")}.zip'
            for img_url in pic_urls:
                HEADERS['User-Agent'] = choice_user_agent()
                page = requests.get(img_url, headers=HEADERS)
                # out = open(f"manga\\page-{page_number}.bmp", "wb")
                out = open(f"data\\{title}-{postfix}\\page-{page_number}.bmp", "wb")
                out.write(page.content)
                myzip.write(f"data\\{title}-{postfix}\\page-{page_number}.bmp")
                page_number += 1
                out.close()
        # удаляем созданную папку с картинками
            shutil.rmtree(name_dir)
            print("end")

            # next_chapter_url = driver.find_elements(By.TAG_NAME, "a").get_attribute("href")
            soup = BeautifulSoup(driver.page_source, "lxml")
            next_chapter_url = soup.find_all("a", class_="reader-header-action_icon")[1].get("href") + "?page=1"

            print(next_chapter_url)
            url = next_chapter_url
            url = url.split("=")

    os.rmdir(name_main_dir)
    return zip_dir

    # except Exception as e:
    #     print("Error")
    #     print(e)
    # finally:
    #     driver.close()
    #     driver.quit()


if __name__ == "__main__":
    print(mangalib_parser("https://mangalib.me/words-and-spirits/v1/c6?page=1"))
