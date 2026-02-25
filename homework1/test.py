import subprocess
import pytest

INTERPRETER = 'python'

def run_script(filename, input_data=None):
    proc = subprocess.run(
        [INTERPRETER, filename],
        input='\n'.join(input_data if input_data else []),
        capture_output=True,
        text=True,
        check=False
    )
    return proc.stdout.strip()

test_data = {
    'python_if_else': [
        ('1', 'Weird'),  # граница: минимум n=1
        ('4', 'Not Weird'),
        ('3', 'Weird'),
        ('6','Weird'), 
        ('22', 'Not Weird'),
        ('2', 'Not Weird'),  
        ('5', 'Weird'),
        ('7', 'Weird'),
        ('19', 'Weird'),
        ('20', 'Weird'),  
        ('21', 'Weird'),  
        ('100', 'Not Weird')  # граница: максимум n=100
    ],
    'arithmetic_operators': [
        (['1', '1'], ['2.0', '0.0', '1.0']),  # граница: минимум a=1, b=1
        (['1', '2'], ['3.0', '-1.0', '2.0']),
        (['10', '5'], ['15.0', '5.0', '50.0']),
        (['10000000000', '10000000000'], ['20000000000.0', '0.0', '1e+20']),  # граница: максимум a=10^10, b=10^10
        (['1', '10000000000'], ['10000000001.0', '-9999999999.0', '10000000000.0'])  # граница: проверка диапазона
    ],
    'division': [
        (['3', '5'], ['0', '0.6']),
        (['10', '2'], ['5', '5.0']),
        (['7', '3'], ['2', '2.3333333333333335']),
        (['100', '10'], ['10', '10.0'])
    ],
    'loops': [
        (['1'], ['0']),  # граница: минимум n=1
        (['3'], ['0', '1', '4']),
        (['5'], ['0', '1', '4', '9', '16']),
        (['10'], ['0', '1', '4', '9', '16', '25', '36', '49', '64', '81']),
        (['20'], ['0', '1', '4', '9', '16', '25', '36', '49', '64', '81', '100', '121', '144', '169', '196', '225', '256', '289', '324', '361'])  # граница: максимум n=20
    ],
    'print_function': [
        (['1'], ['1']),  # граница: минимум n=1
        (['5'], ['12345']),
        (['10'], ['12345678910']),
        (['15'], ['123456789101112131415']),
        (['20'], ['1234567891011121314151617181920'])  # граница: максимум n=20
    ],
    'second_score': [
        (['5', '2 3 6 6 5'], ['5']),
        (['4', '10 20 30 40'], ['30']),
        (['3', '1 1 2'], ['1']),
        (['6', '5 5 5 10 10 15'], ['10'])
    ],
    'nested_list': [
        (['2', 'Harry', '37.21', 'Berry', '37.2'], ['Harry']),  # граница: минимум N=2
        (['3', 'Alice', '50', 'Bob', '45', 'Charlie', '45'], ['Alice']),
        (['5', 'Гарри', '37.21', 'Берри', '37.21', 'Тина', '37.2', 'Акрити', '41', 'Харш', '39'], ['Берри', 'Гарри']),  # граница: максимум N=5
        (['3', 'Ann', '10', 'Bob', '20', 'Carl', '20'], ['Bob', 'Carl'])  # несколько студентов со вторым баллом
    ],
    'swap_case': [
        (['a'], ['A']),  # граница: минимальная длина len(s)=1
        (['Hello'], ['hELLO']),
        (['Www.MosPolytech.ru'], ['wWW.mOSpOLYTECH.RU']),
        (['Pythonist 2'], ['pYTHONIST 2']),
        (['ABC123xyz'], ['abc123XYZ']),
        (['a' * 1000], ['A' * 1000])  # граница: максимальная длина len(s)=1000
    ],
    'split_and_join': [
        (['this is a string'], ['this-is-a-string']),
        (['hello world'], ['hello-world']),
        (['one two three four'], ['one-two-three-four'])
    ],
    'anagram': [
        (['abc', 'bca'], ['YES']),
        (['abc', 'def'], ['NO']),
        (['listen', 'silent'], ['YES']),
        (['hello', 'world'], ['NO']),
        (['test', 'sett'], ['YES'])
    ],
    'is_leap': [
        (['1900'], ['False']),  # граница: минимум year=1900
        (['2000'], ['True']),  # делится на 400
        (['1900'], ['False']),  # делится на 100, но не на 400
        (['2016'], ['True']),  # делится на 4, но не на 100
        (['2017'], ['False']),  # не делится на 4
        (['2400'], ['True']),  # делится на 400
        (['2100'], ['False']),  # делится на 100, но не на 400
        (['2020'], ['True']),
        (['2024'], ['True']),
        (['100000'], ['True'])  # граница: максимум year=10^5, делится на 400
    ],
    'happiness': [
        (['1 1', '1', '1', '2'], ['1']),  # граница: минимум n=1, m=1
        (['3 2', '1 5 3', '3 1', '5 7'], ['1']),
        (['5 3', '1 2 3 4 5', '1 2 3', '4 5 6'], ['1']),
        (['4 2', '10 20 10 20', '10 20', '30 40'], ['4']),
        (['6 2', '1 2 3 4 5 6', '1 3 5', '2 4 6'], ['0']),
        (['3 3', '1000000000 1000000000 1000000000', '1000000000 999999999 999999998', '1 2 3'], ['3'])  # граница: проверка больших чисел (до 10^9)
    ],
    'minion_game': [
        (['A'], ['Kevin 1']),  # граница: минимальная длина len(S)=1 (гласная)
        (['B'], ['Stuart 1']),  # граница: минимальная длина len(S)=1 (согласная)
        (['BANANA'], ['Stuart 12']),
        (['ABC'], ['Draw']),
        (['AEIOUY'], ['Kevin 21']),
        (['A' * 1000000], ['Kevin 500000500000'])  # граница: максимальная длина len(S)=10^6
    ],
    'matrix_mult': [
        (['2', '1 2', '3 4', '5 6', '7 8'], ['19 22', '43 50']),  # граница: минимум n=2
        (['2', '1 0', '0 1', '2 3', '4 5'], ['2 3', '4 5']),
        (['3', '1 2 3', '4 5 6', '7 8 9', '9 8 7', '6 5 4', '3 2 1'], ['30 24 18', '84 69 54', '138 114 90']),
        (['10', '1 0 0 0 0 0 0 0 0 0', '0 1 0 0 0 0 0 0 0 0', '0 0 1 0 0 0 0 0 0 0', '0 0 0 1 0 0 0 0 0 0', '0 0 0 0 1 0 0 0 0 0', '0 0 0 0 0 1 0 0 0 0', '0 0 0 0 0 0 1 0 0 0', '0 0 0 0 0 0 0 1 0 0', '0 0 0 0 0 0 0 0 1 0', '0 0 0 0 0 0 0 0 0 1', '1 2 3 4 5 6 7 8 9 10', '10 9 8 7 6 5 4 3 2 1', '1 1 1 1 1 1 1 1 1 1', '2 2 2 2 2 2 2 2 2 2', '3 3 3 3 3 3 3 3 3 3', '4 4 4 4 4 4 4 4 4 4', '5 5 5 5 5 5 5 5 5 5', '6 6 6 6 6 6 6 6 6 6', '7 7 7 7 7 7 7 7 7 7', '8 8 8 8 8 8 8 8 8 8'], ['1 2 3 4 5 6 7 8 9 10', '10 9 8 7 6 5 4 3 2 1', '1 1 1 1 1 1 1 1 1 1', '2 2 2 2 2 2 2 2 2 2', '3 3 3 3 3 3 3 3 3 3', '4 4 4 4 4 4 4 4 4 4', '5 5 5 5 5 5 5 5 5 5', '6 6 6 6 6 6 6 6 6 6', '7 7 7 7 7 7 7 7 7 7', '8 8 8 8 8 8 8 8 8 8'])  # граница: максимум n=10
    ],
    'lists': [
        (['4', 'append 1', 'append 2', 'insert 1 3', 'print'], ['[1, 3, 2]']),
        (['3', 'append 5', 'append 10', 'print'], ['[5, 10]']),
        (['5', 'insert 0 1', 'insert 1 2', 'insert 2 3', 'sort', 'print'], ['[1, 2, 3]'])
    ],
    'metro': [
        (['2', '10 30', '20 40', '25'], ['2']),
        (['3', '5 15', '10 20', '25 35', '12'], ['2']),
        (['4', '0 10', '5 15', '20 30', '25 35', '10'], ['2'])
    ],
    'max_word': [
        # max_word.py читает из файла example.txt и не принимает входные данные
    ],
    'price_sum': [
        # price_sum.py читает из файла products.csv и не принимает входные данные
        # Ожидаемый вывод: "6842.84 5891.06 6810.90"
    ],
    'pirate_ship': [
        (['10 3', 'золото 5 100', 'серебро 10 80', 'бронза 15 60'], ['золото 5 100', 'серебро 5 40.0']),
        (['50 4', 'алмазы 10 500', 'золото 20 400', 'серебро 30 300', 'бронза 40 200'], ['алмазы 10 500', 'золото 20 400', 'серебро 20 200.0']),
        (['5 2', 'товар1 10 100', 'товар2 3 30'], ['товар1 5 50.0']),
        (['100 1', 'груз 50 1000'], ['груз 50 1000']),  # граница: груз меньше грузоподъемности
        (['10 1', 'груз 20 1000'], ['груз 10 500.0'])  # граница: груз больше грузоподъемности
    ]
}

# Тесты для проверки обработки ошибок (значения вне диапазона)
error_test_data = {
    'python_if_else': [
        ('0', 'Error'),  # n < 1
        ('101', 'Error'),  # n > 100
    ],
    'arithmetic_operators': [
        (['0', '5'], ['Error']),  # a < 1
        (['5', '0'], ['Error']),  # b < 1
        (['10000000001', '5'], ['Error']),  # a > 10^10
        (['5', '10000000001'], ['Error']),  # b > 10^10
    ],
    'loops': [
        (['0'], ['Error']),  # n < 1
        (['21'], ['Error']),  # n > 20
    ],
    'print_function': [
        (['0'], ['Error']),  # n < 1
        (['21'], ['Error']),  # n > 20
    ],
    'nested_list': [
        (['1', 'Alice', '50'], ['Error']),  # N < 2
        (['6', 'A', '1', 'B', '2', 'C', '3', 'D', '4', 'E', '5', 'F', '6'], ['Error']),  # N > 5
    ],
    'swap_case': [
        (['a' * 1001], ['Error']),  # len(s) > 1000
    ],
    'minion_game': [
        (['a' * (10 ** 6 + 1)], ['Error']), # len(s) > 10 ** 6
    ],
    'is_leap': [
        (['1899'], ['Error']),  # year < 1900
        (['100001'], ['Error']),  # year > 10^5
    ],
    'happiness': [
        (['0 5', '1', '1', '2'], ['Error']),  # n < 1
        (['5 0', '1 2 3', '1', '2'], ['Error']),  # m < 1
    ],
    'matrix_mult': [
        (['1'], ['Error']),  # n < 2
        (['11'], ['Error']),  # n > 10
    ],
}

def test_hello():
    assert run_script('hello.py') == 'Hello, world!'

@pytest.mark.parametrize("input_data, expected", test_data['python_if_else'])
def test_python_if_else(input_data, expected):
    assert run_script('python_if_else.py', [input_data]) == expected

@pytest.mark.parametrize("input_data, expected", test_data['arithmetic_operators'])
def test_arithmetic_operators(input_data, expected):
    assert run_script('arithmetic_operators.py', input_data).split('\n') == expected

@pytest.mark.parametrize("input_data, expected", test_data['division'])
def test_division(input_data, expected):
    assert run_script('division.py', input_data).split('\n') == expected

@pytest.mark.parametrize("input_data, expected", test_data['loops'])
def test_loops(input_data, expected):
    assert run_script('loops.py', input_data).split('\n') == expected

@pytest.mark.parametrize("input_data, expected", test_data['print_function'])
def test_print_function(input_data, expected):
    assert run_script('print_function.py', input_data) == expected[0]

@pytest.mark.parametrize("input_data, expected", test_data['second_score'])
def test_second_score(input_data, expected):
    assert run_script('second_score.py', input_data) == expected[0]

@pytest.mark.parametrize("input_data, expected", test_data['nested_list'])
def test_nested_list(input_data, expected):
    result = run_script('nested_list.py', input_data).split('\n')
    assert result == expected

@pytest.mark.parametrize("input_data, expected", test_data['swap_case'])
def test_swap_case(input_data, expected):
    assert run_script('swap_case.py', input_data) == expected[0]

@pytest.mark.parametrize("input_data, expected", test_data['split_and_join'])
def test_split_and_join(input_data, expected):
    assert run_script('split_and_join.py', input_data) == expected[0]

@pytest.mark.parametrize("input_data, expected", test_data['anagram'])
def test_anagram(input_data, expected):
    assert run_script('anagram.py', input_data) == expected[0]

@pytest.mark.parametrize("input_data, expected", test_data['is_leap'])
def test_is_leap(input_data, expected):
    assert run_script('is_leap.py', input_data) == expected[0]

@pytest.mark.parametrize("input_data, expected", test_data['happiness'])
def test_happiness(input_data, expected):
    assert run_script('happiness.py', input_data) == expected[0]

@pytest.mark.parametrize("input_data, expected", test_data['minion_game'])
def test_minion_game(input_data, expected):
    assert run_script('minion_game.py', input_data) == expected[0]

@pytest.mark.parametrize("input_data, expected", test_data['matrix_mult'])
def test_matrix_mult(input_data, expected):
    assert run_script('matrix_mult.py', input_data).split('\n') == expected

@pytest.mark.parametrize("input_data, expected", test_data['lists'])
def test_lists(input_data, expected):
    assert run_script('lists.py', input_data) == expected[0]

@pytest.mark.parametrize("input_data, expected", test_data['metro'])
def test_metro(input_data, expected):
    assert run_script('metro.py', input_data) == expected[0]

def test_max_word():
    # max_word.py читает файл example.txt, поэтому проверяем только что программа запускается
    result = run_script('max_word.py')
    assert len(result) > 0
    words = result.split('\n')
    assert len(words) > 0

def test_price_sum():
    result = run_script('price_sum.py')
    assert result == '6842.84 5891.06 6810.90'

@pytest.mark.parametrize("input_data, expected", test_data['pirate_ship'])
def test_pirate_ship(input_data, expected):
    result = run_script('pirate_ship.py', input_data).split('\n')
    assert result == expected

# Тесты для проверки обработки ошибок (значения вне допустимого диапазона)

@pytest.mark.parametrize("input_data, expected", error_test_data['python_if_else'])
def test_python_if_else_errors(input_data, expected):
    assert run_script('python_if_else.py', [input_data]) == expected

@pytest.mark.parametrize("input_data, expected", error_test_data['arithmetic_operators'])
def test_arithmetic_operators_errors(input_data, expected):
    result = run_script('arithmetic_operators.py', input_data)
    assert result == expected[0]

@pytest.mark.parametrize("input_data, expected", error_test_data['loops'])
def test_loops_errors(input_data, expected):
    assert run_script('loops.py', input_data) == expected[0]

@pytest.mark.parametrize("input_data, expected", error_test_data['print_function'])
def test_print_function_errors(input_data, expected):
    assert run_script('print_function.py', input_data) == expected[0]

@pytest.mark.parametrize("input_data, expected", error_test_data['nested_list'])
def test_nested_list_errors(input_data, expected):
    result = run_script('nested_list.py', input_data)
    assert result == expected[0]

@pytest.mark.parametrize("input_data, expected", error_test_data['swap_case'])
def test_swap_case_errors(input_data, expected):
    assert run_script('swap_case.py', input_data) == expected[0]

@pytest.mark.parametrize("input_data, expected", error_test_data['minion_game'])
def test_minion_game_errors(input_data, expected):
    assert run_script('minion_game.py', input_data) == expected[0]

@pytest.mark.parametrize("input_data, expected", error_test_data['is_leap'])
def test_is_leap_errors(input_data, expected):
    assert run_script('is_leap.py', input_data) == expected[0]

@pytest.mark.parametrize("input_data, expected", error_test_data['happiness'])
def test_happiness_errors(input_data, expected):
    result = run_script('happiness.py', input_data)
    assert result == expected[0]

@pytest.mark.parametrize("input_data, expected", error_test_data['matrix_mult'])
def test_matrix_mult_errors(input_data, expected):
    result = run_script('matrix_mult.py', input_data)
    assert result == expected[0]
