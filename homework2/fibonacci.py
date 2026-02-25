cube = lambda x: x**3

def fibonacci(n):
    if n < 1 or n > 15:
        return "Error"
    if n == 1:
        return [0]
    result = [0, 1]
    for i in range(2, n):
        result.append(result[-1] + result[-2])
    return result

if __name__ == '__main__':
    n = int(input())
    print(list(map(cube, fibonacci(n))))
