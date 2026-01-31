from app.extensions import db
from datetime import datetime

class User:
    collection_name = 'users'

    def __init__(self, uid, email, role='client', display_name=None, photo_url=None):
        self.uid = uid
        self.email = email
        self.role = role
        self.display_name = display_name
        self.photo_url = photo_url
        self.created_at = datetime.now()

    @staticmethod
    def get_by_id(uid):
        doc = db.collection(User.collection_name).document(uid).get()
        if doc.exists:
            data = doc.to_dict()
            return User(
                uid=uid,
                email=data.get('email'),
                role=data.get('role', 'client'),
                display_name=data.get('display_name'),
                photo_url=data.get('photo_url')
            )
        return None

    def save(self):
        """Syncs user data to Firestore"""
        db.collection(self.collection_name).document(self.uid).set({
            'email': self.email,
            'role': self.role,
            'display_name': self.display_name,
            'photo_url': self.photo_url,
            'created_at': self.created_at
        }, merge=True)

    def touch_last_login(self):
        db.collection(self.collection_name).document(self.uid).set({
            'last_login_at': datetime.now()
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
