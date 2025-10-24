from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
from src.logic.user_logic import UserLogic, RoleLogic

user_bp = Blueprint('user', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('user.login'))
        return f(*args, **kwargs)
    return decorated_function

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Email and password are required', 'error')
            return render_template('public/login_reg/login/index.html')
        
        try:
            # Authenticate user
            user = UserLogic.authenticate_user(email, password)
            
            if user:
                # Set session data
                session['user_id'] = user.id
                session['user_email'] = user.email
                session['user_type'] = user.user_type
                session['user_name'] = user.full_name
                
                flash(f'Welcome back, {user.first_name}!', 'success')
                
                # Redirect based on user type
                if user.user_type == 'teacher':
                    return redirect(url_for('user.teacher_dashboard'))
                elif user.user_type == 'student':
                    return redirect(url_for('user.student_dashboard'))
                else:
                    return redirect(url_for('user.dashboard'))
            else:
                flash('Invalid email or password', 'error')
                
        except Exception as e:
            flash('Login failed. Please try again.', 'error')
    
    return render_template('public/login_reg/login/index.html')

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        errors = {}
        
        if not first_name:
            errors['first_name'] = 'First name is required'
        elif len(first_name) < 2:
            errors['first_name'] = 'First name must be at least 2 characters'
            
        if not last_name:
            errors['last_name'] = 'Last name is required'
        elif len(last_name) < 2:
            errors['last_name'] = 'Last name must be at least 2 characters'
            
        if not email:
            errors['email'] = 'Email is required'
        elif '@' not in email or '.' not in email:
            errors['email'] = 'Please enter a valid email address'
            
        if not password:
            errors['password'] = 'Password is required'
        elif len(password) < 8:
            errors['password'] = 'Password must be at least 8 characters'
            
        if password != confirm_password:
            errors['confirm_password'] = 'Passwords do not match'
            
        if not request.form.get('terms'):
            errors['terms'] = 'You must agree to the Terms of Service'
        
        # If there are validation errors, return to form
        if errors:
            return render_template('public/login_reg/registration/index.html', 
                                 errors=errors)
        
        try:
            # Create user
            user_data = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'password': password,
                'default_role': 'user'
            }
            
            user = UserLogic.create_user(user_data, 'user')
            
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('user.login'))
            
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('public/login_reg/registration/index.html', errors={'general': str(e)})
        except Exception as e:
            flash('Registration failed. Please try again.', 'error')
            return render_template('public/login_reg/registration/index.html', errors={'general': 'Registration failed'})
    
    return render_template('public/login_reg/registration/index.html')

@user_bp.route('/dashboard')
@login_required
def dashboard():
    """General dashboard - redirects to specific dashboard based on user type."""
    user = UserLogic.get_user_by_id(session['user_id'])
    if not user:
        flash('Session expired. Please log in again.', 'error')
        return redirect(url_for('user.login'))
    
    if user.user_type == 'teacher':
        return redirect(url_for('user.teacher_dashboard'))
    elif user.user_type == 'student':
        return redirect(url_for('user.student_dashboard'))
    else:
        return render_template('private/dashboard/index.html', user=user)

@user_bp.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    """Teacher-specific dashboard."""
    user = UserLogic.get_user_by_id(session['user_id'])
    if not user or user.user_type != 'teacher':
        flash('Access denied. Teacher account required.', 'error')
        return redirect(url_for('user.login'))
    
    return render_template('private/teacher/dashboard/index.html', user=user)

@user_bp.route('/student/dashboard')
@login_required
def student_dashboard():
    """Student-specific dashboard."""
    user = UserLogic.get_user_by_id(session['user_id'])
    if not user or user.user_type != 'student':
        flash('Access denied. Student account required.', 'error')
        return redirect(url_for('user.login'))
    
    return render_template('private/student/dashboard/index.html', user=user)

@user_bp.route('/debug-user')
@login_required
def debug_user():
    """Debug route to check user data."""
    user = UserLogic.get_user_by_id(session['user_id'])
    debug_info = {
        'session_data': {
            'user_id': session.get('user_id'),
            'user_email': session.get('user_email'),
            'user_type': session.get('user_type'),
            'user_name': session.get('user_name')
        },
        'user_data': user.to_dict() if user else None,
        'user_roles': user.get_role_names() if user else [],
        'has_teacher_role': user.has_role('teacher') if user else False,
        'user_type_check': user.user_type if user else None
    }
    return f"<pre>{debug_info}</pre>"


@user_bp.route('/logout')
def logout():
    """Log out the current user."""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))


# forgot password and reset password routes can be added here in the future
@user_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        # TODO: Add password reset logic here
        flash('Password reset instructions sent to your email')
        return redirect(url_for('user.login'))
    return render_template('public/login_reg/forgot_password/index.html')

@user_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'POST':
        new_password = request.form['password']
        # TODO: Add password reset logic here
        flash('Your password has been reset successfully')
        return redirect(url_for('user.login'))
    return render_template('public/login_reg/reset_password/index.html', token=token)