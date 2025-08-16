import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, g
from werkzeug.utils import secure_filename
import uuid
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, FileField
from wtforms.validators import DataRequired, Length
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
        ''')
        db.commit()

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    db = get_db()
    posts = db.execute('''
        SELECT * FROM posts 
        ORDER BY created_at DESC 
        LIMIT 10
    ''').fetchall()
    return render_template('index.html', posts=posts)

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
def edit_post(post_id):
    db = get_db()
    post = db.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    
    if post is None:
        flash('Post not found.', 'error')
        return redirect(url_for('index'))
    
    form = PostForm(obj=post)

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

if __name__ == '__main__':
    init_db()
    app.run(debug=app.config['DEBUG'])