import os
import sqlite3
import traceback
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, g, session
from werkzeug.utils import secure_filename
import uuid
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, FileField, PasswordField
from wtforms.validators import DataRequired, Length
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
csrf = CSRFProtect(app)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=100)])
    content = TextAreaField('Content', validators=[DataRequired()])
    excerpt = StringField('Excerpt', validators=[Length(max=200)])
    post_type = SelectField('Type', choices=[('article', 'Article'), ('story', 'Story')], validators=[DataRequired()])
    image = FileField('Image')
    submit = SubmitField('Publish')

class DeleteForm(FlaskForm):
    submit = SubmitField('Delete')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class AdminPostForm(PostForm):
    pass

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.executescript('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                excerpt TEXT,
                image_filename TEXT,
                post_type TEXT NOT NULL DEFAULT 'article',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        
        # Create default admin user if none exists
        admin_exists = db.execute('SELECT COUNT(*) FROM admin_users').fetchone()[0]
        if admin_exists == 0:
            admin_password_hash = generate_password_hash('admin123')
            db.execute('INSERT INTO admin_users (username, password_hash) VALUES (?, ?)', 
                      ('admin', admin_password_hash))
        
        db.commit()

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Admin access required.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def is_admin_logged_in():
    return session.get('admin_logged_in', False)

@app.route('/')
def index():
    db = get_db()
    
    # Get featured post
    featured_post = db.execute('''
        SELECT * FROM posts 
        WHERE featured = 1 
        LIMIT 1
    ''').fetchone()
    
    # Get regular posts (excluding featured post if it exists)
    if featured_post:
        posts = db.execute('''
            SELECT * FROM posts 
            WHERE featured = 0
            ORDER BY created_at DESC 
            LIMIT 9
        ''').fetchall()
    else:
        posts = db.execute('''
            SELECT * FROM posts 
            ORDER BY created_at DESC 
            LIMIT 10
        ''').fetchall()
    
    return render_template('index.html', posts=posts, featured_post=featured_post)

@app.route('/stories')
def stories():
    db = get_db()
    stories = db.execute('''
        SELECT * FROM posts 
        WHERE post_type = 'story'
        ORDER BY created_at DESC
    ''').fetchall()
    return render_template('stories.html', stories=stories)

@app.route('/articles')
def articles():
    db = get_db()
    articles = db.execute('''
        SELECT * FROM posts 
        WHERE post_type = 'article'
        ORDER BY created_at DESC
    ''').fetchall()
    return render_template('articles.html', articles=articles)

@app.route('/post/<int:post_id>')
def view_post(post_id):
    db = get_db()
    post = db.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    if post is None:
        flash('Post not found.', 'error')
        return redirect(url_for('index'))
    form = DeleteForm()
    return render_template('post.html', post=post, form=form)

@app.route('/create', methods=['GET', 'POST'])
@admin_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        excerpt = form.excerpt.data
        post_type = form.post_type.data
        
        # Handle file upload
        image_filename = None
        if form.image.data:
            file = form.image.data
            if allowed_file(file.filename):
                # Generate unique filename
                filename = secure_filename(str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower())
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename
        
        db = get_db()
        db.execute('''
            INSERT INTO posts (title, content, excerpt, image_filename, post_type)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, content, excerpt, image_filename, post_type))
        db.commit()
        flash('Post created successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('create.html', form=form)

@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@admin_required
def edit_post(post_id):
    db = get_db()
    post = db.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    
    if post is None:
        flash('Post not found.', 'error')
        return redirect(url_for('index'))
    
    form = PostForm()
    
    # Pre-populate form with existing data on GET request
    if request.method == 'GET':
        form.title.data = post['title']
        form.content.data = post['content']
        form.excerpt.data = post['excerpt']
        form.post_type.data = post['post_type']

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        excerpt = form.excerpt.data
        post_type = form.post_type.data
        
        image_filename = post['image_filename']
        if form.image.data:
            file = form.image.data
            if allowed_file(file.filename):
                if image_filename:
                    old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                
                filename = secure_filename(str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower())
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename
        
        db.execute('''
            UPDATE posts
            SET title = ?, content = ?, excerpt = ?, image_filename = ?, post_type = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (title, content, excerpt, image_filename, post_type, post_id))
        db.commit()
        flash('Post updated successfully!', 'success')
        return redirect(url_for('view_post', post_id=post_id))
    
    return render_template('edit.html', form=form, post=post)

@app.route('/delete/<int:post_id>', methods=['POST'])
@admin_required
def delete_post(post_id):
    form = DeleteForm()
    if form.validate_on_submit():
        db = get_db()
        post = db.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
        
        if post:
            # Delete associated image file
            if post['image_filename']:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], post['image_filename'])
                if os.path.exists(file_path):
                    os.remove(file_path)

            db.execute('DELETE FROM posts WHERE id = ?', (post_id,))
            db.commit()
            flash('Post deleted successfully!', 'success')
        else:
            flash('Post not found.', 'error')
    else:
        flash('Invalid request.', 'error')
    
    return redirect(url_for('index'))

# Admin Routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    form = LoginForm()
    if form.validate_on_submit():
        db = get_db()
        admin = db.execute('SELECT * FROM admin_users WHERE username = ?', 
                          (form.username.data,)).fetchone()
        
        if admin and check_password_hash(admin['password_hash'], form.password.data):
            session['admin_logged_in'] = True
            session['admin_username'] = admin['username']
            flash('Successfully logged in as admin.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('admin/login.html', form=form)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    db = get_db()
    posts = db.execute('''
        SELECT * FROM posts 
        ORDER BY created_at DESC
    ''').fetchall()
    
    stats = {
        'total_posts': len(posts),
        'total_stories': len([p for p in posts if p['post_type'] == 'story']),
        'total_articles': len([p for p in posts if p['post_type'] == 'article'])
    }
    
    return render_template('admin/dashboard.html', posts=posts, stats=stats)

@app.route('/admin/posts')
@admin_required
def admin_posts():
    db = get_db()
    posts = db.execute('''
        SELECT * FROM posts 
        ORDER BY created_at DESC
    ''').fetchall()
    return render_template('admin/posts.html', posts=posts)

@app.route('/admin/posts/<int:post_id>/delete', methods=['POST'])
@admin_required
def admin_delete_post(post_id):
    form = DeleteForm()
    if form.validate_on_submit():
        db = get_db()
        post = db.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
        
        if post:
            # Delete associated image file
            if post['image_filename']:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], post['image_filename'])
                if os.path.exists(file_path):
                    os.remove(file_path)

            db.execute('DELETE FROM posts WHERE id = ?', (post_id,))
            db.commit()
            flash('Post deleted successfully!', 'success')
        else:
            flash('Post not found.', 'error')
    
    return redirect(url_for('admin_posts'))

@app.route('/admin/posts/<int:post_id>/feature', methods=['POST'])
@admin_required
def admin_feature_post(post_id):
    db = get_db()
    post = db.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    
    if post:
        # Unfeature all other posts first (only one featured post at a time)
        db.execute('UPDATE posts SET featured = 0')
        # Feature this post
        db.execute('UPDATE posts SET featured = 1 WHERE id = ?', (post_id,))
        db.commit()
        flash('Post featured successfully!', 'success')
    else:
        flash('Post not found.', 'error')
    
    return redirect(url_for('admin_posts'))

@app.route('/admin/posts/<int:post_id>/unfeature', methods=['POST'])
@admin_required
def admin_unfeature_post(post_id):
    db = get_db()
    post = db.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    
    if post:
        db.execute('UPDATE posts SET featured = 0 WHERE id = ?', (post_id,))
        db.commit()
        flash('Post unfeatured successfully!', 'success')
    else:
        flash('Post not found.', 'error')
    
    return redirect(url_for('admin_posts'))

# Add admin context to all templates
@app.context_processor
def inject_admin_status():
    return {'is_admin_logged_in': is_admin_logged_in()}

if __name__ == '__main__':
    init_db()
    app.run(debug=True)