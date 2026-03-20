tuple1 = tuple(map(int, input().split()))
tuple2 = tuple(map(int, input().split()))
merged = sorted(tuple1 + tuple2)
print(*merged)
