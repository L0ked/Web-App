import os
import uuid
import hashlib
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from models import db, Course, Category, Image, Review

bp = Blueprint('courses', __name__, url_prefix='/courses')

RATING_OPTIONS = [
    (5, 'отлично'),
    (4, 'хорошо'),
    (3, 'удовлетворительно'),
    (2, 'неудовлетворительно'),
    (1, 'плохо'),
    (0, 'ужасно'),
]

@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    courses = db.paginate(
        db.select(Course).order_by(Course.created_at.desc()),
        page=page, per_page=9
    )
    return render_template('courses/index.html', title='Курсы', courses=courses)

@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    categories = db.session.execute(db.select(Category)).scalars().all()
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            short_desc = request.form.get('short_desc', '').strip()
            full_desc = request.form.get('full_desc', '').strip()
            category_id = request.form.get('category_id') or None

            course = Course(
                name=name,
                short_desc=short_desc,
                full_desc=full_desc,
                category_id=category_id,
                author_id=current_user.id,
            )

            # Handle image upload
            f = request.files.get('background_image')
            if f and f.filename:
                img = _save_image(f)
                db.session.add(img)
                course.background_image_id = img.id

            db.session.add(course)
            db.session.commit()
            flash('Курс успешно создан.', 'success')
            return redirect(url_for('courses.show', course_id=course.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при создании курса: {e}', 'danger')
    return render_template('courses/new.html', title='Новый курс', categories=categories)

def _save_image(f):
    """Save uploaded image file and return Image model instance."""
    data = f.read()
    md5_hash = hashlib.md5(data).hexdigest()
    ext = os.path.splitext(f.filename)[1]
    storage_name = f'{uuid.uuid4()}{ext}'
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.join(upload_folder, storage_name)
    with open(filepath, 'wb') as out:
        out.write(data)
    img = Image(
        id=str(uuid.uuid4()),
        file_name=f.filename,
        mime_type=f.content_type or 'image/jpeg',
        md5_hash=md5_hash,
        storage_filename=storage_name,
    )
    return img

@bp.route('/<int:course_id>')
def show(course_id):
    course = db.get_or_404(Course, course_id)
    # Last 5 reviews
    recent_reviews = db.session.execute(
        db.select(Review).filter_by(course_id=course_id)
        .order_by(Review.created_at.desc()).limit(5)
    ).scalars().all()

    # Check if current user already left a review
    user_review = None
    if current_user.is_authenticated:
        user_review = db.session.execute(
            db.select(Review).filter_by(course_id=course_id, user_id=current_user.id)
        ).scalar()

    return render_template('courses/show.html', title=course.name, course=course,
                           recent_reviews=recent_reviews, user_review=user_review,
                           rating_options=RATING_OPTIONS)

@bp.route('/<int:course_id>/reviews')
def reviews(course_id):
    course = db.get_or_404(Course, course_id)

    sort = request.args.get('sort', 'newest')
    page = request.args.get('page', 1, type=int)

    query = db.select(Review).filter_by(course_id=course_id)
    if sort == 'positive':
        query = query.order_by(Review.rating.desc(), Review.created_at.desc())
    elif sort == 'negative':
        query = query.order_by(Review.rating.asc(), Review.created_at.desc())
    else:
        query = query.order_by(Review.created_at.desc())

    reviews_page = db.paginate(query, page=page, per_page=5)

    user_review = None
    if current_user.is_authenticated:
        user_review = db.session.execute(
            db.select(Review).filter_by(course_id=course_id, user_id=current_user.id)
        ).scalar()

    return render_template('courses/reviews.html', title=f'Отзывы — {course.name}',
                           course=course, reviews=reviews_page, sort=sort,
                           user_review=user_review, rating_options=RATING_OPTIONS)

@bp.route('/<int:course_id>/reviews/create', methods=['POST'])
@login_required
def create_review(course_id):
    course = db.get_or_404(Course, course_id)

    # Check if already reviewed
    existing = db.session.execute(
        db.select(Review).filter_by(course_id=course_id, user_id=current_user.id)
    ).scalar()
    if existing:
        flash('Вы уже оставили отзыв к этому курсу.', 'warning')
        return redirect(url_for('courses.show', course_id=course_id))

    try:
        rating = int(request.form.get('rating', 5))
        text = request.form.get('text', '').strip()
        if not text:
            flash('Текст отзыва не может быть пустым.', 'danger')
            return redirect(url_for('courses.show', course_id=course_id))

        review = Review(
            rating=rating,
            text=text,
            course_id=course_id,
            user_id=current_user.id,
        )
        db.session.add(review)

        # Update course rating
        course.rating_sum += rating
        course.rating_num += 1

        db.session.commit()
        flash('Отзыв успешно добавлен.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при сохранении отзыва: {e}', 'danger')

    return redirect(url_for('courses.show', course_id=course_id))
