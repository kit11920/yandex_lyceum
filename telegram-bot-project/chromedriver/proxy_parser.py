import requests
from bs4 import BeautifulSoup
from user_agent import choice_user_agent
import random

# import urllib
# import socket


# возвращает список прокси вида 'socks5://ip:port'
# Парсер proxy, который будет давать список с proxy, которые будут использованы в дальнейшем при парсинге
# На данный момент это просто заготовка, так как использовать ее пока негде
# https://best-proxies.ru/proxylist/free/ - сайт с proxy
# https://hidemy.name/ru/proxy-list/ - НА САМОМ ДЕЛЕ ЭТОТ САЙТ
def proxy_parser():
    # Заголовки запроса
    HEADERS = {
        'User-Agent': choice_user_agent(),
        'accept': '*/*',
        'path': '/f/AGSKWxX5DCelNV50_TQnazSCzoTHwq9hqhkgqu8JIi5x2DuieNPQ22VWtkYtsabsu0wtR4MfqvDn35ptlYQwqw7-c2MvgvS79vEV4UkSIAlfwJznXd--TRq_rF-K-lPYM7VGHwQm2ZjgfMY0x6nExhx8AowAzd0IQH-S-h4b-leLKOCoWoJQjvBRB6jAIIRT?fccs=W1siQUtzUm9sOHpRb1pwdHlndHhIWl93NVVzLVBSNy1DOGZvN0ptVDZXekNKdDFpRUJJRnpQdTFMa2RpWnM3ZVU1eUJiMUJ5VjdLQVd1czJ1NVVrdDRwb3FwSWRraW1UYTJjdWFJTE9PRTdBZW9JZ0FKMm13TjQ5SzRqeXI0aGJIZjRxUi1GUmc1TTBFMHVlUklVTjFpZ0ZSdFFmWjZWS28wTktBPT0iXSxudWxsLG51bGwsbnVsbCxudWxsLG51bGwsWzE2NDc2ODUxMzgsMzgwMDAwMDBdLG51bGwsbnVsbCxudWxsLFtudWxsLFs3LDZdLG51bGwsbnVsbCxudWxsLG51bGwsbnVsbCxudWxsLG51bGwsbnVsbCxudWxsLDFdLCJodHRwczovL21hbmdhcG9pc2sucnUvbWFuZ2EvdmFucGFuY2htZW4vY2hhcHRlci8zMC0yMDIiLG51bGwsW11d'
    }

    content = requests.get(url="https://hidemy.name/ru/proxy-list/", headers=HEADERS).text
    soup = BeautifulSoup(content, "lxml")

    arr = soup.find("table").find_all("tr")
    proxy_list = []
    for item in arr[1:]:
        country = item.find("td").find_next().find_next().find("span", class_="country").text
        # print(country)
        if country != "Russian Federation":
            # print(item.find_all('td'))
            item_list = item.find_all('td')
            # [протокол, адрес, порт]
            one_proxy = [str(item_list[4])[4:-5].lower(), str(item_list[0])[4:-5], str(item_list[1])[4:-5]]
            # print(one_proxy)
            one_proxy = f'{one_proxy[0]}://{one_proxy[1]}:{one_proxy[2]}'
            proxy_list.append(one_proxy)

            # было
            # proxy_list.append(f'{item.find("td").get_text()}:{item.find("td").find_next().get_text()}')

    # for i in proxy_list:
    #     print(i)
    # return random.choice(proxy_list)
    return proxy_list

# def get_session(proxies):
#     # создать HTTP‑сеанс
#     session = requests.Session()
#     # выбираем один случайный прокси
#     proxy = random.choice(proxies)
#     session.proxies = {"http": proxy, "https": proxy}
#     return session
#
#
# def get_one_proxy():
#     proxies = proxy_parser()
#     # print(proxies)
#     for i in range(5):
#         s = get_session(proxies)
#         try:
#             return s.get("http://icanhazip.com", timeout=1.5).text.strip()
#             # print("Страница запроса с IP:", s.get("http://icanhazip.com", timeout=1.5).text.strip())
#         except Exception as e:
#             continue


# проверяет прокси на работоспособность (таймаут или нет)
# хочешь увелитьчить проверку маймаута измени переменую timeout
def get_one_proxy():
    proxies_all = proxy_parser()
    reg = proxies_all
    url = 'https://www.baidu.com/'
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'}
    can_use = []
    for i in reg:
        try:
            # print(i.split(':')[1])
            proxy = {i.split(':')[0]: i.split(':')[1][2:]}
            response = requests.get(url, headers, proxies=proxy, timeout=1)
            if response.status_code == 200:
                can_use.append(i)
                return i
        except Exception as e:
            print('проблема появляется', e)
    return can_use


if __name__ == "__main__":
    # возвращает проверенный прокси

    print(get_one_proxy())
