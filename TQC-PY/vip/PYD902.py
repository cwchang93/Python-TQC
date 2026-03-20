from pathlib import Path

path = Path("PYD902.txt")
values = []

while True:
    try:
        values.append(input().strip())
    except EOFError:
        break

path.write_text("\n".join(values))
numbers = [int(line) for line in path.read_text().splitlines() if line.strip()]
print(sum(numbers))
