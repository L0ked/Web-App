s1 = input()
s2 = input()

if s1.isascii() and s2.isascii() and ' ' not in s1 and ' ' not in s2:
    if sorted(s1) == sorted(s2):
        print("YES")
    else:
        print("NO")
else:
    print("Error")
