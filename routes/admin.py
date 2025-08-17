"""
Admin routes for the Story Hub application.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import PostModel, AdminModel, TagModel
from forms import DeleteForm
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