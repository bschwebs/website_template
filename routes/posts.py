"""
Post-related routes for the Story Hub application.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import PostModel, CategoryModel, PostTemplateModel, ActivityLogModel
from forms import PostForm, DeleteForm
from utils import admin_required, generate_unique_slug, save_uploaded_file, delete_file, parse_tags
from flask import current_app
import os
from datetime import datetime

posts = Blueprint('posts', __name__)


@posts.route('/post/<slug>')
def view_post_by_slug(slug):
    """View a post by its slug."""
    post = PostModel.get_post_by_slug(slug)
    if post is None:
        flash('Post not found.', 'error')
        return redirect(url_for('main.index'))
    
    # Get tags for this post
    tags = PostModel.get_post_tags(post['id'])
    form = DeleteForm()
    return render_template('post.html', post=post, tags=tags, form=form)


@posts.route('/post/<int:post_id>')
def view_post(post_id):
    """View a post by ID (redirects to slug if available)."""
    post = PostModel.get_post_by_id(post_id)
    if post is None:
        flash('Post not found.', 'error')
        return redirect(url_for('main.index'))
    
    # Redirect to slug-based URL if slug exists
    if post['slug']:
        return redirect(url_for('posts.view_post_by_slug', slug=post['slug']), code=301)
    
    # Get tags for this post
    tags = PostModel.get_post_tags(post['id'])
    form = DeleteForm()
    return render_template('post.html', post=post, tags=tags, form=form)


@posts.route('/create', methods=['GET', 'POST'])
@admin_required
def create_post():
    """Create a new post."""
    form = PostForm()
    
    # Populate category choices
    categories = CategoryModel.get_all_categories()
    form.category_id.choices = [(None, 'No Category')] + [(cat['id'], cat['name']) for cat in categories]
    
    # Populate template choices
    templates = PostTemplateModel.get_all_templates()
    form.template_id.choices = [(None, 'No Template')] + [(template['id'], template['name']) for template in templates]
    
    if form.validate_on_submit():
        # Check if this is a preview request
        if request.form.get('preview') == 'true':
            # Create a temporary post object for preview
            preview_post = {
                'id': 0,  # Temporary ID for new post
                'title': form.title.data,
                'content': form.content.data,
                'excerpt': form.excerpt.data,
                'image_filename': None,  # No image for new post preview
                'slug': generate_unique_slug(form.title.data),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'category_id': form.category_id.data,
                'status': form.status.data,
                'publish_date': form.publish_date.data,
                'template_id': form.template_id.data,
                'image_position_x': form.image_position_x.data,
                'image_position_y': form.image_position_y.data
            }
            
            # Get tags for preview
            if form.tags.data:
                tag_list = parse_tags(form.tags.data)
                preview_tags = [{'name': tag} for tag in tag_list]
            else:
                preview_tags = []
            
            form = DeleteForm()
            return render_template('post.html', post=preview_post, tags=preview_tags, form=form, preview=True)
        
        title = form.title.data
        content = form.content.data
        excerpt = form.excerpt.data
        post_type = 'article'  # All posts are now articles
        
        # Handle file upload
        image_filename = None
        if form.image.data:
            image_filename = save_uploaded_file(form.image.data, current_app.config['UPLOAD_FOLDER'])
        
        # Generate unique slug
        slug = generate_unique_slug(title)
        
        # Get image positioning
        image_position_x = form.image_position_x.data
        image_position_y = form.image_position_y.data
        
        # Get category
        category_id = form.category_id.data if form.category_id.data else None
        
        # Get template
        template_id = form.template_id.data if form.template_id.data else None
        
        # Get status and publish date
        status = form.status.data
        publish_date = form.publish_date.data if form.publish_date.data else None
        
        # If scheduling for future, force status to be draft
        if publish_date and publish_date > datetime.now():
            status = 'draft'
        
        # Check if trying to add to introduction category
        if category_id:
            category = CategoryModel.get_category_by_id(category_id)
            if category and category['slug'] == 'introduction':
                # Check if there's already a post in introduction category
                existing_intro = PostModel.get_introduction_post()
                if existing_intro:
                    flash('The Introduction category can only contain one post. Please edit the existing introduction post instead.', 'error')
                    return render_template('create.html', form=form)
        
        # Create the post
        PostModel.create_post(title, content, excerpt, image_filename, post_type, slug, 
                            image_position_x, image_position_y, category_id, status, publish_date, template_id)
        
        # Get the newly created post to add tags
        new_post = PostModel.get_post_by_slug(slug)
        if new_post and form.tags.data:
            tag_list = parse_tags(form.tags.data)
            PostModel.add_tags_to_post(new_post['id'], tag_list)
        
        # Log post creation activity
        ActivityLogModel.log_activity(
            admin_username=session.get('admin_username', 'unknown'),
            action='Post Created',
            details=f'Created new post: "{title}" (ID: {new_post["id"] if new_post else "unknown"}, Status: {status})',
            ip_address=request.remote_addr
        )
        
        flash('Post created successfully!', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('create.html', form=form)


@posts.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@admin_required
def edit_post(post_id):
    """Edit an existing post."""
    print(f"=== EDIT POST CALLED: {request.method} for post {post_id} ===")
    post = PostModel.get_post_by_id(post_id)
    
    if post is None:
        flash('Post not found.', 'error')
        return redirect(url_for('main.index'))
    
    form = PostForm()
    
    # Populate category choices
    categories = CategoryModel.get_all_categories()
    form.category_id.choices = [(None, 'No Category')] + [(cat['id'], cat['name']) for cat in categories]
    
    # Populate template choices
    templates = PostTemplateModel.get_all_templates()
    form.template_id.choices = [(None, 'No Template')] + [(template['id'], template['name']) for template in templates]
    
    # Pre-populate form with existing data on GET request
    if request.method == 'GET':
        form.title.data = post['title']
        form.content.data = post['content']
        form.excerpt.data = post['excerpt']
        form.category_id.data = post['category_id'] if post['category_id'] else None
        form.template_id.data = post['template_id'] if post['template_id'] else None
        form.status.data = post['status'] if post['status'] else 'published'
        if post['publish_date']:
            # Convert timestamp to datetime
            form.publish_date.data = datetime.fromisoformat(post['publish_date'].replace('Z', '+00:00')) if 'Z' in post['publish_date'] else datetime.strptime(post['publish_date'], '%Y-%m-%d %H:%M:%S')
        form.image_position_x.data = post['image_position_x'] if post['image_position_x'] else 'center'
        form.image_position_y.data = post['image_position_y'] if post['image_position_y'] else 'center'
        
        # Get existing tags
        existing_tags = PostModel.get_post_tags(post_id)
        if existing_tags:
            form.tags.data = ', '.join([tag['name'] for tag in existing_tags])

    # Debug form submission (avoiding Unicode issues)
    if request.method == 'POST':
        print(f"Form submitted. Validation result: {form.validate()}")
        if form.content.data:
            print(f"Content received, length: {len(form.content.data)}")
        else:
            print("Content field is empty!")
        if form.errors:
            print(f"Form has errors: {list(form.errors.keys())}")

    if form.validate_on_submit():
        # Check if this is a preview request
        if 'preview' in request.form:
            # Create a temporary post object for preview
            preview_post = {
                'id': post['id'],
                'title': form.title.data,
                'content': form.content.data,
                'excerpt': form.excerpt.data,
                'image_filename': post['image_filename'],  # Use existing image for preview
                'slug': post['slug'],
                'created_at': post['created_at'],
                'updated_at': post['updated_at'],
                'category_id': form.category_id.data,
                'status': form.status.data,
                'publish_date': form.publish_date.data,
                'template_id': form.template_id.data,
                'image_position_x': form.image_position_x.data,
                'image_position_y': form.image_position_y.data
            }
            
            # Get tags for preview
            if form.tags.data:
                tag_list = parse_tags(form.tags.data)
                preview_tags = [{'name': tag} for tag in tag_list]
            else:
                preview_tags = PostModel.get_post_tags(post_id)
            
            form = DeleteForm()
            return render_template('post.html', post=preview_post, tags=preview_tags, form=form, preview=True)
        
        title = form.title.data
        content = form.content.data
        excerpt = form.excerpt.data
        post_type = 'article'  # All posts are now articles
        
        image_filename = post['image_filename']
        if form.image.data:
            # Delete old image
            delete_file(image_filename)
            # Save new image
            image_filename = save_uploaded_file(form.image.data, current_app.config['UPLOAD_FOLDER'])
        
        # Generate new slug if title changed
        if title != post['title']:
            slug = generate_unique_slug(title, post_id)
        else:
            slug = post['slug'] if post['slug'] else generate_unique_slug(title, post_id)
        
        # Get image positioning
        image_position_x = form.image_position_x.data
        image_position_y = form.image_position_y.data
        
        # Get category
        category_id = form.category_id.data if form.category_id.data else None
        
        # Get template
        template_id = form.template_id.data if form.template_id.data else None
        
        # Get status and publish date
        status = form.status.data
        publish_date = form.publish_date.data if form.publish_date.data else None
        
        # If scheduling for future, force status to be draft
        if publish_date and publish_date > datetime.now():
            status = 'draft'
        
        # Check if trying to move to introduction category
        if category_id:
            category = CategoryModel.get_category_by_id(category_id)
            if category and category['slug'] == 'introduction':
                # Check if there's already a different post in introduction category
                existing_intro = PostModel.get_introduction_post()
                if existing_intro and existing_intro['id'] != post_id:
                    flash('The Introduction category can only contain one post. Please edit the existing introduction post instead.', 'error')
                    return render_template('edit.html', form=form, post=post)
        
        # Update the post
        PostModel.update_post(post_id, title, content, excerpt, image_filename, post_type, slug, 
                            image_position_x, image_position_y, category_id, status, publish_date, template_id)
        
        # Update tags
        if form.tags.data is not None:  # Check if tags field was submitted
            tag_list = parse_tags(form.tags.data)
            PostModel.add_tags_to_post(post_id, tag_list)
        
        # Log post update activity
        changes = []
        if title != post['title']:
            changes.append(f'title changed from "{post["title"]}" to "{title}"')
        if status != (post['status'] if post['status'] else 'published'):
            changes.append(f'status changed to {status}')
        if category_id != post['category_id']:
            changes.append('category changed')
        
        change_details = f'Updated post: "{title}" (ID: {post_id})' + (f' - {", ".join(changes)}' if changes else '')
        
        ActivityLogModel.log_activity(
            admin_username=session.get('admin_username', 'unknown'),
            action='Post Updated',
            details=change_details,
            ip_address=request.remote_addr
        )
        
        flash('Post updated successfully!', 'success')
        return redirect(url_for('posts.view_post_by_slug', slug=slug))
    
    return render_template('edit.html', form=form, post=post)


@posts.route('/delete/<int:post_id>', methods=['POST'])
@admin_required
def delete_post(post_id):
    """Delete a post."""
    form = DeleteForm()
    if form.validate_on_submit():
        post = PostModel.get_post_by_id(post_id)
        
        if post:
            # Log post deletion before actually deleting
            ActivityLogModel.log_activity(
                admin_username=session.get('admin_username', 'unknown'),
                action='Post Deleted',
                details=f'Deleted post: "{post["title"]}" (ID: {post_id})',
                ip_address=request.remote_addr
            )
            
            # Delete associated image file
            delete_file(post['image_filename'])
            # Delete the post
            PostModel.delete_post(post_id)
            flash('Post deleted successfully!', 'success')
        else:
            flash('Post not found.', 'error')
    else:
        flash('Invalid request.', 'error')
    
    return redirect(url_for('main.index'))


@posts.route('/preview/<int:post_id>')
@admin_required
def preview_post(post_id):
    """Preview a post (including drafts)."""
    post = PostModel.get_post_by_id(post_id)
    if post is None:
        flash('Post not found.', 'error')
        return redirect(url_for('main.index'))
    
    # Get tags for this post
    tags = PostModel.get_post_tags(post['id'])
    form = DeleteForm()
    return render_template('post.html', post=post, tags=tags, form=form, preview=True)


@posts.route('/api/template/<int:template_id>')
@admin_required
def get_template_content(template_id):
    """AJAX endpoint to get template content."""
    template = PostTemplateModel.get_template_by_id(template_id)
    if template:
        return {'content': template['content_template']}
    return {'error': 'Template not found'}, 404