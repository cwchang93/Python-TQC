# n = int(input())

# for _ in range(n):
#     x = input().strip()
#     total = sum(int(ch) for ch in x)
#     print(f"Sum of all digits of {x} is {total}")

test_count = int(input())

for i in range(test_count):
    number = input()
    digit_sum = 0

    for ch in number:
        digit_sum += int(ch)

    print("Sum of all digits of", number, "is", digit_sum)