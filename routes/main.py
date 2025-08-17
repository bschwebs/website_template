"""
Main routes for the Story Hub application.
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for
from models import PostModel, TagModel, CategoryModel, ContactModel, EmailConfigModel
from utils import is_admin_logged_in
from forms import ContactForm
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
    """Stories page with pagination."""
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    
    # Responsive pagination - 6 for larger devices, 3 for mobile
    # We'll use JavaScript to determine this, but default to 6
    per_page = request.args.get('per_page', 6, type=int)
    if per_page not in [3, 6]:
        per_page = 6  # Default fallback
    
    # Get paginated stories
    stories = PostModel.get_posts_by_type_paginated('story', page, per_page)
    total_stories = PostModel.count_posts_by_type('story')
    
    # Calculate pagination info
    total_pages = (total_stories + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages
    prev_page = page - 1 if has_prev else None
    next_page = page + 1 if has_next else None
    
    return render_template('stories.html', 
                         stories=stories,
                         page=page,
                         total_pages=total_pages,
                         has_prev=has_prev,
                         has_next=has_next,
                         prev_page=prev_page,
                         next_page=next_page,
                         per_page=per_page,
                         total_stories=total_stories)


@main.route('/articles')
def articles():
    """Articles page with pagination."""
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    
    # Responsive pagination - 6 for larger devices, 3 for mobile
    # We'll use JavaScript to determine this, but default to 6
    per_page = request.args.get('per_page', 6, type=int)
    if per_page not in [3, 6]:
        per_page = 6  # Default fallback
    
    # Get paginated articles
    articles = PostModel.get_posts_by_type_paginated('article', page, per_page)
    total_articles = PostModel.count_posts_by_type('article')
    
    # Calculate pagination info
    total_pages = (total_articles + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages
    prev_page = page - 1 if has_prev else None
    next_page = page + 1 if has_next else None
    
    return render_template('articles.html', 
                         articles=articles,
                         page=page,
                         total_pages=total_pages,
                         has_prev=has_prev,
                         has_next=has_next,
                         prev_page=prev_page,
                         next_page=next_page,
                         per_page=per_page,
                         total_articles=total_articles)


@main.route('/articles/category/<category_slug>')
def articles_by_category(category_slug):
    """Articles page filtered by category with pagination."""
    # Get the category
    category = CategoryModel.get_category_by_slug(category_slug)
    if not category:
        return render_template('404.html'), 404
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    
    # Responsive pagination - 6 for larger devices, 3 for mobile
    per_page = request.args.get('per_page', 6, type=int)
    if per_page not in [3, 6]:
        per_page = 6  # Default fallback
    
    # Get paginated articles for this category
    articles = PostModel.get_posts_by_type_paginated('article', page, per_page, category['id'])
    total_articles = PostModel.count_posts_by_type('article', category['id'])
    
    # Calculate pagination info
    total_pages = (total_articles + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages
    prev_page = page - 1 if has_prev else None
    next_page = page + 1 if has_next else None
    
    return render_template('articles.html', 
                         articles=articles,
                         page=page,
                         total_pages=total_pages,
                         has_prev=has_prev,
                         has_next=has_next,
                         prev_page=prev_page,
                         next_page=next_page,
                         per_page=per_page,
                         total_articles=total_articles,
                         category=category)


@main.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact form page."""
    form = ContactForm()
    
    
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        subject = form.subject.data
        message = form.message.data
        
        # Save message to database
        try:
            ContactModel.save_message(name, email, subject, message)
            
            # Try to send email if configured
            email_config = EmailConfigModel.get_config()
            if email_config:
                try:
                    send_contact_email(email_config, name, email, subject, message)
                    flash('Thank you for your message! We\'ll get back to you soon.', 'success')
                except Exception as e:
                    # Email failed but message was saved
                    flash('Thank you for your message! We\'ll get back to you soon.', 'success')
            else:
                flash('Thank you for your message! We\'ll get back to you soon.', 'success')
            
            return redirect(url_for('main.contact'))
            
        except Exception as e:
            flash('Sorry, there was an error sending your message. Please try again.', 'error')
    
    return render_template('contact.html', form=form)


def send_contact_email(config, name, email, subject, message):
    """Send contact form email."""
    # Create message
    msg = MIMEMultipart()
    msg['From'] = config['from_email']
    msg['To'] = config['to_email']
    msg['Subject'] = f"Contact Form: {subject}"
    
    # Email body
    body = f"""
New contact form submission:

Name: {name}
Email: {email}
Subject: {subject}

Message:
{message}

---
This message was sent via the contact form on Japan's History.
Reply directly to this email to respond to {name} at {email}.
"""
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Send email
    server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
    if config['use_tls']:
        server.starttls()
    server.login(config['smtp_username'], config['smtp_password'])
    server.send_message(msg)
    server.quit()


# Add admin status and categories to template context
@main.app_context_processor
def inject_template_vars():
    """Inject admin login status and categories into all templates."""
    # Only show categories that have articles
    all_categories = CategoryModel.get_all_categories()
    categories_with_articles = [cat for cat in all_categories if cat['post_count'] > 0]
    
    return {
        'is_admin_logged_in': is_admin_logged_in(),
        'categories': categories_with_articles
    }