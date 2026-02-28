import re
from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
application = app
app.secret_key = 'super-secret-key-lab3'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Для доступа к данной странице необходимо пройти процедуру аутентификации.'
login_manager.login_message_category = 'warning'

# --- Users (lab3) ---

class User(UserMixin):
    def __init__(self, user_id, username, password):
        self.id = user_id
        self.username = username
        self.password = password

users = {
    '1': User('1', 'user', 'qwerty'),
}

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

def find_user(username, password):
    for u in users.values():
        if u.username == username and u.password == password:
            return u
    return None

# --- Phone validation (lab2) ---

def validate_phone(raw):
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

    if len(digits) == 11:
        digits = digits[1:]

    formatted = f'8-{digits[0:3]}-{digits[3:6]}-{digits[6:8]}-{digits[8:10]}'
    return formatted, None

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

# Lab2: request data pages
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
        resp.set_cookie('sample_cookie', 'hello_from_lab3')
    return resp

# Lab2: form data display (авторизационная форма для демонстрации параметров формы)
@app.route('/form/', methods=['GET', 'POST'])
def form():
    form_data = None
    if request.method == 'POST':
        form_data = {
            'login': request.form.get('login', ''),
            'password': request.form.get('password', ''),
        }
    return render_template('form.html', title='Параметры формы', form_data=form_data)

# Lab2: phone validation
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

# Lab3: visits counter
@app.route('/visits/')
def visits():
    session['visits'] = session.get('visits', 0) + 1
    return render_template('visits.html', title='Счётчик посещений', count=session['visits'])

# Lab3: authentication
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('login', '')
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'
        user = find_user(username, password)
        if user:
            login_user(user, remember=remember)
            flash('Вы успешно вошли в систему!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Неверный логин или пароль.', 'danger')
    return render_template('login.html', title='Вход')

@app.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('index'))

# Lab3: secret page
@app.route('/secret/')
@login_required
def secret():
    return render_template('secret.html', title='Секретная страница')

@app.route('/about/')
def about():
    return render_template('about.html', title='Об авторе')
