def process_list(arr):
    if len(arr) < 1 or len(arr) > 1000:
        return "Error"
    result = []
    for i in arr:
        if i % 2 == 0:
            result.append(i**2)
        else:
            result.append(i**3)
    return result

def process_list_lc(arr):
    if len(arr) < 1 or len(arr) > 1000:
        return "Error"
    return [i**2 if i % 2 == 0 else i**3 for i in arr]

def process_list_gen(arr):
    if len(arr) < 1 or len(arr) > 1000:
        yield "Error"
        return
    for i in arr:
        yield i**2 if i % 2 == 0 else i**3

if __name__ == '__main__':
    import time

    test_arr = list(range(1, 1000))

    start = time.time()
    for _ in range(10):
        process_list(test_arr)
    orig_time = time.time() - start

    start = time.time()
    for _ in range(10):
        process_list_lc(test_arr)
    lc_time = time.time() - start

    start = time.time()
    for _ in range(10):
        list(process_list_gen(test_arr))
    gen_time = time.time() - start

    print(f"Исходная: {orig_time}с") # 0.0019960403442382812
    print(f"List comprehension: {lc_time}с") # 0.001004934310913086
    print(f"Генератор: {gen_time}с") # 0.0009999275207519531
