import re
from flask import Flask, render_template, request, make_response

app = Flask(__name__)
application = app

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/url_params/')
def url_params():
    return render_template('url_params.html', title='Параметры URL', params=request.args)

@app.route('/headers/')
def headers():
    return render_template('headers.html', title='Заголовки запроса', headers=request.headers)

@app.route('/cookies/')
def cookies():
    resp = make_response(render_template('cookies.html', title='Cookies', cookies=request.cookies))
    if not request.cookies.get('visited'):
        resp.set_cookie('visited', 'true')
    if not request.cookies.get('sample_cookie'):
        resp.set_cookie('sample_cookie', 'hello_from_lab2')
    return resp

@app.route('/login/', methods=['GET', 'POST'])
def login():
    form_data = None
    if request.method == 'POST':
        form_data = {
            'login': request.form.get('login', ''),
            'password': request.form.get('password', ''),
        }
    return render_template('login.html', title='Форма авторизации', form_data=form_data)

def validate_phone(raw):
    """Validate phone number and return (formatted, error) tuple."""
    allowed = set('0123456789 ()-.+')
    if not all(ch in allowed for ch in raw):
        return None, 'Недопустимый ввод. В номере телефона встречаются недопустимые символы.'

    digits = re.sub(r'\D', '', raw)

    if raw.strip().startswith('+7') or raw.strip().startswith('8'):
        if len(digits) != 11:
            return None, 'Недопустимый ввод. Неверное количество цифр.'
    else:
        if len(digits) != 10:
            return None, 'Недопустимый ввод. Неверное количество цифр.'

    # Normalize to 10-digit local number
    if len(digits) == 11:
        digits = digits[1:]  # drop leading 8 or 7

    formatted = f'8-{digits[0:3]}-{digits[3:6]}-{digits[6:8]}-{digits[8:10]}'
    return formatted, None

@app.route('/phone/', methods=['GET', 'POST'])
def phone():
    error = None
    formatted = None
    phone_value = ''
    if request.method == 'POST':
        phone_value = request.form.get('phone', '')
        formatted, error = validate_phone(phone_value)
    return render_template('phone.html', title='Проверка номера телефона',
                           error=error, formatted=formatted, phone_value=phone_value)

@app.route('/about/')
def about():
    return render_template('about.html', title='Об авторе')
