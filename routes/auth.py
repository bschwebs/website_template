"""
Authentication routes for the Story Hub application.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from models import AdminModel
from forms import LoginForm

auth = Blueprint('auth', __name__)


@auth.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page."""
    form = LoginForm()
    if form.validate_on_submit():
        admin = AdminModel.get_admin_by_username(form.username.data)
        
        if admin and check_password_hash(admin['password_hash'], form.password.data):
            session['admin_logged_in'] = True
            session['admin_username'] = admin['username']
            flash('Successfully logged in as admin.', 'success')
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('admin/login.html', form=form)


@auth.route('/admin/logout')
def admin_logout():
    """Admin logout."""
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))