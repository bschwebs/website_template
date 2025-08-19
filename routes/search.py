"""
Search and tag filtering routes for the Story Hub application.
"""
from flask import Blueprint, render_template, request, jsonify
from models import PostModel, TagModel
from forms import SearchForm
from utils import is_admin_logged_in

search = Blueprint('search', __name__)


@search.route('/search')
def search_posts():
    """Search posts by query with advanced filtering."""
    form = SearchForm()
    query = request.args.get('query', '').strip()
    page = request.args.get('page', 1, type=int)
    
    # Advanced filtering parameters
    category_filter = request.args.get('category', '').strip()
    tag_filter = request.args.get('tag', '').strip()
    date_from = request.args.get('date_from', '').strip()
    date_to = request.args.get('date_to', '').strip()
    sort_by = request.args.get('sort_by', 'relevance').strip()
    
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
    
    # Get filter options for the UI (only categories and tags with posts)
    from models import CategoryModel
    categories = CategoryModel.get_categories_with_posts()
    popular_tags = TagModel.get_tags_with_posts(limit=20)
    
    if query:
        # Perform advanced search with filters
        posts = PostModel.advanced_search(
            query=query, 
            page=page, 
            per_page=per_page,
            category_filter=category_filter,
            tag_filter=tag_filter,
            date_from=date_from,
            date_to=date_to,
            sort_by=sort_by
        )
        total_posts = PostModel.count_advanced_search(
            query=query,
            category_filter=category_filter,
            tag_filter=tag_filter,
            date_from=date_from,
            date_to=date_to
        )
        
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
                         per_page=per_page,
                         categories=categories,
                         popular_tags=popular_tags,
                         category_filter=category_filter,
                         tag_filter=tag_filter,
                         date_from=date_from,
                         date_to=date_to,
                         sort_by=sort_by)


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


@search.route('/api/search/suggestions')
def search_suggestions():
    """API endpoint for live search suggestions."""
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 2:
        return jsonify({'suggestions': []})
    
    # Get suggestions from posts and tags
    post_suggestions = PostModel.get_search_suggestions(query, limit=5)
    tag_suggestions = TagModel.get_tag_suggestions(query, limit=3)
    
    suggestions = []
    
    # Add post suggestions
    for post in post_suggestions:
        suggestions.append({
            'type': 'post',
            'title': post.title,
            'url': f"/posts/{post.slug}" if post.slug else f"/posts/{post.id}",
            'excerpt': post.excerpt[:100] + '...' if post.excerpt and len(post.excerpt) > 100 else post.excerpt,
            'category': post.category_name if hasattr(post, 'category_name') else None
        })
    
    # Add tag suggestions
    for tag in tag_suggestions:
        suggestions.append({
            'type': 'tag',
            'title': f"#{tag.name}",
            'url': f"/tag/{tag.slug}",
            'description': f"{tag.post_count} posts" if hasattr(tag, 'post_count') else "Tag"
        })
    
    return jsonify({'suggestions': suggestions})


@search.route('/api/search/quick')
def quick_search():
    """API endpoint for quick search results."""
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({'posts': [], 'total': 0})
    
    # Get quick search results (fewer posts for dropdown)
    posts = PostModel.search_posts(query, page=1, per_page=8)
    total = PostModel.count_search_results(query)
    
    results = []
    for post in posts:
        results.append({
            'id': post.id,
            'title': post.title,
            'slug': post.slug,
            'excerpt': post.excerpt[:150] + '...' if post.excerpt and len(post.excerpt) > 150 else post.excerpt,
            'category': post.category_name if hasattr(post, 'category_name') else None,
            'image': post.image_filename,
            'created_at': post.created_at.strftime('%Y-%m-%d') if post.created_at else None
        })
    
    return jsonify({'posts': results, 'total': total})


# Add search form to template context
@search.app_context_processor
def inject_search_form():
    """Inject search form into all templates."""
    return {'search_form': SearchForm(), 'is_admin_logged_in': is_admin_logged_in()}