from pathlib import Path

path = Path("PYD906.txt")
text = input()
old, new = input().split()

path.write_text(text)
print(path.read_text().replace(old, new))
