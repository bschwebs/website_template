"""
Post-related routes for the Story Hub application.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import PostModel
from forms import PostForm, DeleteForm
from utils import admin_required, generate_unique_slug, save_uploaded_file, delete_file, parse_tags
from flask import current_app
import os

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
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        excerpt = form.excerpt.data
        post_type = form.post_type.data
        
        # Handle file upload
        image_filename = None
        if form.image.data:
            image_filename = save_uploaded_file(form.image.data, current_app.config['UPLOAD_FOLDER'])
        
        # Generate unique slug
        slug = generate_unique_slug(title)
        
        # Get image positioning
        image_position_x = form.image_position_x.data
        image_position_y = form.image_position_y.data
        
        # Create the post
        PostModel.create_post(title, content, excerpt, image_filename, post_type, slug, image_position_x, image_position_y)
        
        # Get the newly created post to add tags
        new_post = PostModel.get_post_by_slug(slug)
        if new_post and form.tags.data:
            tag_list = parse_tags(form.tags.data)
            PostModel.add_tags_to_post(new_post['id'], tag_list)
        
        flash('Post created successfully!', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('create.html', form=form)


@posts.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@admin_required
def edit_post(post_id):
    """Edit an existing post."""
    post = PostModel.get_post_by_id(post_id)
    
    if post is None:
        flash('Post not found.', 'error')
        return redirect(url_for('main.index'))
    
    form = PostForm()
    
    # Pre-populate form with existing data on GET request
    if request.method == 'GET':
        form.title.data = post['title']
        form.content.data = post['content']
        form.excerpt.data = post['excerpt']
        form.post_type.data = post['post_type']
        form.image_position_x.data = post['image_position_x'] if post['image_position_x'] else 'center'
        form.image_position_y.data = post['image_position_y'] if post['image_position_y'] else 'center'
        
        # Get existing tags
        existing_tags = PostModel.get_post_tags(post_id)
        if existing_tags:
            form.tags.data = ', '.join([tag['name'] for tag in existing_tags])

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        excerpt = form.excerpt.data
        post_type = form.post_type.data
        
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
        
        # Update the post
        PostModel.update_post(post_id, title, content, excerpt, image_filename, post_type, slug, image_position_x, image_position_y)
        
        # Update tags
        if form.tags.data is not None:  # Check if tags field was submitted
            tag_list = parse_tags(form.tags.data)
            PostModel.add_tags_to_post(post_id, tag_list)
        
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