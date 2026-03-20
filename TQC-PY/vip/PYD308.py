n = int(input())

for _ in range(n):
    x = input().strip()
    total = sum(int(ch) for ch in x)
    print(f"Sum of all digits of {x} is {total}")
