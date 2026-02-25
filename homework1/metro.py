n = int(input())
passengers = []
valid = True
for _ in range(n):
    a, b = map(int, input().split())
    
    if a < b:
        passengers.append((a, b))
    else:
        valid = False
        break

if valid and passengers:
    t = int(input())
    count = 0
    for a, b in passengers:
        if a <= t <= b:
            count += 1
    print(count)
else:
    if not valid:
        t = input()
    print("Error")
