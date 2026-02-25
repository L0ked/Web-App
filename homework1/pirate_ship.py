n, m = map(int, input().split())
items = []
for _ in range(m):
    parts = input().split()
    name = parts[0]
    weight = int(parts[1])
    value = int(parts[2])
    items.append((name, weight, value, value / weight))

items.sort(key=lambda x: x[3], reverse=True)

remaining = n
for name, weight, value, ratio in items:
    if remaining == 0:
        break
    if weight <= remaining:
        print(f"{name} {weight} {value}")
        remaining -= weight
    else:
        new_weight = remaining
        new_value = round(ratio * remaining, 2)
        print(f"{name} {new_weight} {new_value}")
        remaining = 0
