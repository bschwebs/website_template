"""
Admin routes for the Story Hub application.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify, send_file, make_response
from models import PostModel, AdminModel, TagModel, CategoryModel, EmailConfigModel, ContactModel, AboutModel, PostTemplateModel, ImageGalleryModel, ActivityLogModel
from forms import DeleteForm, CategoryForm, DeleteCategoryForm, ChangePasswordForm, AboutForm, PostTemplateForm, ImageGalleryForm, ImageEditForm, ImageSearchForm, BulkDeleteForm
from utils import admin_required, delete_file, save_uploaded_file
import os
import json
import zipfile
import tempfile
from datetime import datetime
from PIL import Image

admin = Blueprint('admin', __name__)


@admin.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard."""
    posts = PostModel.get_articles_paginated(page=1, per_page=20)  # Get recent posts with category info
    stats = AdminModel.get_post_statistics()
    categories = CategoryModel.get_all_categories()
    return render_template('admin/dashboard.html', posts=posts, stats=stats, categories=categories)


@admin.route('/admin/posts')
@admin_required
def admin_posts():
    """Admin posts management."""
    posts = PostModel.get_articles_paginated(page=1, per_page=1000)  # Get all posts with category info
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


@admin.route('/admin/posts/bulk-delete', methods=['POST'])
@admin_required
def admin_bulk_delete_posts():
    """Bulk delete multiple posts."""
    form = BulkDeleteForm()
    if form.validate_on_submit():
        try:
            # Parse the selected post IDs from JSON
            import json
            selected_ids = json.loads(form.selected_items.data)
            
            if not selected_ids:
                flash('No posts selected for deletion.', 'error')
                return redirect(url_for('admin.admin_posts'))
            
            deleted_count = 0
            for post_id in selected_ids:
                post = PostModel.get_post_by_id(post_id)
                if post:
                    # Delete associated image file
                    delete_file(post['image_filename'])
                    # Delete the post
                    PostModel.delete_post(post_id)
                    deleted_count += 1
            
            if deleted_count > 0:
                # Log bulk delete activity
                ActivityLogModel.log_activity(
                    admin_username=session.get('admin_username', 'unknown'),
                    action='Bulk Delete Posts',
                    details=f'Deleted {deleted_count} posts in bulk operation',
                    ip_address=request.remote_addr
                )
                flash(f'{deleted_count} post(s) deleted successfully!', 'success')
            else:
                flash('No valid posts found for deletion.', 'error')
        
        except Exception as e:
            flash('Error occurred during bulk deletion.', 'error')
    
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


@admin.route('/admin/tags/bulk-delete', methods=['POST'])
@admin_required
def admin_bulk_delete_tags():
    """Bulk delete multiple tags (only those with no posts)."""
    form = BulkDeleteForm()
    if form.validate_on_submit():
        try:
            # Parse the selected tag IDs from JSON
            import json
            selected_ids = json.loads(form.selected_items.data)
            
            if not selected_ids:
                flash('No tags selected for deletion.', 'error')
                return redirect(url_for('admin.admin_tags'))
            
            deleted_count = 0
            skipped_count = 0
            
            for tag_id in selected_ids:
                tag = TagModel.get_tag_by_id(tag_id)
                if tag:
                    # Only delete tags with no posts
                    if tag.get('post_count', 0) == 0:
                        TagModel.delete_tag(tag_id)
                        deleted_count += 1
                    else:
                        skipped_count += 1
            
            messages = []
            if deleted_count > 0:
                messages.append(f'{deleted_count} tag(s) deleted successfully!')
            if skipped_count > 0:
                messages.append(f'{skipped_count} tag(s) skipped (in use by posts)')
            
            if messages:
                flash(' '.join(messages), 'success' if deleted_count > 0 else 'warning')
            else:
                flash('No valid tags found for deletion.', 'error')
        
        except Exception as e:
            flash('Error occurred during bulk deletion.', 'error')
    
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


@admin.route('/admin/about', methods=['GET', 'POST'])
@admin_required
def admin_about():
    """Manage about page information."""
    form = AboutForm()
    
    if form.validate_on_submit():
        # Handle file upload
        image_filename = None
        if form.image.data and form.image.data.filename:
            try:
                image_filename = save_uploaded_file(form.image.data, current_app.config['UPLOAD_FOLDER'])
                if image_filename:
                    flash(f'Image uploaded successfully: {image_filename}', 'success')
                else:
                    flash('Image upload failed. Please check file format.', 'error')
                    return render_template('admin/about.html', form=form, about_info=AboutModel.get_about_info())
            except Exception as e:
                flash(f'Error uploading image: {str(e)}', 'error')
                return render_template('admin/about.html', form=form, about_info=AboutModel.get_about_info())
        else:
            # Keep existing image if no new image uploaded
            existing_info = AboutModel.get_about_info()
            if existing_info:
                image_filename = existing_info['image_filename']
        
        try:
            AboutModel.update_about_info(
                name=form.name.data,
                email=form.email.data,
                bio=form.bio.data,
                image_filename=image_filename,
                website_url=form.website_url.data,
                github_url=form.github_url.data,
                linkedin_url=form.linkedin_url.data,
                twitter_url=form.twitter_url.data
            )
            flash('About information updated successfully!', 'success')
            return redirect(url_for('admin.admin_about'))
        except Exception as e:
            flash('Error saving about information.', 'error')
    
    # Pre-populate form with existing data
    about_info = AboutModel.get_about_info()
    if about_info and request.method == 'GET':
        form.name.data = about_info['name']
        form.email.data = about_info['email']
        form.bio.data = about_info['bio']
        form.website_url.data = about_info['website_url']
        form.github_url.data = about_info['github_url']
        form.linkedin_url.data = about_info['linkedin_url']
        form.twitter_url.data = about_info['twitter_url']
    
    return render_template('admin/about.html', form=form, about_info=about_info)


# Template Management Routes
@admin.route('/admin/templates')
@admin_required
def admin_templates():
    """Manage post templates."""
    templates = PostTemplateModel.get_all_templates()
    return render_template('admin/templates.html', templates=templates)


@admin.route('/admin/templates/create', methods=['GET', 'POST'])
@admin_required
def admin_create_template():
    """Create a new post template."""
    form = PostTemplateForm()
    
    if form.validate_on_submit():
        try:
            PostTemplateModel.create_template(
                name=form.name.data,
                description=form.description.data,
                content_template=form.content_template.data
            )
            flash('Template created successfully!', 'success')
            return redirect(url_for('admin.admin_templates'))
        except Exception as e:
            flash('Error creating template.', 'error')
    
    return render_template('admin/template_form.html', form=form, title='Create Template')


@admin.route('/admin/templates/<int:template_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_template(template_id):
    """Edit an existing post template."""
    template = PostTemplateModel.get_template_by_id(template_id)
    if not template:
        flash('Template not found.', 'error')
        return redirect(url_for('admin.admin_templates'))
    
    form = PostTemplateForm()
    
    if form.validate_on_submit():
        try:
            PostTemplateModel.update_template(
                template_id=template_id,
                name=form.name.data,
                description=form.description.data,
                content_template=form.content_template.data
            )
            flash('Template updated successfully!', 'success')
            return redirect(url_for('admin.admin_templates'))
        except Exception as e:
            flash('Error updating template.', 'error')
    
    # Pre-populate form
    if request.method == 'GET':
        form.name.data = template['name']
        form.description.data = template['description']
        form.content_template.data = template['content_template']
    
    return render_template('admin/template_form.html', form=form, template=template, title='Edit Template')


@admin.route('/admin/templates/<int:template_id>/delete', methods=['POST'])
@admin_required
def admin_delete_template(template_id):
    """Delete a post template."""
    form = DeleteForm()
    if form.validate_on_submit():
        try:
            PostTemplateModel.delete_template(template_id)
            flash('Template deleted successfully!', 'success')
        except Exception as e:
            flash('Error deleting template.', 'error')
    
    return redirect(url_for('admin.admin_templates'))


# Image Gallery Management Routes
@admin.route('/admin/gallery')
@admin_required
def admin_gallery():
    """Manage image gallery."""
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('query', '')
    search_form = ImageSearchForm()
    
    if search_query:
        images = ImageGalleryModel.search_images(search_query, page=page, per_page=20)
        total_images = len(ImageGalleryModel.search_images(search_query, page=1, per_page=1000))
    else:
        images = ImageGalleryModel.get_all_images(page=page, per_page=20)
        total_images = ImageGalleryModel.count_images()
    
    # Calculate pagination
    per_page = 20
    total_pages = (total_images + per_page - 1) // per_page
    
    return render_template('admin/gallery.html', 
                         images=images, 
                         page=page, 
                         total_pages=total_pages,
                         search_form=search_form,
                         search_query=search_query)


@admin.route('/admin/gallery/upload', methods=['GET', 'POST'])
@admin_required
def admin_upload_images():
    """Upload multiple images to gallery."""
    form = ImageGalleryForm()
    
    if form.validate_on_submit():
        uploaded_count = 0
        failed_uploads = []
        
        for image_file in form.images.data:
            if image_file and image_file.filename:
                try:
                    # Save the file
                    filename = save_uploaded_file(image_file, current_app.config['UPLOAD_FOLDER'])
                    
                    if filename:
                        # Get image dimensions and file size
                        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                        file_size = os.path.getsize(file_path)
                        
                        try:
                            with Image.open(file_path) as img:
                                width, height = img.size
                        except:
                            width = height = None
                        
                        # Add to gallery database
                        ImageGalleryModel.add_image(
                            filename=filename,
                            original_filename=image_file.filename,
                            file_size=file_size,
                            width=width,
                            height=height
                        )
                        uploaded_count += 1
                    else:
                        failed_uploads.append(image_file.filename)
                        
                except Exception as e:
                    failed_uploads.append(f"{image_file.filename}: {str(e)}")
        
        if uploaded_count > 0:
            flash(f'{uploaded_count} images uploaded successfully!', 'success')
        
        if failed_uploads:
            flash(f'Failed to upload: {", ".join(failed_uploads)}', 'error')
        
        return redirect(url_for('admin.admin_gallery'))
    
    return render_template('admin/upload_images.html', form=form)


@admin.route('/admin/gallery/<int:image_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_image(image_id):
    """Edit image metadata."""
    image = ImageGalleryModel.get_image_by_id(image_id)
    if not image:
        flash('Image not found.', 'error')
        return redirect(url_for('admin.admin_gallery'))
    
    form = ImageEditForm()
    
    if form.validate_on_submit():
        try:
            ImageGalleryModel.update_image(
                image_id=image_id,
                alt_text=form.alt_text.data,
                caption=form.caption.data
            )
            flash('Image updated successfully!', 'success')
            return redirect(url_for('admin.admin_gallery'))
        except Exception as e:
            flash('Error updating image.', 'error')
    
    # Pre-populate form
    if request.method == 'GET':
        form.alt_text.data = image['alt_text']
        form.caption.data = image['caption']
    
    return render_template('admin/edit_image.html', form=form, image=image)


@admin.route('/admin/gallery/<int:image_id>/delete', methods=['POST'])
@admin_required
def admin_delete_image(image_id):
    """Delete an image from gallery."""
    form = DeleteForm()
    if form.validate_on_submit():
        image = ImageGalleryModel.get_image_by_id(image_id)
        if image:
            try:
                # Delete file from filesystem
                delete_file(image['filename'])
                # Delete from database
                ImageGalleryModel.delete_image(image_id)
                flash('Image deleted successfully!', 'success')
            except Exception as e:
                flash('Error deleting image.', 'error')
        else:
            flash('Image not found.', 'error')
    
    return redirect(url_for('admin.admin_gallery'))


@admin.route('/admin/gallery/bulk-delete', methods=['POST'])
@admin_required
def admin_bulk_delete_images():
    """Bulk delete multiple images from gallery."""
    form = BulkDeleteForm()
    if form.validate_on_submit():
        try:
            # Parse the selected image IDs from JSON
            import json
            selected_ids = json.loads(form.selected_items.data)
            
            if not selected_ids:
                flash('No images selected for deletion.', 'error')
                return redirect(url_for('admin.admin_gallery'))
            
            deleted_count = 0
            for image_id in selected_ids:
                image = ImageGalleryModel.get_image_by_id(image_id)
                if image:
                    try:
                        # Delete file from filesystem
                        delete_file(image['filename'])
                        # Delete from database
                        ImageGalleryModel.delete_image(image_id)
                        deleted_count += 1
                    except Exception as e:
                        continue  # Skip failed deletions
            
            if deleted_count > 0:
                # Log bulk delete activity
                ActivityLogModel.log_activity(
                    admin_username=session.get('admin_username', 'unknown'),
                    action='Bulk Delete Images',
                    details=f'Deleted {deleted_count} images from gallery in bulk operation',
                    ip_address=request.remote_addr
                )
                flash(f'{deleted_count} image(s) deleted successfully!', 'success')
            else:
                flash('No valid images found for deletion.', 'error')
        
        except Exception as e:
            flash('Error occurred during bulk deletion.', 'error')
    
    return redirect(url_for('admin.admin_gallery'))


@admin.route('/admin/upload-image-ajax', methods=['POST'])
@admin_required
def upload_image_ajax():
    """AJAX endpoint for TinyMCE image uploads."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        filename = save_uploaded_file(file, current_app.config['UPLOAD_FOLDER'])
        if filename:
            # Add to gallery database
            try:
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file_size = os.path.getsize(file_path)
                
                try:
                    with Image.open(file_path) as img:
                        width, height = img.size
                except:
                    width = height = None
                
                ImageGalleryModel.add_image(
                    filename=filename,
                    original_filename=file.filename,
                    file_size=file_size,
                    width=width,
                    height=height
                )
            except:
                pass  # Don't fail if database operation fails
            
            # Return the URL for TinyMCE
            image_url = url_for('static', filename=f'uploads/{filename}')
            return jsonify({'location': image_url})
        else:
            return jsonify({'error': 'Failed to save file'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Backup and Export Routes
@admin.route('/admin/backup')
@admin_required
def admin_backup():
    """Show backup and export options."""
    return render_template('admin/backup.html')


@admin.route('/admin/export/posts')
@admin_required
def admin_export_posts():
    """Export all posts as JSON."""
    try:
        posts = PostModel.get_articles_paginated(page=1, per_page=10000)  # Get all posts
        
        # Convert datetime objects to strings for JSON serialization
        export_data = []
        for post in posts:
            post_data = dict(post)
            # Convert datetime fields to ISO format strings
            for field in ['created_at', 'updated_at', 'publish_date']:
                if post_data.get(field):
                    post_data[field] = post_data[field].isoformat() if hasattr(post_data[field], 'isoformat') else str(post_data[field])
            export_data.append(post_data)
        
        # Create response
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'posts_export_{timestamp}.json'
        
        response = make_response(json.dumps(export_data, indent=2))
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        
        return response
        
    except Exception as e:
        flash('Error exporting posts.', 'error')
        return redirect(url_for('admin.admin_backup'))


@admin.route('/admin/export/categories')
@admin_required
def admin_export_categories():
    """Export all categories as JSON."""
    try:
        categories = CategoryModel.get_all_categories()
        
        # Convert to list of dictionaries
        export_data = [dict(category) for category in categories]
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'categories_export_{timestamp}.json'
        
        response = make_response(json.dumps(export_data, indent=2))
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        
        return response
        
    except Exception as e:
        flash('Error exporting categories.', 'error')
        return redirect(url_for('admin.admin_backup'))


@admin.route('/admin/export/tags')
@admin_required
def admin_export_tags():
    """Export all tags as JSON."""
    try:
        tags = TagModel.get_all_tags()
        
        # Convert to list of dictionaries
        export_data = [dict(tag) for tag in tags]
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'tags_export_{timestamp}.json'
        
        response = make_response(json.dumps(export_data, indent=2))
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        
        return response
        
    except Exception as e:
        flash('Error exporting tags.', 'error')
        return redirect(url_for('admin.admin_backup'))


@admin.route('/admin/export/complete-backup')
@admin_required
def admin_complete_backup():
    """Create a complete backup including all content and media files."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
            with zipfile.ZipFile(temp_file.name, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                
                # Export posts
                posts = PostModel.get_articles_paginated(page=1, per_page=10000)
                posts_data = []
                for post in posts:
                    post_data = dict(post)
                    for field in ['created_at', 'updated_at', 'publish_date']:
                        if post_data.get(field):
                            post_data[field] = post_data[field].isoformat() if hasattr(post_data[field], 'isoformat') else str(post_data[field])
                    posts_data.append(post_data)
                
                zip_file.writestr('posts.json', json.dumps(posts_data, indent=2))
                
                # Export categories
                categories = CategoryModel.get_all_categories()
                categories_data = [dict(category) for category in categories]
                zip_file.writestr('categories.json', json.dumps(categories_data, indent=2))
                
                # Export tags
                tags = TagModel.get_all_tags()
                tags_data = [dict(tag) for tag in tags]
                zip_file.writestr('tags.json', json.dumps(tags_data, indent=2))
                
                # Export templates if available
                try:
                    templates = PostTemplateModel.get_all_templates()
                    templates_data = [dict(template) for template in templates]
                    zip_file.writestr('templates.json', json.dumps(templates_data, indent=2))
                except:
                    pass
                
                # Export about information
                try:
                    about_info = AboutModel.get_about_info()
                    if about_info:
                        zip_file.writestr('about.json', json.dumps(dict(about_info), indent=2))
                except:
                    pass
                
                # Add uploaded images
                upload_folder = current_app.config.get('UPLOAD_FOLDER')
                if upload_folder and os.path.exists(upload_folder):
                    for filename in os.listdir(upload_folder):
                        file_path = os.path.join(upload_folder, filename)
                        if os.path.isfile(file_path):
                            zip_file.write(file_path, f'uploads/{filename}')
                
                # Add backup metadata
                metadata = {
                    'backup_date': datetime.now().isoformat(),
                    'backup_type': 'complete',
                    'posts_count': len(posts_data),
                    'categories_count': len(categories_data),
                    'tags_count': len(tags_data)
                }
                zip_file.writestr('backup_metadata.json', json.dumps(metadata, indent=2))
        
        # Log backup activity
        ActivityLogModel.log_activity(
            admin_username=session.get('admin_username', 'unknown'),
            action='Complete Backup Created',
            details=f'Created complete backup archive with {len(posts_data)} posts, {len(categories_data)} categories, {len(tags_data)} tags',
            ip_address=request.remote_addr
        )
        
        # Send the zip file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'complete_backup_{timestamp}.zip'
        
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=filename,
            mimetype='application/zip'
        )
        
    except Exception as e:
        flash('Error creating complete backup.', 'error')
        return redirect(url_for('admin.admin_backup'))


@admin.route('/admin/activity-log')
@admin_required
def admin_activity_log():
    """View admin activity log."""
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('query', '')
    
    if search_query:
        activities = ActivityLogModel.search_activities(search_query, page=page, per_page=20)
        total_activities = len(ActivityLogModel.search_activities(search_query, page=1, per_page=10000))
    else:
        activities = ActivityLogModel.get_activities_paginated(page=page, per_page=20)
        total_activities = ActivityLogModel.count_activities()
    
    # Calculate pagination
    per_page = 20
    total_pages = (total_activities + per_page - 1) // per_page
    
    return render_template('admin/activity_log.html', 
                         activities=activities, 
                         page=page, 
                         total_pages=total_pages,
                         search_query=search_query,
                         total_activities=total_activities)