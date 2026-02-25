import random
import math

def circle_square_mk(r, n):
    inside = 0
    for _ in range(n):
        x = random.uniform(-r, r)
        y = random.uniform(-r, r)
        if x**2 + y**2 <= r**2:
            inside += 1
    square_area = (2 * r) ** 2
    circle_area = square_area * inside / n
    return circle_area
