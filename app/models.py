from app.extensions import db
from datetime import datetime

class User:
    collection_name = 'users'

    def __init__(self, uid, email, role='client'):
        self.uid = uid
        self.email = email
        self.role = role
        self.created_at = datetime.now()

    @staticmethod
    def get_by_id(uid):
        doc = db.collection(User.collection_name).document(uid).get()
        if doc.exists:
            data = doc.to_dict()
            return User(uid=uid, email=data.get('email'), role=data.get('role'))
        return None

    def save(self):
        """Syncs user data to Firestore"""
        db.collection(self.collection_name).document(self.uid).set({
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at
        }, merge=True)

class ChatSession:
    collection_name = 'sessions'

    @staticmethod
    def create(user_id):
        """Create a new chat session document"""
        new_ref = db.collection(ChatSession.collection_name).document()
        session_data = {
            'user_id': user_id,
            'started_at': datetime.now(),
            'messages': [],
            'extracted_data': {} # For storing slots like severity, duration
        }
        new_ref.set(session_data)
        return new_ref.id

    @staticmethod
    def add_message(session_id, message_data):
        """Append a message (dict) to the history"""
        ref = db.collection(ChatSession.collection_name).document(session_id)
        doc = ref.get()
        if doc.exists:
            current_messages = doc.to_dict().get('messages', [])
            current_messages.append(message_data)
            ref.update({'messages': current_messages})