from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Home works"

@app.route('/post/<int:post_id>')
def test_post(post_id):
    return f"Post {post_id} works"

if __name__ == '__main__':
    app.run(debug=True, port=5001)