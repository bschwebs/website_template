import sqlite3
from flask import Flask, render_template, g
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import SubmitField

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-key'
csrf = CSRFProtect(app)

class DeleteForm(FlaskForm):
    submit = SubmitField('Delete')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('content.db')
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def home():
    return "Fresh test app works"

@app.route('/post/<int:post_id>')
def view_post(post_id):
    db = get_db()
    post = db.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    if post is None:
        return "Post not found", 404
    form = DeleteForm()
    return render_template('post_simple.html', post=post, form=form)

if __name__ == '__main__':
    app.run(debug=True, port=5002)