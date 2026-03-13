import os
import re
import sqlite3
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response, g
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
application = app
app.secret_key = 'super-secret-key-lab4'

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Для доступа к данной странице необходимо пройти процедуру аутентификации.'
login_manager.login_message_category = 'warning'

# ============================================================
# Database helpers
# ============================================================

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys = ON')
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = sqlite3.connect(DATABASE)
    db.execute('PRAGMA foreign_keys = ON')
    db.executescript('''
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            last_name TEXT,
            first_name TEXT NOT NULL,
            middle_name TEXT,
            role_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (role_id) REFERENCES roles(id)
        );
    ''')
    # Seed roles if empty
    cur = db.execute('SELECT COUNT(*) FROM roles')
    if cur.fetchone()[0] == 0:
        db.executemany('INSERT INTO roles (name, description) VALUES (?, ?)', [
            ('Администратор', 'Полный доступ к системе'),
            ('Пользователь', 'Базовый доступ'),
            ('Модератор', 'Управление контентом'),
        ])
    # Seed admin user if no users
    cur = db.execute('SELECT COUNT(*) FROM users')
    if cur.fetchone()[0] == 0:
        db.execute(
            'INSERT INTO users (login, password_hash, last_name, first_name, middle_name, role_id) VALUES (?, ?, ?, ?, ?, ?)',
            ('user', generate_password_hash('qwerty'), 'Петрачков', 'Владимир', 'Владимирович', 1)
        )
    db.commit()
    db.close()

with app.app_context():
    init_db()

# ============================================================
# User model for Flask-Login
# ============================================================

class User(UserMixin):
    def __init__(self, row):
        self.id = row['id']
        self.login = row['login']
        self.password_hash = row['password_hash']
        self.last_name = row['last_name'] or ''
        self.first_name = row['first_name']
        self.middle_name = row['middle_name'] or ''
        self.role_id = row['role_id']

    @property
    def full_name(self):
        parts = [self.last_name, self.first_name, self.middle_name]
        return ' '.join(p for p in parts if p)

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    row = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if row:
        return User(row)
    return None

# ============================================================
# Validation
# ============================================================

def validate_login(login):
    errors = []
    if not login:
        errors.append('Поле не может быть пустым.')
    elif len(login) < 5:
        errors.append('Логин должен содержать не менее 5 символов.')
    elif not re.match(r'^[a-zA-Z0-9]+$', login):
        errors.append('Логин должен состоять только из латинских букв и цифр.')
    return errors

def validate_password(password):
    errors = []
    if not password:
        errors.append('Поле не может быть пустым.')
        return errors
    if len(password) < 8:
        errors.append('Пароль должен содержать не менее 8 символов.')
    if len(password) > 128:
        errors.append('Пароль должен содержать не более 128 символов.')
    if ' ' in password:
        errors.append('Пароль не должен содержать пробелы.')
    if not re.search(r'[a-zA-Zа-яА-ЯёЁ]', password):
        errors.append('Пароль должен содержать хотя бы одну букву.')
    else:
        if not re.search(r'[A-ZА-ЯЁ]', password):
            errors.append('Пароль должен содержать хотя бы одну заглавную букву.')
        if not re.search(r'[a-zа-яё]', password):
            errors.append('Пароль должен содержать хотя бы одну строчную букву.')
    if not re.search(r'[0-9]', password):
        errors.append('Пароль должен содержать хотя бы одну цифру.')
    allowed = re.compile(r'^[a-zA-Zа-яА-ЯёЁ0-9~!?@#$%^&*_\-+\(\)\[\]\{\}<>/\\|"\'\.,:;]+$')
    if not allowed.match(password):
        errors.append('Пароль содержит недопустимые символы.')
    return errors

def validate_user_form(form, is_edit=False):
    errors = {}

    if not is_edit:
        login_errors = validate_login(form.get('login', ''))
        if login_errors:
            errors['login'] = login_errors

        password_errors = validate_password(form.get('password', ''))
        if password_errors:
            errors['password'] = password_errors

    if not form.get('first_name', '').strip():
        errors['first_name'] = ['Поле не может быть пустым.']

    if not form.get('last_name', '').strip():
        errors['last_name'] = ['Поле не может быть пустым.']

    return errors

# ============================================================
# Lab2: phone validation
# ============================================================

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

# ============================================================
# Routes
# ============================================================

# --- Main page: user list (lab4) ---
@app.route('/')
def index():
    db = get_db()
    users = db.execute('''
        SELECT users.*, roles.name as role_name
        FROM users LEFT JOIN roles ON users.role_id = roles.id
        ORDER BY users.id
    ''').fetchall()
    return render_template('index.html', users=users)

# --- CRUD: view user ---
@app.route('/users/<int:user_id>/')
def user_view(user_id):
    db = get_db()
    user = db.execute('''
        SELECT users.*, roles.name as role_name
        FROM users LEFT JOIN roles ON users.role_id = roles.id
        WHERE users.id = ?
    ''', (user_id,)).fetchone()
    if not user:
        flash('Пользователь не найден.', 'danger')
        return redirect(url_for('index'))
    return render_template('user_view.html', title='Просмотр пользователя', user=user)

# --- CRUD: create user ---
@app.route('/users/create/', methods=['GET', 'POST'])
@login_required
def user_create():
    db = get_db()
    roles = db.execute('SELECT * FROM roles ORDER BY id').fetchall()

    if request.method == 'POST':
        errors = validate_user_form(request.form, is_edit=False)
        if errors:
            flash('При сохранении данных возникла ошибка. Проверьте правильность введённых данных.', 'danger')
            return render_template('user_create.html', title='Создание пользователя',
                                   roles=roles, errors=errors, form_data=request.form)
        try:
            login_val = request.form['login'].strip()
            # Check uniqueness
            existing = db.execute('SELECT id FROM users WHERE login = ?', (login_val,)).fetchone()
            if existing:
                flash('Пользователь с таким логином уже существует.', 'danger')
                errors['login'] = ['Пользователь с таким логином уже существует.']
                return render_template('user_create.html', title='Создание пользователя',
                                       roles=roles, errors=errors, form_data=request.form)

            password_hash = generate_password_hash(request.form['password'])
            role_id = request.form.get('role_id') or None
            db.execute(
                'INSERT INTO users (login, password_hash, last_name, first_name, middle_name, role_id) VALUES (?, ?, ?, ?, ?, ?)',
                (login_val, password_hash,
                 request.form.get('last_name', '').strip(),
                 request.form['first_name'].strip(),
                 request.form.get('middle_name', '').strip() or None,
                 role_id)
            )
            db.commit()
            flash('Пользователь успешно создан.', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.rollback()
            flash(f'Ошибка при сохранении: {e}', 'danger')
            return render_template('user_create.html', title='Создание пользователя',
                                   roles=roles, errors={}, form_data=request.form)

    return render_template('user_create.html', title='Создание пользователя',
                           roles=roles, errors={}, form_data={})

# --- CRUD: edit user ---
@app.route('/users/<int:user_id>/edit/', methods=['GET', 'POST'])
@login_required
def user_edit(user_id):
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if not user:
        flash('Пользователь не найден.', 'danger')
        return redirect(url_for('index'))

    roles = db.execute('SELECT * FROM roles ORDER BY id').fetchall()

    if request.method == 'POST':
        errors = validate_user_form(request.form, is_edit=True)
        if errors:
            flash('При сохранении данных возникла ошибка. Проверьте правильность введённых данных.', 'danger')
            return render_template('user_edit.html', title='Редактирование пользователя',
                                   user=user, roles=roles, errors=errors, form_data=request.form)
        try:
            role_id = request.form.get('role_id') or None
            db.execute(
                'UPDATE users SET last_name=?, first_name=?, middle_name=?, role_id=? WHERE id=?',
                (request.form.get('last_name', '').strip(),
                 request.form['first_name'].strip(),
                 request.form.get('middle_name', '').strip() or None,
                 role_id, user_id)
            )
            db.commit()
            flash('Данные пользователя успешно обновлены.', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.rollback()
            flash(f'Ошибка при сохранении: {e}', 'danger')
            return render_template('user_edit.html', title='Редактирование пользователя',
                                   user=user, roles=roles, errors={}, form_data=request.form)

    return render_template('user_edit.html', title='Редактирование пользователя',
                           user=user, roles=roles, errors={}, form_data=dict(user))

# --- CRUD: delete user ---
@app.route('/users/<int:user_id>/delete/', methods=['POST'])
@login_required
def user_delete(user_id):
    db = get_db()
    try:
        db.execute('DELETE FROM users WHERE id = ?', (user_id,))
        db.commit()
        flash('Пользователь успешно удалён.', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Ошибка при удалении: {e}', 'danger')
    return redirect(url_for('index'))

# --- Password change ---
@app.route('/change_password/', methods=['GET', 'POST'])
@login_required
def change_password():
    errors = {}
    if request.method == 'POST':
        old_password = request.form.get('old_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not check_password_hash(current_user.password_hash, old_password):
            errors['old_password'] = ['Неверный старый пароль.']

        new_errors = validate_password(new_password)
        if new_errors:
            errors['new_password'] = new_errors

        if new_password != confirm_password:
            errors['confirm_password'] = ['Пароли не совпадают.']

        if not errors:
            db = get_db()
            try:
                db.execute('UPDATE users SET password_hash = ? WHERE id = ?',
                           (generate_password_hash(new_password), current_user.id))
                db.commit()
                flash('Пароль успешно изменён.', 'success')
                return redirect(url_for('index'))
            except Exception as e:
                db.rollback()
                flash(f'Ошибка: {e}', 'danger')
        else:
            flash('При смене пароля возникла ошибка.', 'danger')

    return render_template('change_password.html', title='Изменить пароль', errors=errors)

# --- Auth ---
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('login', '')
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        db = get_db()
        row = db.execute('SELECT * FROM users WHERE login = ?', (username,)).fetchone()
        if row and check_password_hash(row['password_hash'], password):
            login_user(User(row), remember=remember)
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

# --- Lab3: visits ---
@app.route('/visits/')
def visits():
    session['visits'] = session.get('visits', 0) + 1
    return render_template('visits.html', title='Счётчик посещений', count=session['visits'])

# --- Lab3: secret ---
@app.route('/secret/')
@login_required
def secret():
    return render_template('secret.html', title='Секретная страница')

# --- Lab2: request data ---
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
        resp.set_cookie('sample_cookie', 'hello_from_lab4')
    return resp

@app.route('/form/', methods=['GET', 'POST'])
def form():
    form_data = None
    if request.method == 'POST':
        form_data = {
            'login': request.form.get('login', ''),
            'password': request.form.get('password', ''),
        }
    return render_template('form.html', title='Параметры формы', form_data=form_data)

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
