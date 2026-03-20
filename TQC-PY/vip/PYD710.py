items = {}

for item in input().split():
    key, value = item.split(":")
    items[key] = value

query = input()
print(items[query])
