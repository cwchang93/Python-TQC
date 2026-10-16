import math

n = int(input())
s = float(input())
area = (n * math.pow(s, 2)) / (4 * math.tan(math.pi / n))
print(f"Area = {area:.4f}")
