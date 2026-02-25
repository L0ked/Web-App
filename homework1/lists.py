n = int(input())
arr = []
try:
    for _ in range(n):
        command = input().split()
        cmd = command[0]
        if cmd == "insert":
            arr.insert(int(command[1]), int(command[2]))
        elif cmd == "print":
            print(arr)
        elif cmd == "remove":
            arr.remove(int(command[1]))
        elif cmd == "append":
            arr.append(int(command[1]))
        elif cmd == "sort":
            arr.sort()
        elif cmd == "pop":
            arr.pop()
        elif cmd == "reverse":
            arr.reverse()
except (ValueError, IndexError):
    print("Error")
