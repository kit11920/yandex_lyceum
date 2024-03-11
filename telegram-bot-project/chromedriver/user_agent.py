import random


# Функция, которая выбирвет случайный user-agent
# Делается это для того, чтобы уменьшить риск блокировки парсера на сайте
def choice_user_agent():
    with open("user-agent_list.txt", mode="r", encoding="utf-8") as file:
        file = file.readlines()
        return random.choice(file).rstrip("\n")


# Случайные имена для файлов с новеллами
def random_name_generation():
    symbols = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'a',
               's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'z', 'x', 'c', 'v', 'b', 'n', 'm']

    file_name = ''
    for _ in range(1, 31):
        file_name += random.choice(symbols)

    return file_name + ".txt"


if __name__ == "__main__":
    print(choice_user_agent())
