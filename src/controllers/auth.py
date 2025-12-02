from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from src.services.user_service import UserService

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


# Route for user login
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = UserService.login_user({**request.form})
        if user:
            # login successful
            from src.models.logbook import Logbook
            log_entry = Logbook.create({
                'entry': f'User logged in: {user.username} ({user.email})',
                'type': 'user_login',
                'reference_code': 'b4bf13e6',
                'severity': 'info',
                'user_id': user.id
            })
            session['user_token'] = log_entry.hash_key
            flash('Login successful!', 'success_login')
            return redirect(url_for('auth.dashboard'))

    return render_template('public/auth/login/index.html')


# Route for user registration
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_data = {**request.form}
        user = UserService.create_user(user_data)
        if user:
            # login the user
            from src.models.logbook import Logbook
            log_entry = Logbook.create({
                'entry': f'New user registered: {user.username} ({user.email})',
                'type': 'user_registration',
                'reference_code': 'af5a409f',
                'severity': 'info',
                'user_id': user.id
            })
            session['user_token'] = log_entry.hash_key
            flash('Registration successful! Please log in.', 'success_registration')
            return redirect(url_for('auth.dashboard'))

    return render_template('public/auth/register/index.html')


@auth_bp.route('/logout')
def logout():
    session.pop('user_token', None)
    flash('You have been logged out.', 'info_logout')
    return redirect(url_for('main.home'))


@auth_bp.route('/dashboard')
def dashboard():
    
    context = {
        'current_user': UserService.get_current_user(session.get('user_token'))
    }
    return render_template('private/users/dashboard/index.html', **context)