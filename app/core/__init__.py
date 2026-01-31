from flask import Blueprint
core_bp = Blueprint("core", __name__, template_folder="core_templates", static_folder="core_static")
from app.core import routes