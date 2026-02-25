year = int(input())
if 1900 <= year <= 10**5:
    if year % 400 == 0:
        print(True)
    elif year % 100 == 0:
        print(False)
    elif year % 4 == 0:
        print(True)
    else:
        print(False)
else:
    print("Error")
