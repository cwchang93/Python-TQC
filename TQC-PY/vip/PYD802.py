text = input()
total = 0

for ch in text:
    code = ord(ch)
    print("ASCII code for '{}' is {}".format(ch, code))
    total += code

print(total)

# Python ord() / chr() 官方文件
# https://docs.python.org/3/library/functions.html#ord
# https://docs.python.org/3/library/functions.html#chr

# Python Unicode HOWTO
# https://docs.python.org/3/howto/unicode.html

# ASCII 簡介與對照表
# https://en.wikipedia.org/wiki/ASCII