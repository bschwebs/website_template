import pytest

def test_index(client):
    """Test the index page."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Story & Article Hub' in response.data

def test_create_post(client):
    """Test creating a post."""
    response = client.post('/create', data={
        'title': 'Test Title',
        'content': 'Test Content',
        'excerpt': 'Test Excerpt',
        'post_type': 'article'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Post created successfully!' in response.data
    assert b'Test Title' in response.data

def test_xss_vulnerability(client):
    """Test for XSS vulnerability."""
    xss_payload = '<script>alert("XSS")</script>'
    client.post('/create', data={
        'title': 'XSS Test',
        'content': xss_payload,
        'excerpt': 'XSS Excerpt',
        'post_type': 'article'
    }, follow_redirects=True)

    # The post should be the first one on the index page
    response = client.get('/')
    # find the post id from the href
    import re
    match = re.search(r'/post/(\d+)', response.data.decode('utf-8'))
    assert match is not None
    post_id = match.group(1)

    response = client.get(f'/post/{post_id}')
    assert response.status_code == 200
    assert b'<script>alert("XSS")</script>' not in response.data
    assert b'&lt;script&gt;alert(&#34;XSS&#34;)&lt;/script&gt;' in response.data
