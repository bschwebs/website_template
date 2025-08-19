# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Core Application Commands
- **Start development server**: `python app.py` (runs on http://127.0.0.1:5000)
- **Initialize database**: Run `python app.py` on first start (auto-initializes via `init_db()`)
- **Install dependencies**: `pip install -r requirements.txt`
- **Create virtual environment**: `python -m venv .venv` then activate with `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (macOS/Linux)

### Testing Commands
- **Run Playwright tests**: `npx playwright test`
- **Install Playwright browsers**: `npx playwright install`
- **View test report**: `npx playwright show-report`
- **Run Python tests**: `pytest tests/` (if pytest tests exist)

### Database Operations
- **Database file**: `content.db` (SQLite)
- **Initialize/reset database**: Delete `content.db` and restart application
- **Fix database issues**: Run `python fix_database.py` if it exists

## Architecture Overview

### Application Structure
This is a **Flask-based blog application** with a modular blueprint architecture:

- **Main entry point**: `app.py` - Application factory pattern with blueprint registration
- **Configuration**: `config.py` - Environment-based config using python-dotenv
- **Database**: SQLite with custom model layer in `models.py` (no ORM)
- **Routes**: Modular blueprints in `routes/` directory
- **Templates**: Jinja2 templates in `templates/` with admin sub-directory
- **Static assets**: `static/` with CSS, JS, and user uploads

### Key Components

#### Blueprint Architecture
- `routes/main.py` - Homepage, stories, articles listing
- `routes/posts.py` - CRUD operations for posts
- `routes/admin.py` - Admin dashboard and management features
- `routes/auth.py` - Authentication (admin login/logout)
- `routes/search.py` - Search and tag filtering
- `routes/seo.py` - SEO-related routes

#### Database Layer
- **No ORM used** - Direct SQLite queries with sqlite3
- **Models**: Custom model classes in `models.py` with static methods
- **Key tables**: posts, categories, tags, post_tags, contact_messages, email_config, admin_users
- **Connection handling**: Flask's `g` object for request-scoped connections

#### Content Management
- **Post types**: Articles (with categories) and Stories
- **Rich features**: Image uploads, excerpts, SEO slugs, featured posts
- **Tagging system**: Many-to-many relationship with tag management
- **Category system**: For articles only, with color-coded display

#### Template System
- **Base template**: `templates/base.html` with Bootstrap 5
- **Admin interface**: Separate admin templates in `templates/admin/`
- **Custom filters**: Date formatting, image positioning, content truncation
- **Template globals**: Utility functions for reading time, tag management

### Technology Stack
- **Backend**: Flask 3.0 with Flask-WTF for forms and CSRF protection
- **Database**: SQLite with direct SQL queries
- **Frontend**: Bootstrap 5, custom CSS, vanilla JavaScript
- **Forms**: WTForms with server-side validation
- **File uploads**: Custom handling in `static/uploads/`
- **Testing**: Playwright for E2E testing
- **Utilities**: python-slugify, email-validator, python-dotenv

### Important Implementation Details

#### Admin System
- **Authentication**: Session-based with password hashing
- **Default credentials**: admin/admin123 (change via `/admin/change-password`)
- **Features**: Dashboard, post management, category/tag management, email config

#### Search and Navigation
- **Full-text search**: Searches titles, content, and excerpts
- **Tag system**: Tag-based filtering with popular tags display
- **Pagination**: Custom pagination for posts and search results
- **SEO**: Automatic slug generation for posts and categories

#### File Management
- **Upload handling**: Images stored in `static/uploads/` with UUID filenames
- **Image positioning**: Custom CSS background-position support
- **File validation**: Size limits and type restrictions

#### Content Features
- **Featured posts**: Hero display on homepage with overlay
- **Reading time**: Calculated based on word count
- **Content truncation**: Smart truncation preserving HTML
- **Rich content**: HTML support in post content

### Development Patterns

#### Form Handling
- All forms use Flask-WTF with CSRF protection
- Server-side validation with custom validators
- Flash messages for user feedback

#### Database Patterns
- Request-scoped connections via `get_db()`
- Row factory for dict-like access
- Manual SQL with parameterized queries
- Transaction handling for data consistency

#### Template Patterns
- Extensive use of template inheritance
- Custom filters for content formatting
- Template globals for utility functions
- Bootstrap classes with custom theme

#### Security Measures
- CSRF protection on all forms
- Password hashing with Werkzeug
- File upload restrictions
- Input sanitization via Jinja2 autoescaping

### Admin Access
- **Login URL**: `/admin/login`
- **Dashboard**: `/admin/dashboard` 
- **Default credentials**: admin/admin123 (should be changed immediately)
- **Password change**: Available in admin interface

### Contact System
- **Contact form**: `/contact` with email integration
- **Email configuration**: Managed through admin panel at `/admin/email-config`
- **Supported providers**: Gmail, Outlook, Yahoo, custom SMTP

### Recent Enhancements (v1.1.0)

#### UI/UX Improvements
- **Typography System**: Enhanced line-heights, spacing, and content width optimization
- **Recently Viewed Sidebar**: Universal tracking and display across all non-admin pages
- **Mobile Navigation**: Optimized height (<60px) and touch targets (44px minimum)
- **Loading Animations**: Skeleton screens, intersection observers, and smooth transitions
- **Responsive Design**: Improved spacing, padding, and breakpoint handling

#### Advanced Features
- **Instant Search**: Live suggestions with keyboard navigation
- **AJAX Pagination**: Seamless page transitions without refreshes
- **Enhanced Cards**: Improved hover effects, category colors, reading time
- **Accessibility**: WCAG AA compliant contrast ratios and touch targets
- **Performance**: Optimized image loading, content width, and responsive layouts

#### CSS Architecture
- **Design Tokens**: CSS custom properties for consistent theming
- **Component System**: Modular styling with BEM-like methodology
- **Responsive Utilities**: Mobile-first approach with progressive enhancement
- **Animation Library**: Keyframes, transitions, and intersection observer integration

This application follows Flask best practices with a clean separation of concerns, modern UI/UX patterns, and modular architecture suitable for content management and blogging.