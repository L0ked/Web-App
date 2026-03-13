import csv
import io
from flask import Blueprint, render_template, request, redirect, url_for, flash, g, Response
from flask_login import current_user, login_required

logs_bp = Blueprint('logs', __name__, url_prefix='/logs', template_folder='templates')

RECORDS_PER_PAGE = 10

def get_db():
    return g.db

def check_logs_access(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Для доступа к данной странице необходимо пройти процедуру аутентификации.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated

@logs_bp.route('/')
@check_logs_access
def log_index():
    db = get_db()
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * RECORDS_PER_PAGE

    # Admin sees all, user sees only own
    if current_user.is_admin:
        total = db.execute('SELECT COUNT(*) FROM visit_logs').fetchone()[0]
        logs = db.execute('''
            SELECT visit_logs.*, users.last_name, users.first_name, users.middle_name
            FROM visit_logs
            LEFT JOIN users ON visit_logs.user_id = users.id
            ORDER BY visit_logs.created_at DESC
            LIMIT ? OFFSET ?
        ''', (RECORDS_PER_PAGE, offset)).fetchall()
    else:
        total = db.execute('SELECT COUNT(*) FROM visit_logs WHERE user_id = ?', (current_user.id,)).fetchone()[0]
        logs = db.execute('''
            SELECT visit_logs.*, users.last_name, users.first_name, users.middle_name
            FROM visit_logs
            LEFT JOIN users ON visit_logs.user_id = users.id
            WHERE visit_logs.user_id = ?
            ORDER BY visit_logs.created_at DESC
            LIMIT ? OFFSET ?
        ''', (current_user.id, RECORDS_PER_PAGE, offset)).fetchall()

    total_pages = (total + RECORDS_PER_PAGE - 1) // RECORDS_PER_PAGE

    return render_template('logs/index.html', title='Журнал посещений',
                           logs=logs, page=page, total_pages=total_pages, offset=offset)

@logs_bp.route('/by_pages/')
@check_logs_access
def report_by_pages():
    db = get_db()
    if current_user.is_admin:
        rows = db.execute('''
            SELECT path, COUNT(*) as cnt
            FROM visit_logs
            GROUP BY path
            ORDER BY cnt DESC
        ''').fetchall()
    else:
        rows = db.execute('''
            SELECT path, COUNT(*) as cnt
            FROM visit_logs
            WHERE user_id = ?
            GROUP BY path
            ORDER BY cnt DESC
        ''', (current_user.id,)).fetchall()
    return render_template('logs/by_pages.html', title='Отчёт по страницам', rows=rows)

@logs_bp.route('/by_pages/csv/')
@check_logs_access
def report_by_pages_csv():
    db = get_db()
    if current_user.is_admin:
        rows = db.execute('''
            SELECT path, COUNT(*) as cnt
            FROM visit_logs GROUP BY path ORDER BY cnt DESC
        ''').fetchall()
    else:
        rows = db.execute('''
            SELECT path, COUNT(*) as cnt
            FROM visit_logs WHERE user_id = ? GROUP BY path ORDER BY cnt DESC
        ''', (current_user.id,)).fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['№', 'Страница', 'Количество посещений'])
    for i, row in enumerate(rows, 1):
        writer.writerow([i, row['path'], row['cnt']])

    resp = Response(output.getvalue(), mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment;filename=report_pages.csv'})
    return resp

@logs_bp.route('/by_users/')
@check_logs_access
def report_by_users():
    db = get_db()
    if current_user.is_admin:
        rows = db.execute('''
            SELECT users.last_name, users.first_name, users.middle_name,
                   visit_logs.user_id, COUNT(*) as cnt
            FROM visit_logs
            LEFT JOIN users ON visit_logs.user_id = users.id
            GROUP BY visit_logs.user_id
            ORDER BY cnt DESC
        ''').fetchall()
    else:
        rows = db.execute('''
            SELECT users.last_name, users.first_name, users.middle_name,
                   visit_logs.user_id, COUNT(*) as cnt
            FROM visit_logs
            LEFT JOIN users ON visit_logs.user_id = users.id
            WHERE visit_logs.user_id = ?
            GROUP BY visit_logs.user_id
            ORDER BY cnt DESC
        ''', (current_user.id,)).fetchall()
    return render_template('logs/by_users.html', title='Отчёт по пользователям', rows=rows)

@logs_bp.route('/by_users/csv/')
@check_logs_access
def report_by_users_csv():
    db = get_db()
    if current_user.is_admin:
        rows = db.execute('''
            SELECT users.last_name, users.first_name, users.middle_name,
                   visit_logs.user_id, COUNT(*) as cnt
            FROM visit_logs LEFT JOIN users ON visit_logs.user_id = users.id
            GROUP BY visit_logs.user_id ORDER BY cnt DESC
        ''').fetchall()
    else:
        rows = db.execute('''
            SELECT users.last_name, users.first_name, users.middle_name,
                   visit_logs.user_id, COUNT(*) as cnt
            FROM visit_logs LEFT JOIN users ON visit_logs.user_id = users.id
            WHERE visit_logs.user_id = ?
            GROUP BY visit_logs.user_id ORDER BY cnt DESC
        ''', (current_user.id,)).fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['№', 'Пользователь', 'Количество посещений'])
    for i, row in enumerate(rows, 1):
        if row['user_id']:
            name = ' '.join(p for p in [row['last_name'], row['first_name'], row['middle_name']] if p)
        else:
            name = 'Неаутентифицированный пользователь'
        writer.writerow([i, name, row['cnt']])

    resp = Response(output.getvalue(), mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment;filename=report_users.csv'})
    return resp
