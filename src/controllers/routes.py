from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('public/landing/index.html')

@main_bp.route('/about')
def about():
    return render_template('public/about/index.html')