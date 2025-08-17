"""
SEO-related routes for the Story Hub application.
"""
from flask import Blueprint, Response, url_for, render_template_string
from models import PostModel, TagModel
from datetime import datetime

seo = Blueprint('seo', __name__)


@seo.route('/sitemap.xml')
def sitemap():
    """Generate XML sitemap for search engines."""
    
    # Get all posts
    posts = PostModel.get_all_posts()
    
    # Get all tags
    tags = TagModel.get_all_tags()
    
    # Generate sitemap XML
    sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <!-- Home page -->
    <url>
        <loc>{{ url_for('main.index', _external=True) }}</loc>
        <lastmod>{{ last_modified }}</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
    
    
    <!-- Articles page -->
    <url>
        <loc>{{ url_for('main.articles', _external=True) }}</loc>
        <lastmod>{{ last_modified }}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>
    
    <!-- Search page -->
    <url>
        <loc>{{ url_for('search.search_posts', _external=True) }}</loc>
        <lastmod>{{ last_modified }}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.6</priority>
    </url>
    
    <!-- All tags page -->
    <url>
        <loc>{{ url_for('search.all_tags', _external=True) }}</loc>
        <lastmod>{{ last_modified }}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.7</priority>
    </url>
    
    <!-- Individual posts -->
    {% for post in posts %}
    <url>
        <loc>{{ url_for('posts.view_post_by_slug', slug=post.slug, _external=True) if post.slug else url_for('posts.view_post', post_id=post.id, _external=True) }}</loc>
        <lastmod>{{ post.updated_at or post.created_at }}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>{% if post.featured %}0.9{% else %}0.7{% endif %}</priority>
    </url>
    {% endfor %}
    
    <!-- Tag pages -->
    {% for tag in tags %}
    <url>
        <loc>{{ url_for('search.posts_by_tag', slug=tag.slug, _external=True) }}</loc>
        <lastmod>{{ last_modified }}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.6</priority>
    </url>
    {% endfor %}
</urlset>"""
    
    # Get the most recent post update time
    last_modified = datetime.now().strftime('%Y-%m-%d')
    if posts:
        most_recent = max(posts, key=lambda p: p['updated_at'] or p['created_at'])
        last_modified = (most_recent['updated_at'] or most_recent['created_at'])[:10]
    
    # Render the sitemap
    rendered_sitemap = render_template_string(
        sitemap_xml,
        posts=posts,
        tags=tags,
        last_modified=last_modified
    )
    
    return Response(rendered_sitemap, mimetype='application/xml')


@seo.route('/robots.txt')
def robots():
    """Generate robots.txt file for search engines."""
    
    robots_txt = """User-agent: *
Allow: /

# Sitemap
Sitemap: {{ url_for('seo.sitemap', _external=True) }}

# Crawl-delay for polite crawling
Crawl-delay: 1

# Disallow admin areas
Disallow: /admin/
Disallow: /static/uploads/

# Allow important pages
Allow: /
Allow: /about
Allow: /articles
Allow: /search
Allow: /tags
Allow: /post/
Allow: /tag/
"""
    
    rendered_robots = render_template_string(robots_txt)
    return Response(rendered_robots, mimetype='text/plain')


@seo.route('/.well-known/security.txt')
def security():
    """Generate security.txt file for security researchers."""
    
    security_txt = """Contact: mailto:security@storyhub.com
Expires: 2025-12-31T23:59:59.000Z
Preferred-Languages: en
Canonical: {{ url_for('seo.security', _external=True) }}
Policy: {{ url_for('main.index', _external=True) }}/security-policy
"""
    
    rendered_security = render_template_string(security_txt)
    return Response(rendered_security, mimetype='text/plain')


@seo.route('/feed.xml')
def rss_feed():
    """Generate RSS feed for the blog."""
    
    # Get recent posts
    posts = PostModel.get_all_posts(20)  # Limit to 20 most recent posts
    
    rss_xml = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
    <channel>
        <title>Story Hub - Latest Posts</title>
        <link>{{ url_for('main.index', _external=True) }}</link>
        <description>Discover insightful articles about Japanese history and culture from our community of writers.</description>
        <language>en-us</language>
        <lastBuildDate>{{ build_date }}</lastBuildDate>
        <atom:link href="{{ url_for('seo.rss_feed', _external=True) }}" rel="self" type="application/rss+xml" />
        
        {% for post in posts %}
        <item>
            <title>{{ post.title }}</title>
            <link>{{ url_for('posts.view_post_by_slug', slug=post.slug, _external=True) if post.slug else url_for('posts.view_post', post_id=post.id, _external=True) }}</link>
            <description><![CDATA[{{ post.excerpt if post.excerpt else (post.content|striptags)[:200] }}]]></description>
            <guid>{{ url_for('posts.view_post_by_slug', slug=post.slug, _external=True) if post.slug else url_for('posts.view_post', post_id=post.id, _external=True) }}</guid>
            <pubDate>{{ post.created_at }}</pubDate>
            <category>Article</category>
            {% if post.image_filename %}
            <enclosure url="{{ url_for('static', filename='uploads/' + post.image_filename, _external=True) }}" type="image/jpeg" />
            {% endif %}
        </item>
        {% endfor %}
    </channel>
</rss>"""
    
    build_date = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    rendered_rss = render_template_string(
        rss_xml,
        posts=posts,
        build_date=build_date
    )
    
    return Response(rendered_rss, mimetype='application/rss+xml')