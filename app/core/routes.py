from flask import Blueprint, render_template
from app.core import core_bp

@core_bp.route('/')
def index():
    return render_template('haven-app.html')

@core_bp.route('/privacy')
def privacy():
    return render_template('privacy.html')

@core_bp.route('/terms')
def terms():
    return render_template('terms.html')

@core_bp.route('/my-group')
def my_group():
    return render_template('my-group.html')
