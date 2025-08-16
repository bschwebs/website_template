# Project Documentation

This document provides instructions for setting up, running, and testing the Flask Story Publishing Website.

## Overview

This is a simple Flask application that allows users to create, view, edit, and delete articles and stories. It uses a SQLite database to store the content and allows for image uploads.

## Technologies Used

-   **Backend**: Flask
-   **Database**: SQLite
-e   **Frontend**: Bootstrap 5, Jinja2
-   **Testing**: Pytest, Pytest-Flask
-   **Dependency Management**: pip, requirements.txt

## Setup and Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables**:
    Create a `.env` file in the root of the project and add the following variables:
    ```
    FLASK_ENV=development
    SECRET_KEY=a_very_secret_key_that_is_long_and_random
    DATABASE_URL=content.db
    ```
    **Note**: The `SECRET_KEY` should be a long, random string.

5.  **Initialize the database**:
    To create the database and populate it with sample data, run:
    ```bash
    python init_db.py --recreate
    ```

## Running the Application

To run the application in development mode, use the following command:
```bash
flask run
```
The application will be available at `http://127.0.0.1:5000`.

## Running Tests

To run the test suite, use the following command:
```bash
pytest
```
This will discover and run all tests in the `tests/` directory.
