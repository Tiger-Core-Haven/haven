import os
from flask import Blueprint, jsonify, g
from app.auth.utils import token_required
from app.models import User
from app.email.service import send_email

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/sync', methods=['POST'])
@token_required
def sync_user():
    """
    Called by Frontend after login to ensure User exists in Firestore.
    """
    uid = g.user_uid
    email = g.user_email
    
    user = User.get_by_id(uid)
    
    if not user:
        user = User(uid=uid, email=email, role='client')
        user.save()
        if email:
            display_name = email.split("@")[0]
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
    
    return jsonify({
        'message': 'User synced', 
        'uid': user.uid,
        'role': user.role
    })
