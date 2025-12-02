from flask import Blueprint, render_template, redirect, session, url_for
from src.services.user_service import UserService

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile')
def profile():
    context = {
        'current_user': UserService.get_current_user(session.get('user_token'))
    }
    return render_template('private/users/profile/index.html', **context)

@user_bp.route('/home')
def home():
    context = {
        'current_user': UserService.get_current_user(session.get('user_token'))
    }
    return render_template('private/users/home/index.html', **context)