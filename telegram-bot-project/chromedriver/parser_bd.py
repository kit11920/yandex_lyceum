from bs4 import BeautifulSoup
import requests
from user_agent import choice_user_agent
import os
import shutil
from zipfile import ZipFile
from data_db import db_session
from data_db.manga import Manga

WEBSITE = 'https://mangapoisk.ru'
db_session.global_init("db/catalog_manga.sqlite")

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


# возвращает списко ссылок на страницу манги
def get_url_list_manga(url):
    """Код для получения контента по ссылке"""
    content = get_html(url)
    soup = BeautifulSoup(content, features="lxml")
    all_manga_block = soup.find_all('article', class_='flex-item card mx-1 mx-md-2 mb-3 shadow-sm rounded')
    links = list()
    for manga_block in all_manga_block:
        link = manga_block.find('a', class_='px-1 py-1').get('href')
        # link = url + '/' + link.split('/')[-1]
        link = WEBSITE + link
        links.append(link)
    return links


# получает ссылку на страницу манги
# возвращает имя на первую страницу
def get_name_manga(url):
    """Код для получения контента по ссылке"""
    content = get_html(url)
    soup = BeautifulSoup(content, features="lxml")
    name_rus = soup.find('span', class_='post-name').text.lower()
    # попытка вытащить другие имена манги ПРОДОЛЖЕНИЕ СЛУДЕТ...
    # name_en = soup.find('span', class_='post-name-en h5').text
    # name_other_block = soup.find('div', class_='col-md-7 col-lg-8')
    # name_other = name_other_block.find('h2', class_='h6').text

    return name_rus


# возвращает следующую страницу из каталога
def url_next_page_catalog(url):
    """Код для получения контента по ссылке"""
    content = get_html(url)
    soup = BeautifulSoup(content, features="lxml")
    href_block = soup.find_all('li', class_='page-item')[-1]
    href = href_block.find('a').get('href')
    return href


# получает ссылку на страницу манги
# возвращаетссылку на первую страницу
def get_url_manga_frst_page(url):
    """Код для получения контента по ссылке"""
    content = get_html(url)
    soup = BeautifulSoup(content, features="lxml")
    href = soup.find('a', class_='btn btn-outline-primary').get('href')
    href = WEBSITE + href
    return href


def parser_catalog(url_catalog, st=1, end=2):
    db_sess = db_session.create_session()
    for i in range(st, end + 1):
        url_list = get_url_list_manga(url_catalog)
        # get_name_url_manga(url_list[0])
        for url in url_list:
            try:
                manga = Manga()
                manga.name = get_name_manga(url)
                manga.url = get_url_manga_frst_page(url)
                db_sess.add(manga)
                db_sess.commit()
            except Exception:
                pass
        print(i + 24)
        url_catalog = url_next_page_catalog(url_catalog)


if __name__ == "__main__":
    parser_catalog('https://mangapoisk.ru/manga?page=24', st=74, end=224)