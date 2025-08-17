# Story Hub - Flask Blog Application

A modern, feature-rich blog application built with Flask, featuring comprehensive content management, tagging system, and full-text search capabilities.

![Story Hub](static/uploads/sample1.jpg)

## 🌟 Features

### Content Management
- **Rich Text Editing**: Support for HTML formatting in posts
- **Image Uploads**: High-quality image support with automatic filename generation
- **Post Types**: Distinguish between Articles and Stories
- **Category System**: Organize articles by categories with dedicated pages
- **SEO-Friendly URLs**: Automatic slug generation for better search engine optimization
- **Excerpts**: Optional post summaries for better content preview

### Search & Discovery
- **Full-Text Search**: Search across post titles, content, and excerpts
- **Tagging System**: Comprehensive tagging with clickable tag navigation
- **Tag-Based Filtering**: Browse posts by specific tags
- **Popular Tags**: Discover trending topics and categories
- **Search Pagination**: Efficient pagination for search results

### Admin Features
- **Secure Authentication**: Session-based admin login system
- **Admin Dashboard**: Overview of post statistics and recent activity
- **Post Management**: Create, edit, delete, and feature posts
- **Category Management**: Create and manage article categories
- **Tag Management**: Organize and clean up tag system
- **Contact System**: Email configuration and message management
- **Featured Posts**: Highlight important content with prominent display
- **Bulk Operations**: Manage multiple posts efficiently

### User Experience
- **Responsive Design**: Mobile-first Bootstrap-based UI with Japanese-inspired theme
- **Featured Post Display**: Eye-catching hero section with overlay design
- **Contact Form**: Professional contact system with email integration
- **Pagination**: Clean navigation through content pages
- **Navigation Search**: Integrated search bar in the main navigation
- **Tag Clouds**: Visual tag browsing with post counts
- **Category Navigation**: Dropdown navigation for article categories

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Git (for cloning the repository)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/bschwebs/website_template.git
   cd website_template
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # macOS/Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   ```bash
   python init_db.py
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   - Open your browser and navigate to `http://127.0.0.1:5000`
   - Admin login: `http://127.0.0.1:5000/admin/login`
   - Default credentials: `admin` / `admin123`
   - Contact page: `http://127.0.0.1:5000/contact`

## 📁 Project Structure

```
story-hub/
├── routes/                   # Blueprint route modules
│   ├── __init__.py
│   ├── admin.py             # Admin dashboard and management
│   ├── auth.py              # Authentication routes
│   ├── main.py              # Main pages (home, stories, articles)
│   ├── posts.py             # Post CRUD operations
│   └── search.py            # Search and tag filtering
├── static/                  # Static assets
│   └── uploads/             # User-uploaded images
├── templates/               # Jinja2 templates
│   ├── admin/               # Admin interface templates
│   ├── search/              # Search and tag templates
│   ├── base.html            # Base template
│   ├── index.html           # Homepage
│   └── ...                  # Other page templates
├── app.py                   # Application factory and main entry point
├── config.py                # Configuration settings
├── content.db               # SQLite database (created after init)
├── forms.py                 # Flask-WTF form definitions
├── init_db.py               # Database initialization script
├── models.py                # Database models and operations
├── requirements.txt         # Python dependencies
└── utils.py                 # Helper functions and utilities
```

## 🗄️ Database Schema

The application uses SQLite with the following main tables:

### Posts Table
- `id` - Primary key
- `title` - Post title
- `content` - HTML content
- `excerpt` - Optional summary
- `image_filename` - Uploaded image reference
- `image_position_x/y` - Image positioning for display
- `post_type` - 'article' or 'story'
- `category_id` - Foreign key to categories (articles only)
- `slug` - SEO-friendly URL slug
- `featured` - Boolean for featured posts
- `created_at` / `updated_at` - Timestamps

### Categories Table
- `id` - Primary key
- `name` - Category display name
- `slug` - URL-friendly category identifier
- `description` - Category description

### Tags Table
- `id` - Primary key
- `name` - Tag display name
- `slug` - URL-friendly tag identifier

### Post_Tags Table (Many-to-Many)
- `post_id` - Foreign key to posts
- `tag_id` - Foreign key to tags

### Contact_Messages Table
- `id` - Primary key
- `name` - Sender name
- `email` - Sender email
- `subject` - Message subject
- `message` - Message content
- `created_at` - Timestamp

### Email_Config Table
- `id` - Primary key
- `smtp_server` - SMTP server address
- `smtp_port` - SMTP port number
- `smtp_username` - SMTP username
- `smtp_password` - SMTP password
- `from_email` - From email address
- `to_email` - Destination email address
- `use_tls` - TLS/SSL flag

### Admin_Users Table
- `id` - Primary key
- `username` - Admin username
- `password_hash` - Hashed password

## 🎨 Customization

### Styling
The application uses Bootstrap 5 for styling. Custom styles can be added to `templates/base.html`:

```css
<style>
    /* Add your custom CSS here */
    .custom-style {
        /* Your styles */
    }
</style>
```

### Configuration
Modify `config.py` to customize application settings:

```python
class Config:
    SECRET_KEY = 'your-secret-key'
    DATABASE = 'your-database.db'
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
```

### Contact System Setup
Configure email settings through the admin panel at `/admin/email-config`:

1. **SMTP Server**: Your email provider's SMTP server (e.g., `smtp.gmail.com`)
2. **Port**: Usually 587 for TLS or 465 for SSL
3. **Username/Password**: Your email credentials (use app passwords for Gmail)
4. **From/To Emails**: Configure sender and recipient addresses
5. **TLS/SSL**: Enable for secure email transmission

**Supported Email Providers:**
- Gmail: `smtp.gmail.com:587` (requires app password)
- Outlook: `smtp.outlook.com:587`
- Yahoo: `smtp.mail.yahoo.com:587`
- Custom SMTP servers

### Adding New Features
The modular architecture makes it easy to extend:

1. **New Routes**: Add blueprint files in the `routes/` directory
2. **New Models**: Extend the database models in `models.py`
3. **New Forms**: Add form classes to `forms.py`
4. **New Templates**: Create template files in the `templates/` directory

## 🔧 API Reference

### Key Models

#### PostModel
```python
# Get all posts with pagination
PostModel.get_all_posts_paginated(page, per_page)

# Search posts
PostModel.search_posts(query, page, per_page)

# Get posts by tag
PostModel.get_posts_by_tag(tag_slug, page, per_page)

# Manage tags
PostModel.add_tags_to_post(post_id, tag_list)
PostModel.get_post_tags(post_id)
```

#### TagModel
```python
# Get all tags with post counts
TagModel.get_all_tags()

# Get popular tags
TagModel.get_popular_tags(limit)

# Get tag by slug
TagModel.get_tag_by_slug(slug)
```

### Utility Functions
```python
# Generate SEO-friendly slugs
generate_unique_slug(title, post_id=None)

# Parse comma-separated tags
parse_tags(tag_string)

# File upload handling
save_uploaded_file(file, upload_folder)
```

## 🚀 Deployment

### Production Setup

1. **Environment Variables**
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=your-production-secret-key
   export DATABASE_URL=path-to-production-database
   ```

2. **Use a Production WSGI Server**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

3. **Configure Reverse Proxy** (Nginx example)
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
       
       location /static {
           alias /path/to/your/app/static;
       }
   }
   ```

### Docker Deployment
Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python init_db.py

EXPOSE 5000
CMD ["python", "app.py"]
```

## 🧪 Testing

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-flask

# Run tests
pytest tests/
```

### Manual Testing Checklist
- [ ] Admin login/logout functionality
- [ ] Post creation with tags and images
- [ ] Category management and article categorization
- [ ] Contact form submission and email sending
- [ ] Email configuration in admin panel
- [ ] Search functionality across different content
- [ ] Tag-based filtering
- [ ] Pagination on all list views
- [ ] Featured post display
- [ ] Responsive design on mobile devices

## 🔒 Security Considerations

### Default Security Features
- **CSRF Protection**: All forms protected with Flask-WTF
- **Session Security**: Secure session management
- **File Upload Validation**: Restricted file types and sizes
- **Input Sanitization**: Safe HTML rendering with Jinja2
- **Admin Authentication**: Session-based authentication

### Recommended Security Enhancements
1. **Change Default Admin Credentials**: Update the default admin password
2. **Use HTTPS**: Enable SSL/TLS in production
3. **Environment Variables**: Store secrets in environment variables
4. **Database Security**: Use proper database permissions
5. **Regular Updates**: Keep dependencies updated

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation for API changes
- Use meaningful commit messages

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

### Common Issues

**Q: Getting "No such table" errors?**
A: Run `python init_db.py` to initialize the database schema.

**Q: Images not uploading?**
A: Check that the `static/uploads/` directory exists and has write permissions.

**Q: Search not working?**
A: Ensure the database has been properly initialized with the latest schema.

### Getting Help
- Check the [Issues](https://github.com/bschwebs/website_template/issues) page
- Create a new issue with detailed information about your problem
- Include error messages, steps to reproduce, and your environment details

## 🚀 Roadmap

### Planned Features
- [ ] User authentication and multi-author support
- [ ] Comment system for posts
- [ ] RSS/Atom feed generation
- [ ] Advanced admin analytics
- [ ] Email notifications for new contact messages
- [ ] Social media integration
- [ ] Advanced text editor (WYSIWYG)
- [ ] Post scheduling
- [ ] SEO optimization tools
- [ ] Performance monitoring
- [ ] Contact form spam protection
- [ ] Newsletter subscription system

## 📊 Performance

### Optimization Features
- **Database Indexing**: Optimized queries for search and filtering
- **Pagination**: Efficient loading of large content sets
- **Image Optimization**: Proper image handling and serving
- **Template Caching**: Jinja2 template optimization
- **Static Asset Management**: Organized static file structure

### Monitoring
Consider implementing:
- Application performance monitoring (APM)
- Database query optimization
- Image compression and CDN integration
- Caching strategies (Redis/Memcached)

---

**Built with ❤️ using Flask, Bootstrap, and modern web technologies.**

For more information, visit the [project repository](https://github.com/bschwebs/website_template).