s = input()
if 0 < len(s) <= 1000:
    result = ""
    for c in s:
        if c.isupper():
            result += c.lower()
        elif c.islower():
            result += c.upper()
        else:
            result += c
    print(result)
else:
    print("Error")
