import requests
from bs4 import BeautifulSoup
from user_agent import choice_user_agent, random_name_generation
import os
from zipfile import ZipFile

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


# Парсер сайта https://tl.rulate.ru/
def rulate_parser(url, count=1):
    try:
        title = "download_bot_file"
        zip_dir = f"data\\novel_zip\\{title}.zip"
    except IndexError:
        zip_dir = f"data\\novel_zip\\{random_name_generation().replace('.txt', '')}.zip"
    with ZipFile(zip_dir, mode="w") as myzip:
        for chapter_number in range(count):
            HEADERS["User-Agent"] = choice_user_agent()
            content = requests.get(url, headers=HEADERS).text
            soup = BeautifulSoup(content, "lxml")

            text = soup.find("div", class_="content-text")
            print(text)
            try:
                file_name = f"data\\download_bot_chapter{chapter_number + 1}.txt"
            except IndexError:
                file_name = f"data\\{random_name_generation()}"
            with open(file_name, mode="w", encoding="utf-8") as file:
                file.write(soup.find("h1").text + '\n')
            with open(file_name, mode="a", encoding="utf-8") as file:
                for item in text:
                    file.write(item.text + '\n')
            myzip.write(file_name)
            os.remove(file_name)
            print("end")
            next_chapter_url = "https://tl.rulate.ru" + soup.find_all("a", class_="ml")[3].get("href")
            print(next_chapter_url)
            url = next_chapter_url

    return zip_dir


if __name__ == "__main__":
    rulate_parser("https://tl.rulate.ru/book/64510/1737269/ready_new")
