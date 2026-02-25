n = int(input())
if 2 <= n <= 5:
    students = []
    for _ in range(n):
        name = input()
        score = float(input())
        students.append([name, score])

    scores = sorted(set([s[1] for s in students]))
    second_lowest = scores[1]

    names = sorted([s[0] for s in students if s[1] == second_lowest])
    for name in names:
        print(name)
else:
    print("Error")
