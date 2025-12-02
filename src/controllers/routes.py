from flask import Blueprint, render_template, redirect, url_for

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/<int:page_number>')
def home(page_number=None):
    if page_number:
        return render_template(f'public/landing/index{page_number}.html')
    return render_template('public/landing/index.html')

@main_bp.route('/about')
def about():
    return render_template('public/about/index.html')
