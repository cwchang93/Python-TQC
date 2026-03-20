digits = [int(ch) for ch in input().strip() if ch.isdigit()]
print(max(digits) - min(digits))
