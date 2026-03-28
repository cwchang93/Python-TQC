file_name = input()
s1 = input()
s2 = input()

with open(file_name, "r", encoding="utf-8") as file:
    content = file.read()

print("=== Before the replacement")
print(content)

new_content = content.replace(s1, s2)

print("=== After the replacement")
print(new_content)

with open(file_name, "w", encoding="utf-8") as file:
    file.write(new_content)
