"""
Flask-WTF forms for the Story Hub application.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, FileField, PasswordField
from wtforms.validators import DataRequired, Length


class PostForm(FlaskForm):
    """Form for creating and editing posts."""
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=100)])
    content = TextAreaField('Content', validators=[DataRequired()])
    excerpt = StringField('Excerpt', validators=[Length(max=200)])
    post_type = SelectField('Type', choices=[('article', 'Article'), ('story', 'Story')], validators=[DataRequired()])
    tags = StringField('Tags', validators=[Length(max=500)], render_kw={"placeholder": "Enter tags separated by commas (e.g., technology, web development, python)"})
    image = FileField('Image')
    image_position_x = SelectField('Image Horizontal Position', 
                                 choices=[('left', 'Left'), ('center', 'Center'), ('right', 'Right')], 
                                 default='center')
    image_position_y = SelectField('Image Vertical Position', 
                                 choices=[('top', 'Top'), ('center', 'Center'), ('bottom', 'Bottom')], 
                                 default='center')
    submit = SubmitField('Publish')


class DeleteForm(FlaskForm):
    """Form for post deletion (CSRF protection)."""
    submit = SubmitField('Delete')


class LoginForm(FlaskForm):
    """Form for admin login."""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class SearchForm(FlaskForm):
    """Form for searching posts."""
    query = StringField('Search', validators=[Length(max=200)], render_kw={"placeholder": "Search posts..."})
    submit = SubmitField('Search')


class AdminPostForm(PostForm):
    """Admin version of the post form (inherits from PostForm)."""
    pass