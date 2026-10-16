with open("read.txt", "r", encoding="utf-8") as file:
    content = file.read()

numbers = content.split()
total = 0

for num in numbers:
    total += int(num)

print(total)
