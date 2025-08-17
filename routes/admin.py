"""
Admin routes for the Story Hub application.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import PostModel, AdminModel, TagModel, CategoryModel, EmailConfigModel, ContactModel
from forms import DeleteForm, CategoryForm, DeleteCategoryForm, ChangePasswordForm
from utils import admin_required, delete_file

admin = Blueprint('admin', __name__)


@admin.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard."""
    posts = PostModel.get_all_posts()
    stats = AdminModel.get_post_statistics()
    return render_template('admin/dashboard.html', posts=posts, stats=stats)


@admin.route('/admin/posts')
@admin_required
def admin_posts():
    """Admin posts management."""
    posts = PostModel.get_all_posts()
    return render_template('admin/posts.html', posts=posts)


@admin.route('/admin/posts/<int:post_id>/delete', methods=['POST'])
@admin_required
def admin_delete_post(post_id):
    """Delete a post from admin interface."""
    form = DeleteForm()
    if form.validate_on_submit():
        post = PostModel.get_post_by_id(post_id)
        
        if post:
            # Delete associated image file
            delete_file(post['image_filename'])
            # Delete the post
            PostModel.delete_post(post_id)
            flash('Post deleted successfully!', 'success')
        else:
            flash('Post not found.', 'error')
    
    return redirect(url_for('admin.admin_posts'))


@admin.route('/admin/posts/<int:post_id>/feature', methods=['POST'])
@admin_required
def admin_feature_post(post_id):
    """Feature a post."""
    post = PostModel.get_post_by_id(post_id)
    
    if post:
        PostModel.feature_post(post_id)
        flash('Post featured successfully!', 'success')
    else:
        flash('Post not found.', 'error')
    
    return redirect(url_for('admin.admin_posts'))


@admin.route('/admin/posts/<int:post_id>/unfeature', methods=['POST'])
@admin_required
def admin_unfeature_post(post_id):
    """Unfeature a post."""
    post = PostModel.get_post_by_id(post_id)
    
    if post:
        PostModel.unfeature_post(post_id)
        flash('Post unfeatured successfully!', 'success')
    else:
        flash('Post not found.', 'error')
    
    return redirect(url_for('admin.admin_posts'))


@admin.route('/admin/tags')
@admin_required
def admin_tags():
    """Admin tags management."""
    tags = TagModel.get_all_tags()
    return render_template('admin/tags.html', tags=tags)


@admin.route('/admin/tags/<int:tag_id>/delete', methods=['POST'])
@admin_required
def admin_delete_tag(tag_id):
    """Delete a tag from admin interface."""
    form = DeleteForm()
    if form.validate_on_submit():
        tag = TagModel.get_tag_by_id(tag_id)
        
        if tag:
            # Delete the tag and its associations
            TagModel.delete_tag(tag_id)
            flash('Tag deleted successfully!', 'success')
        else:
            flash('Tag not found.', 'error')
    
    return redirect(url_for('admin.admin_tags'))


@admin.route('/admin/categories')
@admin_required
def admin_categories():
    """Admin categories management."""
    categories = CategoryModel.get_all_categories()
    return render_template('admin/categories.html', categories=categories)


@admin.route('/admin/categories/new', methods=['GET', 'POST'])
@admin_required
def admin_create_category():
    """Create a new category."""
    form = CategoryForm()
    
    if form.validate_on_submit():
        # Check if slug already exists
        if CategoryModel.slug_exists(form.slug.data):
            flash('Category slug already exists. Please choose a different slug.', 'error')
        else:
            CategoryModel.create_category(
                name=form.name.data,
                slug=form.slug.data,
                description=form.description.data
            )
            flash('Category created successfully!', 'success')
            return redirect(url_for('admin.admin_categories'))
    
    return render_template('admin/category_form.html', form=form, title='Create Category')


@admin.route('/admin/categories/<int:category_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_category(category_id):
    """Edit an existing category."""
    category = CategoryModel.get_category_by_id(category_id)
    if not category:
        flash('Category not found.', 'error')
        return redirect(url_for('admin.admin_categories'))
    
    form = CategoryForm()
    
    if form.validate_on_submit():
        # Check if slug already exists (excluding current category)
        if CategoryModel.slug_exists(form.slug.data, category_id):
            flash('Category slug already exists. Please choose a different slug.', 'error')
        else:
            CategoryModel.update_category(
                category_id=category_id,
                name=form.name.data,
                slug=form.slug.data,
                description=form.description.data
            )
            flash('Category updated successfully!', 'success')
            return redirect(url_for('admin.admin_categories'))
    
    # Pre-populate form with existing data
    if request.method == 'GET':
        form.name.data = category['name']
        form.slug.data = category['slug']
        form.description.data = category['description']
    
    return render_template('admin/category_form.html', form=form, title='Edit Category', category=category)


@admin.route('/admin/categories/<int:category_id>/delete', methods=['POST'])
@admin_required
def admin_delete_category(category_id):
    """Delete a category from admin interface."""
    form = DeleteCategoryForm()
    if form.validate_on_submit():
        category = CategoryModel.get_category_by_id(category_id)
        
        if category:
            # Delete the category (posts will be unlinked automatically)
            CategoryModel.delete_category(category_id)
            flash('Category deleted successfully! Associated posts have been unlinked.', 'success')
        else:
            flash('Category not found.', 'error')
    
    return redirect(url_for('admin.admin_categories'))


@admin.route('/admin/email-config', methods=['GET', 'POST'])
@admin_required
def admin_email_config():
    """Email server configuration."""
    if request.method == 'POST':
        smtp_server = request.form.get('smtp_server', '').strip()
        smtp_port = request.form.get('smtp_port', 587, type=int)
        smtp_username = request.form.get('smtp_username', '').strip()
        smtp_password = request.form.get('smtp_password', '').strip()
        from_email = request.form.get('from_email', '').strip()
        to_email = request.form.get('to_email', '').strip()
        use_tls = bool(request.form.get('use_tls'))
        
        # Validate required fields
        if not all([smtp_server, smtp_username, smtp_password, from_email, to_email]):
            flash('All fields are required.', 'error')
        else:
            try:
                EmailConfigModel.save_config(
                    smtp_server=smtp_server,
                    smtp_port=smtp_port,
                    smtp_username=smtp_username,
                    smtp_password=smtp_password,
                    from_email=from_email,
                    to_email=to_email,
                    use_tls=use_tls
                )
                flash('Email configuration saved successfully!', 'success')
                return redirect(url_for('admin.admin_email_config'))
            except Exception as e:
                flash('Error saving email configuration.', 'error')
    
    # Get current configuration
    config = EmailConfigModel.get_config()
    return render_template('admin/email_config.html', config=config)


@admin.route('/admin/contact-messages')
@admin_required
def admin_contact_messages():
    """View contact messages."""
    messages = ContactModel.get_all_messages()
    delete_form = DeleteForm()
    return render_template('admin/contact_messages.html', messages=messages, delete_form=delete_form)


@admin.route('/admin/contact-messages/<int:message_id>/delete', methods=['POST'])
@admin_required
def admin_delete_contact_message(message_id):
    """Delete a contact message."""
    form = DeleteForm()
    if form.validate_on_submit():
        try:
            ContactModel.delete_message(message_id)
            flash('Contact message deleted successfully!', 'success')
        except Exception as e:
            flash('Error deleting contact message.', 'error')
    
    return redirect(url_for('admin.admin_contact_messages'))


@admin.route('/admin/change-password', methods=['GET', 'POST'])
@admin_required
def admin_change_password():
    """Change admin password."""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        current_username = session.get('admin_username')
        
        # Verify current password
        if AdminModel.verify_password(current_username, form.current_password.data):
            # Update password
            AdminModel.update_password(current_username, form.new_password.data)
            flash('Password changed successfully!', 'success')
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash('Current password is incorrect.', 'error')
    
    return render_template('admin/change_password.html', form=form)