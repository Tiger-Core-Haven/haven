from flask import Blueprint, jsonify, g
from app.auth.utils import token_required
from app.models import User

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
        return jsonify({'message': 'User created', 'role': 'client'})
    
    return jsonify({
        'message': 'User synced', 
        'uid': user.uid,
        'role': user.role
    })