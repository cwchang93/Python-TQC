# def compute(num):
#     a = 0
#     b = 1
#     for _ in range(num):
#         print('xx')
#         print(a, end=" ")
#         a, b = b, a + b


# num = int(input())
# compute(num)


# def compute(num):
#     a = 0
#     b = 1
#     for _ in range(num):
#         print(a, end=" ")
#         temp = a
#         print('temp', temp)
#         a = b
#         print('a', a)
#         b = temp + b
#         print('b', b)



# num = int(input())
# compute(num)

def compute(num):
    a = 0
    b = 1

    for i in range(num):
        print("第", i + 1, "次迴圈", sep="")
        print("目前 a =", a, ", b =", b)
        print("先輸出 a，所以印出:", a)

        temp = a
        print("把原本的 a 暫存到 temp =", temp)

        a = b
        print("a 改成原本的 b，所以現在 a =", a)

        b = temp + b
        print("b 改成 原本的 a + 原本的 b，所以現在 b =", b)

        print("-" * 20)


num = int(input())
compute(num)
