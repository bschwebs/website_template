# Flask Story & Article Publishing Website

A complete website template for publishing short stories and articles with images, built using Python Flask, SQLite3, and Bootstrap.

## Features

- **Content Management**: Create, read, update, and delete stories and articles
- **Image Upload**: Support for featured images with automatic file handling
- **Content Types**: Separate sections for stories and articles
- **Responsive Design**: Bootstrap-based responsive UI that works on all devices
- **Database**: SQLite3 database for easy deployment and management
- **Search & Navigation**: Easy navigation between different content types

## Project Structure

```
story_website/
├── app.py                 # Main Flask application
├── content.db            # SQLite database (created automatically)
├── requirements.txt      # Python dependencies
├── static/
│   └── uploads/          # Directory for uploaded images
└── templates/
    ├── base.html         # Base template with navigation
    ├── index.html        # Homepage
    ├── stories.html      # Stories listing page
    ├── articles.html     # Articles listing page
    ├── post.html         # Individual post view
    ├── create.html       # Create new post form
    └── edit.html         # Edit existing post form
```

## Installation & Setup

### 1. Create Virtual Environment

```bash
# Create virtual environment
python -m venv story_website
cd story_website

# Activate virtual environment
# On Windows:
Scripts\activate
# On macOS/Linux:
source bin/activate
```

### 2. Install Dependencies

Create a `requirements.txt` file:

```txt
Flask==3.0.0
Werkzeug==3.0.1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Create Directory Structure

```bash
mkdir templates static static/uploads
```

### 4. Add the Files

- Copy the main Flask application code to `app.py`
- Copy all HTML templates to the `templates/` directory
- Make sure to create each template file separately (base.html, index.html, etc.)

### 5. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage

### Creating Content

1. Click "Create Post" in the navigation
2. Choose between "Story" or "Article"
3. Fill in the title, optional excerpt, and content
4. Optionally upload a featured image
5. Click "Publish Post"

### Managing Content

- **View Posts**: Browse all posts on the homepage, or filter by Stories/Articles
- **Edit Posts**: Click the post title to view, then use the dropdown menu to edit
- **Delete Posts**: Use the dropdown menu on individual posts to delete (with confirmation)

### Image Management

- Supported formats: PNG, JPG, JPEG, GIF, WebP
- Maximum file size: 16MB
- Images are automatically renamed with UUIDs to prevent conflicts
- Old images are automatically deleted when posts are updated or removed

## Database Schema

The application uses a simple SQLite database with one main table:

```sql
CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    excerpt TEXT,
    image_filename TEXT,
    post_type TEXT NOT NULL DEFAULT 'article',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Customization

### Styling
- The application uses Bootstrap 5 for styling
- Custom CSS is included in the base template
- You can modify the styles in the `<style>` section of `base.html`

### Adding Features
- **User Authentication**: Add Flask-Login for user management
- **Categories/Tags**: Extend the database schema to include categories
- **Comments**: Add a comments system with additional tables
- **Search**: Implement full-text search functionality
- **Rich Text Editor**: Replace textarea with a WYSIWYG editor like TinyMCE

### Configuration
Important settings in `app.py`:
- `SECRET_KEY`: Change this to a secure random string in production
- `UPLOAD_FOLDER`: Directory for uploaded images
- `MAX_CONTENT_LENGTH`: Maximum file upload size

## Security Considerations

For production deployment:

1. **Secret Key**: Use a secure, random secret key
2. **File Uploads**: The application includes basic file type validation
3. **Input Validation**: Basic validation is included, consider adding more robust sanitization
4. **Database**: Consider using PostgreSQL or MySQL for production
5. **Authentication**: Add user authentication for admin functionality

## Deployment

### Local Development
```bash
python app.py
```

### Production Deployment Options

#### Using Gunicorn (Recommended)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

#### Using Docker
Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

#### Platform-as-a-Service
This application can be easily deployed to:
- Heroku
- Railway
- DigitalOcean App Platform
- AWS Elastic Beanstalk

## Sample Content

To test the application, try creating:

**Sample Story:**
- Title: "The Last Library"
- Type: Story
- Excerpt: "In a world where books are forbidden, one librarian holds the key to humanity's past."

**Sample Article:**
- Title: "The Art of Creative Writing"
- Type: Article
- Excerpt: "Exploring the fundamental techniques that make stories come alive."

## Troubleshooting

### Common Issues

1. **Images not uploading**: Check that the `static/uploads` directory exists and has write permissions
2. **Database errors**: Ensure SQLite is properly installed and the app has write permissions
3. **Template not found**: Verify all template files are in the `templates/` directory
4. **Static files not loading**: Check that the `static/` directory structure is correct

### Debug Mode
The application runs in debug mode by default. For production, change:
```python
app.run(debug=False)
```

## License

This template is provided as-is for educational and project use. Feel free to modify and extend it for your needs.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify your file structure matches the expected layout
3. Ensure all dependencies are properly installed
4. Check the Flask and SQLite documentation for advanced features