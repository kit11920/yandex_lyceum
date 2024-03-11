from bs4 import BeautifulSoup
import requests
from user_agent import choice_user_agent
import os
import shutil
from zipfile import ZipFile


# Заголовки
HEADERS = {
        'User-Agent': choice_user_agent(),
        'accept': '*/*',
        'path': '/f/AGSKWxX5DCelNV50_TQnazSCzoTHwq9hqhkgqu8JIi5x2DuieNPQ22VWtkYtsabsu0wtR4MfqvDn35ptlYQwqw7-c2MvgvS79vEV4UkSIAlfwJznXd--TRq_rF-K-lPYM7VGHwQm2ZjgfMY0x6nExhx8AowAzd0IQH-S-h4b-leLKOCoWoJQjvBRB6jAIIRT?fccs=W1siQUtzUm9sOHpRb1pwdHlndHhIWl93NVVzLVBSNy1DOGZvN0ptVDZXekNKdDFpRUJJRnpQdTFMa2RpWnM3ZVU1eUJiMUJ5VjdLQVd1czJ1NVVrdDRwb3FwSWRraW1UYTJjdWFJTE9PRTdBZW9JZ0FKMm13TjQ5SzRqeXI0aGJIZjRxUi1GUmc1TTBFMHVlUklVTjFpZ0ZSdFFmWjZWS28wTktBPT0iXSxudWxsLG51bGwsbnVsbCxudWxsLG51bGwsWzE2NDc2ODUxMzgsMzgwMDAwMDBdLG51bGwsbnVsbCxudWxsLFtudWxsLFs3LDZdLG51bGwsbnVsbCxudWxsLG51bGwsbnVsbCxudWxsLG51bGwsbnVsbCxudWxsLDFdLCJodHRwczovL21hbmdhcG9pc2sucnUvbWFuZ2EvdmFucGFuY2htZW4vY2hhcHRlci8zMC0yMDIiLG51bGwsW11d'
    }


# Получение html кода странциы
def get_html(url):
    req = requests.get(url, headers=HEADERS)
    return req.text


# считывание данных из файла с html кодом
def read_html():
    with open("code.html", "r", encoding="utf-8") as file:
        return file.read()


# запись html кода, делается это для того, чтобы не делать лишние запросы, а считывать html код из файла
def write_html(url):
    with open("code.html", "w", encoding="utf-8") as file:
        file.write(get_html(url))


# Парсер https://mangapoisk.ru/
def parser_mangapoisk(url, count=1):
    title = url.split("/")[4]
    postfix = url.split("/")[-1]
    name_main_dir = f"data\\manga\\{title}-{postfix}"
    os.mkdir(name_main_dir)
    zip_dir = f'data\\manga_zip\\{title}-{postfix}.zip'
    with ZipFile(f'data\\manga_zip\\{title}-{postfix}.zip', 'w') as myzip:
        for _ in range(count):
            """Код для получения контента по ссылке"""
            content = get_html(url)

            soup = BeautifulSoup(content, features="lxml")
            # список всех тегов, которые содержат ссылки на страницы манги
            # все страницы находятся в блоке с тегом div, класс тега - chapter-images
            items = soup.find_all("div", class_="chapter-images")[0].find_all("img")

            # Список с ссылками на все страницы
            array = []
            for item in items:
                array.append(item.get("data-src"))

            page_number = 1
            # Название файла
            title = url.split("/")[4]
            postfix = url.split("/")[-1]
            name_dir = f"data\\{title}-{postfix}"
            os.mkdir(name_dir)
            # zip_dir = f'{title}-{postfix}.zip'
            for i in array[1:]:
                HEADERS['User-Agent'] = choice_user_agent()
                img = requests.get(i, headers=HEADERS)
                out = open(f"data\\{title}-{postfix}\\page-{page_number}.bmp", "wb")
                out.write(img.content)
                myzip.write(f"data\\{title}-{postfix}\\page-{page_number}.bmp")
                page_number += 1
                out.close()
        # удаляем созданную папку с картинками
            shutil.rmtree(name_dir)
            print(name_dir)
            print("end")

            # ссылка на следующую главу
            new_chapter_url = "https://mangapoisk.ru" + soup.find("a", class_="btn-primary").get("href")
            url = new_chapter_url
    # удаление родительской папки
    os.rmdir(name_main_dir)
    return zip_dir


if __name__ == "__main__":
    parser_mangapoisk("https://mangapoisk.ru/manga/berserk/chapter/26-240")
