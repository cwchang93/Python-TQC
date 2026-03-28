items = {}

while True:
    key = input("Key: ")
    if key == "end":
        break
    value = input("Value: ")
    items[key] = value

query = input("Search key: ")
print(query in items)
