"""
Flask-WTF forms for the Story Hub application.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, FileField, PasswordField, ValidationError, DateTimeLocalField, RadioField, HiddenField, MultipleFileField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Length, Email, Optional, URL
from wtforms.widgets import TextArea
from markupsafe import Markup
import html


class RichTextAreaField(TextAreaField):
    """Text area field that will be enhanced with Quill.js on the frontend."""
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('render_kw', {})
        kwargs['render_kw']['class'] = 'form-control quill-target'
        kwargs['render_kw']['style'] = 'display: none;'  # Hide the textarea, Quill will replace it
        super().__init__(*args, **kwargs)


class PostForm(FlaskForm):
    """Form for creating and editing posts."""
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=100)])
    content = RichTextAreaField('Content', validators=[DataRequired()])
    excerpt = StringField('Excerpt', validators=[Length(max=200)])
    category_id = SelectField('Category', choices=[], coerce=lambda x: int(x) if x and x != '' else None)
    tags = StringField('Tags', validators=[Length(max=500)], render_kw={"placeholder": "Enter tags separated by commas (e.g., technology, web development, python)"})
    template_id = SelectField('Template', choices=[], coerce=lambda x: int(x) if x and str(x).strip() and x != 'None' else None, validators=[Optional()])
    status = RadioField('Status', choices=[('draft', 'Save as Draft'), ('published', 'Publish Now')], default='published')
    publish_date = DateTimeLocalField('Publish Date', validators=[Optional()], 
                                    render_kw={"placeholder": "Leave empty to publish immediately"})
    
    # SEO Fields
    meta_description = TextAreaField('Meta Description', validators=[Length(max=160)], 
                                   render_kw={"placeholder": "Brief description for search engines (160 chars max)", "rows": "3"})
    meta_keywords = StringField('Meta Keywords', validators=[Length(max=255)], 
                              render_kw={"placeholder": "SEO keywords separated by commas"})
    canonical_url = StringField('Canonical URL', validators=[Optional(), URL()], 
                              render_kw={"placeholder": "Optional: canonical URL for this post"})
    
    image = FileField('Featured Image')
    image_position_x = SelectField('Image Horizontal Position', 
                                 choices=[('left', 'Left'), ('center', 'Center'), ('right', 'Right')], 
                                 default='center')
    image_position_y = SelectField('Image Vertical Position', 
                                 choices=[('top', 'Top'), ('center', 'Center'), ('bottom', 'Bottom')], 
                                 default='center')
    submit = SubmitField('Save Post')
    preview = SubmitField('Preview', render_kw={"formtarget": "_blank"})


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


class PostTemplateForm(FlaskForm):
    """Form for creating and editing post templates."""
    name = StringField('Template Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = StringField('Description', validators=[Optional(), Length(max=200)])
    content_template = RichTextAreaField('Template Content', validators=[DataRequired()])
    submit = SubmitField('Save Template')


class ImageGalleryForm(FlaskForm):
    """Form for uploading images to gallery."""
    images = MultipleFileField('Select Images', validators=[DataRequired()])
    submit = SubmitField('Upload Images')


class ImageEditForm(FlaskForm):
    """Form for editing image metadata."""
    alt_text = StringField('Alt Text', validators=[Optional(), Length(max=200)])
    caption = StringField('Caption', validators=[Optional(), Length(max=300)])
    submit = SubmitField('Update Image')


class ImageSearchForm(FlaskForm):
    """Form for searching images in gallery."""
    query = StringField('Search Images', validators=[Length(max=200)], 
                       render_kw={"placeholder": "Search by filename, alt text, or caption..."})
    submit = SubmitField('Search')


class BulkDeleteForm(FlaskForm):
    """Form for bulk deletion operations (CSRF protection)."""
    selected_items = HiddenField('Selected Items', validators=[DataRequired()])
    submit = SubmitField('Delete Selected')


class SocialLinkForm(FlaskForm):
    """Form for creating and editing social media links."""
    name = StringField('Name', validators=[DataRequired(), Length(max=100)], 
                      render_kw={"placeholder": "e.g., Twitter, Facebook"})
    url = StringField('URL', validators=[DataRequired(), URL(), Length(max=500)], 
                     render_kw={"placeholder": "https://twitter.com/yourusername"})
    icon_class = StringField('Icon Class', validators=[DataRequired(), Length(max=100)], 
                            render_kw={"placeholder": "fab fa-twitter"})
    display_order = IntegerField('Display Order', validators=[Optional()], default=0)
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Social Link')


class DeleteSocialLinkForm(FlaskForm):
    """Form for deleting social media links (CSRF protection)."""
    submit = SubmitField('Delete')


class QuoteForm(FlaskForm):
    """Form for creating and editing quotes."""
    text = TextAreaField('Quote Text', validators=[DataRequired(), Length(min=10, max=500)],
                        render_kw={"placeholder": "Enter the quote text here...", "rows": 4})
    author = StringField('Author', validators=[DataRequired(), Length(min=2, max=100)],
                        render_kw={"placeholder": "Author name"})
    source = StringField('Source', validators=[Length(max=200)],
                        render_kw={"placeholder": "Book, speech, etc. (optional)"})
    language = SelectField('Language', choices=[('en', 'English'), ('ja', 'Japanese')], default='en')
    display_order = IntegerField('Display Order', validators=[Optional()], default=0,
                               render_kw={"placeholder": "0 for automatic ordering"})
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Quote')


class DeleteQuoteForm(FlaskForm):
    """Form for deleting quotes (CSRF protection)."""
    submit = SubmitField('Delete')