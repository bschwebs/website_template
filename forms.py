"""
Flask-WTF forms for the Story Hub application.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, FileField, PasswordField, ValidationError
from wtforms.validators import DataRequired, Length, Email, Optional, URL


class PostForm(FlaskForm):
    """Form for creating and editing posts."""
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=100)])
    content = TextAreaField('Content', validators=[DataRequired()])
    excerpt = StringField('Excerpt', validators=[Length(max=200)])
    post_type = SelectField('Type', choices=[('article', 'Article'), ('story', 'Story')], validators=[DataRequired()])
    category_id = SelectField('Category', choices=[], coerce=lambda x: int(x) if x else None, render_kw={"data-post-type": "article"})
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


class CategoryForm(FlaskForm):
    """Form for creating and editing categories."""
    name = StringField('Category Name', validators=[DataRequired(), Length(min=2, max=50)])
    slug = StringField('URL Slug', validators=[DataRequired(), Length(min=2, max=50)])
    description = TextAreaField('Description', validators=[Length(max=200)])
    submit = SubmitField('Save Category')


class DeleteCategoryForm(FlaskForm):
    """Form for category deletion (CSRF protection)."""
    submit = SubmitField('Delete Category')


class ContactForm(FlaskForm):
    """Form for contact page."""
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    subject = StringField('Subject', validators=[DataRequired(), Length(min=2, max=200)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=2000)])
    submit = SubmitField('Send Message')


class ChangePasswordForm(FlaskForm):
    """Form for changing admin password."""
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6, max=100)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), Length(min=6, max=100)])
    submit = SubmitField('Change Password')
    
    def validate_confirm_password(self, field):
        if field.data != self.new_password.data:
            raise ValidationError('Passwords must match.')


class AboutForm(FlaskForm):
    """Form for managing about page information."""
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=100)])
    bio = TextAreaField('Bio', validators=[Optional(), Length(max=2000)])
    image = FileField('Profile Image')
    website_url = StringField('Website URL', validators=[Optional(), URL(), Length(max=200)])
    github_url = StringField('GitHub URL', validators=[Optional(), URL(), Length(max=200)])
    linkedin_url = StringField('LinkedIn URL', validators=[Optional(), URL(), Length(max=200)])
    twitter_url = StringField('Twitter URL', validators=[Optional(), URL(), Length(max=200)])
    submit = SubmitField('Save About Info')