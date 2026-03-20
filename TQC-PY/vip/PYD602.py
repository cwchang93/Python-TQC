cards = []
mapping = {"A": 1, "J": 11, "Q": 12, "K": 13}

for _ in range(5):
    card = input().strip().upper()
    if card in mapping:
        cards.append(mapping[card])
    else:
        cards.append(int(card))

print(sum(cards))
