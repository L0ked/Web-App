n = int(input())
if 2 <= n <= 10:
    A = []
    for _ in range(n):
        A.append(list(map(int, input().split())))

    B = []
    for _ in range(n):
        B.append(list(map(int, input().split())))

    result = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            for k in range(n):
                result[i][j] += A[i][k] * B[k][j]

    for row in result:
        print(' '.join(map(str, row)))
else:
    print("Error")
