n = int(input())
if 1 <= n <= 20:
    result = ""
    for i in range(1, n + 1):
        result += str(i)
    print(result)
else:
    print("Error")
