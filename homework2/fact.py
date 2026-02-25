import time

def fact_rec(n):
    if n < 1 or n >= 100000:
        return "Error"
    if n <= 1:
        return 1
    return n * fact_rec(n - 1)

def fact_it(n):
    if n < 1 or n >= 100000:
        return "Error"
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

if __name__ == '__main__':
    n = 999

    max_it = 0
    for _ in range(1000):
        start_1 = time.time()
        fact_it(n)
        it_time = time.time() - start_1
        if max_it < it_time: max_it = it_time
    
    max_rec = 0
    for _ in range(1000):
        start_2 = time.time()
        fact_rec(n)
        rec_time = time.time() - start_2
        if max_rec < rec_time: max_rec = rec_time

    print(f"Итеративная: {max_it}с") # 0.001142740249633789
    print(f"Рекурсивная: {max_rec}с") # 0.0011646747589111328
