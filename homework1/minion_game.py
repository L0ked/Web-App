s = input()
if 0 < len(s) <= 10**6:
    vowels = "AEIOUY"
    kevin_score = 0
    stuart_score = 0

    for i in range(len(s)):
        if s[i] in vowels:
            kevin_score += len(s) - i
        else:
            stuart_score += len(s) - i

    if kevin_score > stuart_score:
        print(f"Kevin {kevin_score}")
    elif stuart_score > kevin_score:
        print(f"Stuart {stuart_score}")
    else:
        print("Draw")
else:
    print("Error")
