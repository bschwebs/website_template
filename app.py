import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, g
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fdsgs65433546hggfh!'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

DATABASE = 'content.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
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
    return render_template('post.html', post=post)

@app.route('/create', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        excerpt = request.form['excerpt']
        post_type = request.form['post_type']
        
        # Handle file upload
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                # Generate unique filename
                filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename
        
        if title and content:
            db = get_db()
            db.execute('''
                INSERT INTO posts (title, content, excerpt, image_filename, post_type)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, content, excerpt, image_filename, post_type))
            db.commit()
            flash('Post created successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Title and content are required.', 'error')
    
    return render_template('create.html')

@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    db = get_db()
    post = db.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    
    if post is None:
        flash('Post not found.', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        excerpt = request.form['excerpt']
        post_type = request.form['post_type']
        
        # Handle file upload
        image_filename = post['image_filename']  # Keep existing image by default
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                # Delete old image if it exists
                if image_filename:
                    old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                
                # Save new image
                filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename
        
        if title and content:
            db.execute('''
                UPDATE posts 
                SET title = ?, content = ?, excerpt = ?, image_filename = ?, post_type = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (title, content, excerpt, image_filename, post_type, post_id))
            db.commit()
            flash('Post updated successfully!', 'success')
            return redirect(url_for('view_post', post_id=post_id))
        else:
            flash('Title and content are required.', 'error')
    
    return render_template('edit.html', post=post)

@app.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
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
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)