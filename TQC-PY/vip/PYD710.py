def creat_dict(key, value):
    data = {}

    while key != 'end':
        key = input("Key: ")

        if key != 'end':
            value = input("Value: ")
            data[key] = value

        if key == 'end':
            return data


my_dict = creat_dict('key', 'value')

search_key = input("Search key: ")

if search_key in my_dict:
    print(True)
else:
    print(False)
