"""
Search and tag filtering routes for the Story Hub application.
"""
from flask import Blueprint, render_template, request
from models import PostModel, TagModel
from forms import SearchForm
from utils import is_admin_logged_in

search = Blueprint('search', __name__)


@search.route('/search')
def search_posts():
    """Search posts by query."""
    form = SearchForm()
    query = request.args.get('query', '').strip()
    page = request.args.get('page', 1, type=int)
    
    # Responsive pagination - 6 for larger devices, 3 for mobile
    # We'll use JavaScript to determine this, but default to 6
    per_page = request.args.get('per_page', 6, type=int)
    if per_page not in [3, 6]:
        per_page = 6  # Default fallback
    
    posts = []
    total_posts = 0
    total_pages = 0
    has_prev = False
    has_next = False
    prev_page = None
    next_page = None
    
    if query:
        # Perform search
        posts = PostModel.search_posts(query, page, per_page)
        total_posts = PostModel.count_search_results(query)
        
        # Calculate pagination
        total_pages = (total_posts + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages
        prev_page = page - 1 if has_prev else None
        next_page = page + 1 if has_next else None
    
    return render_template('search/results.html',
                         form=form,
                         posts=posts,
                         query=query,
                         total_posts=total_posts,
                         page=page,
                         total_pages=total_pages,
                         has_prev=has_prev,
                         has_next=has_next,
                         prev_page=prev_page,
                         next_page=next_page,
                         per_page=per_page)


@search.route('/tag/<slug>')
def posts_by_tag(slug):
    """Display posts filtered by tag."""
    tag = TagModel.get_tag_by_slug(slug)
    if not tag:
        return render_template('404.html'), 404
    
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Get posts by tag
    posts = PostModel.get_posts_by_tag(slug, page, per_page)
    total_posts = PostModel.count_posts_by_tag(slug)
    
    # Calculate pagination
    total_pages = (total_posts + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages
    prev_page = page - 1 if has_prev else None
    next_page = page + 1 if has_next else None
    
    return render_template('search/tag.html',
                         tag=tag,
                         posts=posts,
                         total_posts=total_posts,
                         page=page,
                         total_pages=total_pages,
                         has_prev=has_prev,
                         has_next=has_next,
                         prev_page=prev_page,
                         next_page=next_page)


@search.route('/tags')
def all_tags():
    """Display all tags."""
    tags = TagModel.get_all_tags()
    return render_template('search/tags.html', tags=tags)


# Add search form to template context
@search.app_context_processor
def inject_search_form():
    """Inject search form into all templates."""
    return {'search_form': SearchForm(), 'is_admin_logged_in': is_admin_logged_in()}