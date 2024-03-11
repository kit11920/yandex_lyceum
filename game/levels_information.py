def get_level_status():
    with open('data\\levels.txt', mode='r', encoding='utf8') as file:
        file = file.readlines()
        dict1 = {}
        for i in file:
            i = i.rstrip().split('=')
            print(i)
            dict1[i[0]] = i[1]
    return dict1


def change_level_status(key):
    dict1 = get_level_status()
    if dict1[key] == 'False':
        dict1[key] = 'True'
    with open('data\\levels.txt', mode='w', encoding='utf8') as file:
        for i in dict1:
            file.write(f'{i}={dict1[i]}\n')
