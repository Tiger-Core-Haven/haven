from flask import Blueprint, render_template
from app.core import core_bp

@core_bp.route('/')
def index():
    return render_template('haven-app.html')