# парсер сайта https://ranobe-novels.ru/
import time

import requests
from bs4 import BeautifulSoup
from user_agent import choice_user_agent
from zipfile import ZipFile
import os
import random


HEADERS = {
        'User-Agent': choice_user_agent(),
        'accept': '*/*',
        'path': '/f/AGSKWxX5DCelNV50_TQnazSCzoTHwq9hqhkgqu8JIi5x2DuieNPQ22VWtkYtsabsu0wtR4MfqvDn35ptlYQwqw7-c2MvgvS79vEV4UkSIAlfwJznXd--TRq_rF-K-lPYM7VGHwQm2ZjgfMY0x6nExhx8AowAzd0IQH-S-h4b-leLKOCoWoJQjvBRB6jAIIRT?fccs=W1siQUtzUm9sOHpRb1pwdHlndHhIWl93NVVzLVBSNy1DOGZvN0ptVDZXekNKdDFpRUJJRnpQdTFMa2RpWnM3ZVU1eUJiMUJ5VjdLQVd1czJ1NVVrdDRwb3FwSWRraW1UYTJjdWFJTE9PRTdBZW9JZ0FKMm13TjQ5SzRqeXI0aGJIZjRxUi1GUmc1TTBFMHVlUklVTjFpZ0ZSdFFmWjZWS28wTktBPT0iXSxudWxsLG51bGwsbnVsbCxudWxsLG51bGwsWzE2NDc2ODUxMzgsMzgwMDAwMDBdLG51bGwsbnVsbCxudWxsLFtudWxsLFs3LDZdLG51bGwsbnVsbCxudWxsLG51bGwsbnVsbCxudWxsLG51bGwsbnVsbCxudWxsLDFdLCJodHRwczovL21hbmdhcG9pc2sucnUvbWFuZ2EvdmFucGFuY2htZW4vY2hhcHRlci8zMC0yMDIiLG51bGwsW11d'
    }


def ranobe_novels_parser(url, count=1):
    title = url.split("/")[3]
    zip_dir = f'data\\novel_zip\\{title}.zip'
    with ZipFile(zip_dir, mode="w") as myzip:
        for i in range(count):
            HEADERS["User-Agent"] = choice_user_agent()
            content = requests.get(url, headers=HEADERS).text
            soup = BeautifulSoup(content, "lxml")

            text = soup.find("div", class_="mt-5").find_all("p")
            name_dir = f"data\\{title}-{i}.txt"
            with open(name_dir, mode="w", encoding="utf-8") as file:
                for item in text:
                    file.write(item.text + "\n")

            myzip.write(name_dir)
            os.remove(name_dir)
            print("end")

            next_chapter_url = soup.find("a", class_="event-right").get("href")
            url = next_chapter_url
            time.sleep(random.randint(3, 8))

    return zip_dir


if __name__ == "__main__":
    ranobe_novels_parser("https://ranobe-novels.ru/c3072-glava-146-sila-super-gildii/")
