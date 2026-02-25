def wrapper(f):
    def fun(l):
        normalized = []
        for phone in l:
            digits = ''.join(filter(str.isdigit, phone))
            if len(digits) == 11:
                digits = digits[1:]
            elif len(digits) > 10:
                digits = digits[-10:]
            normalized.append(digits)
        formatted = [f"+7 ({num[:3]}) {num[3:6]}-{num[6:8]}-{num[8:]}" for num in normalized]
        return f(formatted)
    return fun

@wrapper
def sort_phone(l):
    return sorted(l)

if __name__ == '__main__':
    l = [input() for _ in range(int(input()))]
    print(*sort_phone(l), sep='\n')
