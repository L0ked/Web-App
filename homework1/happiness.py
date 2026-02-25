n, m = map(int, input().split())
if 1 <= n <= 10**5 and 1 <= m <= 10**5:
    arr = list(map(int, input().split()))
    A = set(map(int, input().split()))
    B = set(map(int, input().split()))

    if all(1 <= i <= 10**9 for i in arr):
        happiness = 0
        for i in arr:
            if i in A:
                happiness += 1
            elif i in B:
                happiness -= 1

        print(happiness)
    else:
        print("Error")
else:
    print("Error")
