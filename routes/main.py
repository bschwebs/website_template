"""
Main routes for the Story Hub application.
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for
from models import PostModel, TagModel, CategoryModel, ContactModel, EmailConfigModel, AboutModel, ActivityLogModel, SocialLinksModel
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
    
    # Responsive pagination based on screen size
    # Default: 3 cards (desktop: 1 row), medium: 2 cards (1 row), mobile: 3 cards (3 rows)
    per_page = request.args.get('per_page', 3, type=int)
    
    # Validate per_page values (allow 2 for medium screens, 3 for desktop/mobile)
    if per_page not in [2, 3, 6]:
        per_page = 3  # Default fallback
    
    # Get featured post
    featured_post = PostModel.get_featured_post()
    
    # Get introduction post
    introduction_post = PostModel.get_introduction_post()
    
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
                         introduction_post=introduction_post,
                         page=page,
                         total_pages=total_pages,
                         has_prev=has_prev,
                         has_next=has_next,
                         prev_page=prev_page,
                         next_page=next_page,
                         per_page=per_page,
                         popular_tags=popular_tags)



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
    articles = PostModel.get_articles_paginated(page, per_page)
    total_articles = PostModel.count_articles()
    
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
    articles = PostModel.get_articles_paginated(page, per_page, category['id'])
    total_articles = PostModel.count_articles(category['id'])
    
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
            
            # Log the contact message submission
            ActivityLogModel.log_activity(
                admin_username='system',
                action='Contact Message Received',
                details=f'New contact message from {name} ({email}) - Subject: "{subject}"',
                ip_address=request.remote_addr
            )
            
            # Try to send email if configured
            email_config = EmailConfigModel.get_config()
            if email_config:
                try:
                    send_contact_email(email_config, name, email, subject, message)
                    # Log successful email notification
                    ActivityLogModel.log_activity(
                        admin_username='system',
                        action='Email Notification Sent',
                        details=f'Contact form notification sent to admin for message from {name}',
                        ip_address=request.remote_addr
                    )
                    flash('Thank you for your message! We\'ll get back to you soon.', 'success')
                except Exception as e:
                    # Email failed but message was saved - log the failure
                    ActivityLogModel.log_activity(
                        admin_username='system',
                        action='Email Notification Failed',
                        details=f'Failed to send email notification for contact message from {name}: {str(e)}',
                        ip_address=request.remote_addr
                    )
                    flash('Thank you for your message! We\'ll get back to you soon.', 'success')
            else:
                # No email config - log this
                ActivityLogModel.log_activity(
                    admin_username='system',
                    action='Email Config Missing',
                    details='Contact message received but no email configuration found for notifications',
                    ip_address=request.remote_addr
                )
                flash('Thank you for your message! We\'ll get back to you soon.', 'success')
            
            return redirect(url_for('main.contact'))
            
        except Exception as e:
            flash('Sorry, there was an error sending your message. Please try again.', 'error')
    
    return render_template('contact.html', form=form)


@main.route('/about')
def about():
    """About page."""
    about_info = AboutModel.get_about_info()
    return render_template('about.html', about_info=about_info)


def send_contact_email(config, name, email, subject, message):
    """Send contact form email notification to admin."""
    from datetime import datetime
    import logging
    
    # Set up logging for debugging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    # Validate config object
    if not config:
        logger.error("Email configuration is None")
        raise ValueError("Email configuration is None")
    
    # Debug: Print config attributes
    logger.debug(f"Config object type: {type(config)}")
    logger.debug(f"Config object attributes: {dir(config)}")
    
    # Check required config attributes
    required_attrs = ['from_email', 'to_email', 'smtp_server', 'smtp_port', 'smtp_username', 'smtp_password', 'use_tls']
    for attr in required_attrs:
        if attr not in config:
            logger.error(f"Config missing attribute: {attr}")
            raise ValueError(f"Email configuration missing required attribute: {attr}")
        
        value = config[attr]
        if value is None or (isinstance(value, str) and value.strip() == ''):
            logger.error(f"Config attribute {attr} is None or empty: {value}")
            raise ValueError(f"Email configuration attribute {attr} is None or empty")
        
        logger.debug(f"Config {attr}: {'***' if 'password' in attr else value}")
    
    # Create message
    msg = MIMEMultipart('alternative')
    msg['From'] = config['from_email']
    msg['To'] = config['to_email']
    msg['Reply-To'] = email  # Allow direct reply to sender
    msg['Subject'] = f"📧 New Contact Message: {subject}"
    
    # Plain text version
    text_body = f"""
New Contact Form Submission - Japan's History Blog

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SENDER INFORMATION:
👤 Name: {name}
📧 Email: {email}
📝 Subject: {subject}
🕒 Received: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

MESSAGE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{message}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ADMIN ACTIONS:
• View all messages: your-site.com/admin/contact-messages
• Reply directly to this email to respond to {name}
• Email will be sent from: {email}

---
This notification was sent automatically by Japan's History Blog.
"""

    # HTML version for better formatting
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #2d1810 0%, #8b4513 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; text-align: center; }}
        .content {{ padding: 30px; }}
        .info-row {{ margin: 15px 0; padding: 10px; background-color: #f8f9fa; border-left: 4px solid #007bff; border-radius: 4px; }}
        .message-box {{ background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 6px; padding: 20px; margin: 20px 0; }}
        .footer {{ background-color: #f8f9fa; padding: 20px; border-radius: 0 0 8px 8px; text-align: center; color: #6c757d; font-size: 14px; }}
        .btn {{ display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 5px; }}
        .highlight {{ color: #8b4513; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📧 New Contact Message</h1>
            <p>Japan's History Blog</p>
        </div>
        
        <div class="content">
            <h2>Message Details</h2>
            
            <div class="info-row">
                <strong>👤 From:</strong> {name}
            </div>
            
            <div class="info-row">
                <strong>📧 Email:</strong> <a href="mailto:{email}">{email}</a>
            </div>
            
            <div class="info-row">
                <strong>📝 Subject:</strong> {subject}
            </div>
            
            <div class="info-row">
                <strong>🕒 Received:</strong> {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}
            </div>
            
            <div class="message-box">
                <h3>Message Content:</h3>
                <div style="white-space: pre-wrap; line-height: 1.6;">{message}</div>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="mailto:{email}?subject=Re: {subject}" class="btn">Reply to {name}</a>
                <a href="#/admin/contact-messages" class="btn">View All Messages</a>
            </div>
        </div>
        
        <div class="footer">
            <p>This notification was sent automatically by your Japan's History Blog contact form.</p>
            <p>To configure email settings, visit your <a href="#/admin/email-config">admin panel</a>.</p>
        </div>
    </div>
</body>
</html>
"""
    
    # Attach both versions
    msg.attach(MIMEText(text_body, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))
    
    # Send email
    logger.debug(f"Connecting to SMTP server: {config['smtp_server']}:{config['smtp_port']}")
    try:
        server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
        logger.debug("SMTP connection established")
        
        if config['use_tls']:
            logger.debug("Starting TLS")
            server.starttls()
            logger.debug("TLS started successfully")
        
        logger.debug(f"Logging in with username: {config['smtp_username']}")
        server.login(config['smtp_username'], config['smtp_password'])
        logger.debug("SMTP login successful")
        
        logger.debug("Sending email message")
        server.send_message(msg)
        logger.debug("Email sent successfully")
        
        server.quit()
        logger.debug("SMTP connection closed")
        
    except Exception as smtp_error:
        logger.error(f"SMTP Error: {type(smtp_error).__name__}: {str(smtp_error)}")
        if 'server' in locals():
            try:
                server.quit()
            except:
                pass
        raise smtp_error


# Add admin status and categories to template context
@main.app_context_processor
def inject_template_vars():
    """Inject admin login status and categories into all templates."""
    # Only show categories that have articles
    all_categories = CategoryModel.get_all_categories()
    categories_with_articles = [cat for cat in all_categories if cat['post_count'] > 0]
    
    # Get introduction post for navbar
    introduction_post = PostModel.get_introduction_post()
    
    # Get active social links for footer
    social_links = SocialLinksModel.get_active_social_links()
    
    return {
        'is_admin_logged_in': is_admin_logged_in(),
        'categories': categories_with_articles,
        'navbar_introduction_post': introduction_post,
        'social_links': social_links
    }