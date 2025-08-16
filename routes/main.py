"""
Main routes for the Story Hub application.
"""
from flask import Blueprint, render_template, request
from models import PostModel, TagModel
from utils import is_admin_logged_in

main = Blueprint('main', __name__)


@main.route('/')
def index():
    """Home page with featured post and latest posts."""
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 3  # Show 3 posts per page
    
    # Get featured post
    featured_post = PostModel.get_featured_post()
    
    # Get total count of non-featured posts
    if featured_post:
        total_posts = PostModel.count_non_featured_posts()
        posts = PostModel.get_non_featured_posts_paginated(page, per_page)
    else:
        total_posts = PostModel.count_all_posts()
        posts = PostModel.get_all_posts_paginated(page, per_page)
    
    # Calculate pagination info
    total_pages = (total_posts + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages
    prev_page = page - 1 if has_prev else None
    next_page = page + 1 if has_next else None
    
    # Get popular tags for sidebar
    popular_tags = TagModel.get_popular_tags(8)
    
    return render_template('index.html', 
                         posts=posts, 
                         featured_post=featured_post,
                         page=page,
                         total_pages=total_pages,
                         has_prev=has_prev,
                         has_next=has_next,
                         prev_page=prev_page,
                         next_page=next_page,
                         popular_tags=popular_tags)


@main.route('/stories')
def stories():
    """Stories page."""
    stories = PostModel.get_posts_by_type('story')
    return render_template('stories.html', stories=stories)


@main.route('/articles')
def articles():
    """Articles page."""
    articles = PostModel.get_posts_by_type('article')
    return render_template('articles.html', articles=articles)


# Add admin status to template context
@main.app_context_processor
def inject_admin_status():
    """Inject admin login status into all templates."""
    return {'is_admin_logged_in': is_admin_logged_in()}