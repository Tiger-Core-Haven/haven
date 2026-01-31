from functools import wraps
from flask import request, jsonify, g
from firebase_admin import auth

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # check for auth header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Authorization header is missing'}), 401

        try:
            token = auth_header.split(" ")[1]
            
            # verify with google
            decoded_token = auth.verify_id_token(token)
            
            #
            g.user_uid = decoded_token['uid']
            g.user_email = decoded_token.get('email')
            
        except Exception as e:
            return jsonify({'error': 'Invalid or expired token'}), 403

        return f(*args, **kwargs)
    return decorated