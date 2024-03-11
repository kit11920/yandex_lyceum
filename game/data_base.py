import sqlite3


def get_information():
    """ Получаем результаты из базы данных """
    content = sqlite3.connect("data\\results.db")
    cursor = content.cursor()

    data = cursor.execute("""SELECT * FROM Leader_board""").fetchall()

    cursor.close()

    return data


def update_data_base(arr):
    """ Обновление базы данных, а также расстановка мест"""
    name = arr[0]
    points = arr[1]

    data = get_information()

    data.append((name, points, None))

    data = sorted(data, key=lambda x: (x[1], x[0]))[::-1]

    if len(data) > 5:
        data = data[:5]

    for place, information in enumerate(data):
        new_information = (information[0], information[1], place + 1)
        data[data.index(information)] = new_information

    content = sqlite3.connect("data\\results.db")
    cursor = content.cursor()

    delete_data = """DELETE FROM Leader_board"""
    cursor.execute(delete_data)
    content.commit()

    update = """INSERT INTO Leader_board
    (name, result, place)
    VALUES (?, ?, ?);"""

    for i in data:
        updated_data = i
        cursor.execute(update, updated_data)

        content.commit()

    cursor.close()
