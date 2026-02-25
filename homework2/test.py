import pytest
import math
import os
import subprocess
import tempfile
from fact import fact_it, fact_rec
from show_employee import show_employee
from sum_and_sub import sum_and_sub
from process_list import process_list, process_list_lc, process_list_gen
from my_sum import my_sum
from email_validation import fun
from fibonacci import fibonacci
from average_scores import compute_average_scores
from plane_angle import Point, plane_angle
from complex_numbers import Complex
from circle_square_mk import circle_square_mk
from log_decorator import function_logger
from people_sort import name_format
from phone_number import sort_phone

# ==================== Тестовые данные ====================

test_data = {
    'fact_it': [
        (1, 1),  # граница: минимум n=1
        (2, 2),
        (5, 120),
        (7, 5040),
        (10, 3628800),
    ],
    'fact_rec': [
        (1, 1),  # граница: минимум n=1
        (2, 2),
        (5, 120),
        (7, 5040),
        (10, 3628800),
    ],
    'show_employee': [
        (("Иванов Иван Иванович", 30000), "Иванов Иван Иванович: 30000 ₽"),
        (("Петров Петр Петрович",), "Петров Петр Петрович: 100000 ₽"),
        (("Сидоров Сидор Сидорович", 0), "Сидоров Сидор Сидорович: 0 ₽"),
        (("Test User", 1000000), "Test User: 1000000 ₽"),
        (("", 50000), ": 50000 ₽"),
        (("Test", -1000), "Test: -1000 ₽"),
    ],
    'sum_and_sub': [
        ((5, 3), (8, 2)),
        ((-5, -3), (-8, -2)),
        ((5, -3), (2, 8)),
        ((5.5, 2.5), (8.0, 3.0)),
        ((0, 0), (0, 0)),
        ((1000.5, 500.5), (1501.0, 500.0)),
        ((-10, -5), (-15, -5)),
    ],
    'process_list': [
        ([1, 2, 3, 4], [1, 4, 27, 16]),
        ([2, 4, 6], [4, 16, 36]),
        ([1, 3, 5], [1, 27, 125]),
        ([5], [125]),  # граница: минимум len(arr)=1
    ],
    'my_sum': [
        ((1, 2), 3),
        ((1, 2, 3, 4, 5), 15),
        ((), 0),
        ((1.5, 2.5, 3.0), 7.0),
        ((-1, -2, -3), -6),
        ((5,), 5),
        ((1000, 2000, 3000), 6000),
        ((10, -5, 3, -2), 6),
    ],
    'email_validation': [
        ("test@example.com", True),
        ("test_user@example.com", True),
        ("test-user@example.com", True),
        ("testexample.com", False),
        ("test@exam!ple.com", False),
        ("test@example.comm", False),  # extension > 3
        ("user123@test45.com", True),
        ("user123@test.com", True),
        ("test@site123.com", True),
        ("test@example", False),
        ("@example.com", False),
        ("test@.com", False),
        ("test@example.abc", True),  # граница: максимум extension=3
    ],
    'fibonacci': [
        (1, [0]),  # граница: минимум n=1
        (2, [0, 1]),
        (5, [0, 1, 1, 2, 3]),
        (8, [0, 1, 1, 2, 3, 5, 8, 13]),
        (10, [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]),
    ],
    'complex_add': [
        ((2, 1, 5, 6), (7, 7)),
        ((100, 200, 50, 75), (150, 275)),
    ],
    'complex_sub': [
        ((2, 1, 5, 6), (-3, -5)),
    ],
    'complex_mul': [
        ((2, 1, 5, 6), (4, 17)),
    ],
    'complex_str': [
        ((2, 1), "2.00+1.00i"),
        ((2, -1), "2.00-1.00i"),
        ((2, 0), "2.00+0.00i"),
        ((0, 5), "0.00+5.00i"),
        ((0, 0), "0.00+0.00i"),
    ],
    'point_sub': [
        ((5, 3, 2, 1, 1, 1), (4, 2, 1)),
        ((-1, -2, -3, -4, -5, -6), (3, 3, 3)),
    ],
    'people_sort': [
        ([["Mike", "Thomson", "20", "M"],
          ["Robert", "Downey", "30", "M"],
          ["Alice", "Wonder", "25", "F"]],
         ["Mr. Mike Thomson", "Ms. Alice Wonder", "Mr. Robert Downey"]),
        ([["Anna", "Smith", "18", "F"],
          ["John", "Doe", "18", "M"]],
         ["Ms. Anna Smith", "Mr. John Doe"]),
        ([["Bob", "Brown", "50", "M"]],
         ["Mr. Bob Brown"]),
    ],
    'phone_number': [
        (["89991234567"], ["+7 (999) 123-45-67"]),
        (["79991234567"], ["+7 (999) 123-45-67"]),
        (["9991234567"], ["+7 (999) 123-45-67"]),
        (["+7(999)123-45-67"], ["+7 (999) 123-45-67"]),
        (["89991234567", "84951112233"],
         ["+7 (495) 111-22-33", "+7 (999) 123-45-67"]),  # проверка сортировки
    ],
    'my_sum_argv': [
        (['1', '2'], '3'),
        (['1', '2', '3', '4', '5'], '15'),
        (['10', '20', '30'], '60'),
    ],
}

# Тестовые данные для проверки обработки ошибок
error_test_data = {
    'fact_it': [
        (0, "Error"),   # n < 1
        (-1, "Error"),  # n < 1
        (100000, "Error"),  # n >= 1000
    ],
    'fact_rec': [
        (0, "Error"),   # n < 1
        (-5, "Error"),  # n < 1
        (100000, "Error"),  # n >= 1000
    ],
    'process_list': [
        ([], "Error"),  # len(arr) < 1
        (list(range(1, 1002)), "Error"),  # len(arr) > 1000
    ],
    'process_list_lc': [
        ([], "Error"),  # len(arr) < 1
        (list(range(1, 1002)), "Error"),  # len(arr) > 1000
    ],
    'process_list_gen': [
        ([], ["Error"]),  # len(arr) < 1
        (list(range(1, 1002)), ["Error"]),  # len(arr) > 1000
    ],
    'fibonacci': [
        (0, "Error"),   # n < 1
        (-1, "Error"),  # n < 1
        (16, "Error"),  # n > 15
        (100, "Error"),  # n > 15
    ],
    'average_scores': [
        ([], "Error"),  # X <= 0
        ([tuple([50.0] * 5) for _ in range(101)], "Error"),  # X > 100
        ([tuple([50.0] * 101)], "Error"),  # N > 100
    ],
}

# ==================== Основные тесты ====================

@pytest.mark.parametrize("input_data, expected", test_data['fact_it'])
def test_fact_it(input_data, expected):
    assert fact_it(input_data) == expected

@pytest.mark.parametrize("input_data, expected", test_data['fact_rec'])
def test_fact_rec(input_data, expected):
    assert fact_rec(input_data) == expected

@pytest.mark.parametrize("input_data, expected", test_data['show_employee'])
def test_show_employee(input_data, expected):
    assert show_employee(*input_data) == expected

@pytest.mark.parametrize("input_data, expected", test_data['sum_and_sub'])
def test_sum_and_sub(input_data, expected):
    assert sum_and_sub(*input_data) == expected

@pytest.mark.parametrize("input_data, expected", test_data['process_list'])
def test_process_list(input_data, expected):
    assert process_list(input_data) == expected

@pytest.mark.parametrize("input_data, expected", test_data['process_list'])
def test_process_list_lc(input_data, expected):
    assert process_list_lc(input_data) == expected

@pytest.mark.parametrize("input_data, expected", test_data['process_list'])
def test_process_list_gen(input_data, expected):
    assert list(process_list_gen(input_data)) == expected

@pytest.mark.parametrize("input_data, expected", test_data['my_sum'])
def test_my_sum(input_data, expected):
    assert my_sum(*input_data) == expected

@pytest.mark.parametrize("input_data, expected", test_data['email_validation'])
def test_email_validation(input_data, expected):
    assert fun(input_data) == expected

@pytest.mark.parametrize("input_data, expected", test_data['fibonacci'])
def test_fibonacci(input_data, expected):
    assert fibonacci(input_data) == expected

# Тесты для average_scores.py
def test_average_scores():
    scores = [(89, 90, 78, 93, 80), (90, 91, 85, 88, 86), (91, 92, 83, 89, 90.5)]
    result = compute_average_scores(scores)
    assert len(result) == 5
    assert abs(result[0] - 90.0) < 0.1

def test_average_scores_boundary_max():
    scores = [tuple([50.0] * 100) for _ in range(100)]  # граница: максимум X=100, N=100
    result = compute_average_scores(scores)
    assert result != "Error" and len(result) == 100

# Тесты для plane_angle.py

@pytest.mark.parametrize("input_data, expected", test_data['point_sub'])
def test_point_sub(input_data, expected):
    p1 = Point(input_data[0], input_data[1], input_data[2])
    p2 = Point(input_data[3], input_data[4], input_data[5])
    p3 = p1 - p2
    assert (p3.x, p3.y, p3.z) == expected

def test_point_dot():
    p1 = Point(1, 2, 3)
    p2 = Point(4, 5, 6)
    assert p1.dot(p2) == 32

def test_point_cross():
    p1 = Point(1, 0, 0)
    p2 = Point(0, 1, 0)
    p3 = p1.cross(p2)
    assert (p3.x, p3.y, p3.z) == (0, 0, 1)

def test_point_absolute():
    p = Point(3, 4, 0)
    assert p.absolute() == 5.0

def test_point_zero_vector():
    p = Point(0, 0, 0)
    assert p.absolute() == 0.0

# Тесты для complex_numbers.py

@pytest.mark.parametrize("input_data, expected", test_data['complex_add'])
def test_complex_add(input_data, expected):
    c1 = Complex(input_data[0], input_data[1])
    c2 = Complex(input_data[2], input_data[3])
    c3 = c1 + c2
    assert (c3.real, c3.imaginary) == expected

@pytest.mark.parametrize("input_data, expected", test_data['complex_sub'])
def test_complex_sub(input_data, expected):
    c1 = Complex(input_data[0], input_data[1])
    c2 = Complex(input_data[2], input_data[3])
    c3 = c1 - c2
    assert (c3.real, c3.imaginary) == expected

@pytest.mark.parametrize("input_data, expected", test_data['complex_mul'])
def test_complex_mul(input_data, expected):
    c1 = Complex(input_data[0], input_data[1])
    c2 = Complex(input_data[2], input_data[3])
    c3 = c1 * c2
    assert (c3.real, c3.imaginary) == expected

def test_complex_div():
    c1 = Complex(2, 1)
    c2 = Complex(5, 6)
    c3 = c1 / c2
    assert abs(c3.real - 0.26) < 0.01 and abs(c3.imaginary - (-0.11)) < 0.01

def test_complex_mod():
    c = Complex(2, 1)
    m = c.mod()
    assert abs(m.real - 2.236) < 0.01

@pytest.mark.parametrize("input_data, expected", test_data['complex_str'])
def test_complex_str(input_data, expected):
    c = Complex(input_data[0], input_data[1])
    assert str(c) == expected

# Тесты для circle_square_mk.py

def test_circle_square_mk_small():
    result = circle_square_mk(1, 1000)
    expected = math.pi
    assert abs(result - expected) < 1.0

def test_circle_square_mk_large():
    result = circle_square_mk(5, 10000)
    expected = math.pi * 25
    assert abs(result - expected) < 5.0

def test_circle_square_mk_zero_radius():
    result = circle_square_mk(0, 100)
    assert result == 0

def test_circle_square_mk_large_experiments():
    result = circle_square_mk(10, 100000)
    expected = math.pi * 100
    assert abs(result - expected) < 10.0

# Тесты для process_list.py: граничные значения

def test_process_list_boundary_max():
    arr = list(range(1, 1001))  # граница: максимум len(arr)=1000
    result = process_list(arr)
    assert result != "Error" and len(result) == 1000

def test_process_list_lc_boundary_max():
    arr = list(range(1, 1001))  # граница: максимум len(arr)=1000
    result = process_list_lc(arr)
    assert result != "Error" and len(result) == 1000

def test_fibonacci_boundary_max():
    result = fibonacci(15)  # граница: максимум n=15
    assert result != "Error" and len(result) == 15 and result[14] == 377

def test_fact_it_boundary_max():
    result = fact_it(999)  # граница: максимум n=999
    assert result != "Error"

# ==================== Тесты обработки ошибок ====================

@pytest.mark.parametrize("input_data, expected", error_test_data['fact_it'])
def test_fact_it_errors(input_data, expected):
    assert fact_it(input_data) == expected

@pytest.mark.parametrize("input_data, expected", error_test_data['fact_rec'])
def test_fact_rec_errors(input_data, expected):
    assert fact_rec(input_data) == expected

@pytest.mark.parametrize("input_data, expected", error_test_data['process_list'])
def test_process_list_errors(input_data, expected):
    assert process_list(input_data) == expected

@pytest.mark.parametrize("input_data, expected", error_test_data['process_list_lc'])
def test_process_list_lc_errors(input_data, expected):
    assert process_list_lc(input_data) == expected

@pytest.mark.parametrize("input_data, expected", error_test_data['process_list_gen'])
def test_process_list_gen_errors(input_data, expected):
    assert list(process_list_gen(input_data)) == expected

@pytest.mark.parametrize("input_data, expected", error_test_data['fibonacci'])
def test_fibonacci_errors(input_data, expected):
    assert fibonacci(input_data) == expected

@pytest.mark.parametrize("input_data, expected", error_test_data['average_scores'])
def test_average_scores_errors(input_data, expected):
    assert compute_average_scores(input_data) == expected

# ==================== Тесты для people_sort.py ====================

@pytest.mark.parametrize("input_data, expected", test_data['people_sort'])
def test_people_sort(input_data, expected):
    assert name_format(input_data) == expected

# ==================== Тесты для phone_number.py ====================

@pytest.mark.parametrize("input_data, expected", test_data['phone_number'])
def test_phone_number(input_data, expected):
    assert sort_phone(input_data) == expected

# ==================== Тесты для log_decorator.py ====================
def test_log_decorator_writes_file(tmp_path):
    # assert tmp_path == ""
    log_file = str(tmp_path / "test.log")

    @function_logger(log_file)
    def add(a, b):
        return a + b

    result = add(2, 3)
    assert result == 5
    assert os.path.exists(log_file)
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()
    assert 'add' in content
    assert '(2, 3)' in content
    assert '5' in content

def test_log_decorator_no_return(tmp_path):
    log_file = str(tmp_path / "test.log")

    @function_logger(log_file)
    def noop():
        pass

    result = noop()
    assert result is None
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()
    assert 'noop' in content
    assert '-' in content  # None записывается как '-'

def test_log_decorator_kwargs(tmp_path):
    log_file = str(tmp_path / "test.log")

    @function_logger(log_file)
    def greet(name="World"):
        return f"Hello, {name}!"

    result = greet(name="Test")
    assert result == "Hello, Test!"
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()
    assert 'greet' in content
    assert "name" in content

def test_log_decorator_multiple_calls(tmp_path):
    log_file = str(tmp_path / "test.log")

    @function_logger(log_file)
    def square(x):
        return x * x

    square(3)
    square(5)
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()
    assert content.count('square') == 2

# ==================== Тесты для my_sum_argv.py (subprocess) ====================

INTERPRETER = 'python'

def run_script(filename, args=None):
    cmd = [INTERPRETER, filename] + (args if args else [])
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return proc.stdout.strip()

@pytest.mark.parametrize("input_data, expected", test_data['my_sum_argv'])
def test_my_sum_argv(input_data, expected):
    assert run_script('my_sum_argv.py', input_data) == expected

# ==================== Тесты для file_search.py (subprocess) ====================

def test_file_search_found(tmp_path):
    test_file = tmp_path / "hello.txt"
    test_file.write_text("line1\nline2\nline3\n", encoding='utf-8')
    result = subprocess.run(
        [INTERPRETER, 'file_search.py', 'hello.txt'],
        capture_output=True, text=True, check=False, cwd=str(tmp_path)
    )

    import shutil
    shutil.copy('file_search.py', str(tmp_path / 'file_search.py'))
    result = subprocess.run(
        [INTERPRETER, 'file_search.py', 'hello.txt'],
        capture_output=True, text=True, check=False, cwd=str(tmp_path)
    )
    assert 'line1' in result.stdout

def test_file_search_not_found(tmp_path):
    import shutil
    shutil.copy('file_search.py', str(tmp_path / 'file_search.py'))
    result = subprocess.run(
        [INTERPRETER, 'file_search.py', 'nonexistent.txt'],
        capture_output=True, text=True, check=False, cwd=str(tmp_path)
    )
    assert 'не найден' in result.stdout

def test_file_search_max_5_lines(tmp_path):
    import shutil
    shutil.copy('file_search.py', str(tmp_path / 'file_search.py'))
    test_file = tmp_path / "many_lines.txt"
    test_file.write_text('\n'.join([f"line{i}" for i in range(10)]), encoding='utf-8')
    result = subprocess.run(
        [INTERPRETER, 'file_search.py', 'many_lines.txt'],
        capture_output=True, text=True, check=False, cwd=str(tmp_path)
    )
    lines = result.stdout.strip().split('\n')
    assert len(lines) == 5  # выводит только первые 5 строк

# ==================== Тесты для files_sort.py (subprocess) ====================

def test_files_sort(tmp_path):
    import shutil
    test_dir = tmp_path / "data"
    test_dir.mkdir()
    (test_dir / "b.txt").write_text("", encoding='utf-8')
    (test_dir / "a.txt").write_text("", encoding='utf-8')
    (test_dir / "c.py").write_text("", encoding='utf-8')
    shutil.copy('files_sort.py', str(tmp_path / 'files_sort.py'))
    result = subprocess.run(
        [INTERPRETER, 'files_sort.py', str(test_dir)],
        capture_output=True, text=True, check=False, cwd=str(tmp_path)
    )
    lines = result.stdout.strip().split('\n')
    # Сортировка: сначала по расширению, потом по имени
    assert lines == ['c.py', 'a.txt', 'b.txt']

def test_files_sort_no_extension(tmp_path):
    import shutil
    test_dir = tmp_path / "data"
    test_dir.mkdir()
    (test_dir / "Makefile").write_text("", encoding='utf-8')
    (test_dir / "a.txt").write_text("", encoding='utf-8')
    shutil.copy('files_sort.py', str(tmp_path / 'files_sort.py'))
    result = subprocess.run(
        [INTERPRETER, 'files_sort.py', str(test_dir)],
        capture_output=True, text=True, check=False, cwd=str(tmp_path)
    )
    lines = result.stdout.strip().split('\n')
    # Файлы без расширения (ext='') идут первыми по sorted
    assert lines[0] == 'Makefile'
