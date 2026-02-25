import sys

def my_sum(*args):
    return sum(args)

if __name__ == '__main__':
    numbers = [float(x) for x in sys.argv[1:]]
    print(int(my_sum(*numbers)))
