import os
import logging
from flask import Blueprint, jsonify, g
from app.auth.utils import token_required
from app.models import User
from app.email.service import send_email

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger("haven.auth")

@auth_bp.route('/sync', methods=['POST'])
@token_required
def sync_user():
    """
    Called by Frontend after login to ensure User exists in Firestore.
    """
    uid = g.user_uid
    email = g.user_email
    display_name = getattr(g, "user_name", None)
    photo_url = getattr(g, "user_picture", None)
    
    user = User.get_by_id(uid)
    
    if not user:
        user = User(uid=uid, email=email, role='client', display_name=display_name, photo_url=photo_url)
        user.save()
        if email:
            display_name = display_name or email.split("@")[0]
            app_base_url = os.getenv("APP_BASE_URL", "http://localhost:5000")
            send_email(
                to_email=email,
                subject="welcome to haven",
                template_name="welcome.html",
                context={
                    "display_name": display_name,
                    "preheader": "you're all set — your journey starts here.",
                    "cta_url": app_base_url,
                    "cta_label": "continue your journey"
                },
                tags=[{"name": "type", "value": "welcome"}]
            )
        return jsonify({'message': 'User created', 'role': 'client'})

    if display_name or photo_url:
        user.display_name = display_name or user.display_name
        user.photo_url = photo_url or user.photo_url
        user.save()
    user.touch_last_login()

    logger.info("User already exists, skipping welcome email uid=%s", uid)
    return jsonify({
        'message': 'User synced', 
        'uid': user.uid,
        'role': user.role
    })
