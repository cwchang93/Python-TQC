data1 = []
data2 = []

print("Create tuple1:")
while True:
    num = int(input())
    if num == -9999:
        break
    data1.append(num)

print("Create tuple2:")
while True:
    num = int(input())
    if num == -9999:
        break
    data2.append(num)

tuple1 = tuple(data1)
tuple2 = tuple(data2)
combined_tuple = tuple1 + tuple2
sorted_list = sorted(combined_tuple)

print("Combined tuple before sorting:", combined_tuple)
print("Combined list after sorting:", sorted_list)
