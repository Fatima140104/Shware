from flask import render_template, session, redirect, url_for, flash
from app.dashboard import dashboard_bp

@dashboard_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('auth.login'))
    return render_template('dashboard.html')