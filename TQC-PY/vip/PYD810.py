# k = int(input())

# for _ in range(k):
#     numbers = [float(x) for x in input().split()]
#     diff = max(numbers) - min(numbers)
#     print(f"{diff:.2f}")


# k = int(input())

# for _ in range(k):
#     numbers = []
#     for x in data:
#         numbers.append(float(x))
#     diff = max(numbers) - min(numbers)
#     print(f"{diff:.2f}")

count = int(input())

for i in range(count):
    data = input().split()

    numbers = []
    for x in data:
        numbers.append(float(x))

    result = max(numbers) - min(numbers)
    print("%.2f" % result)