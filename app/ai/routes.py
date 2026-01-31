from flask import request, jsonify, g
from app.auth.utils import token_required
from app.models import User, ChatSession
from app.ai.chat_engine import ChatbotEngine
from app.ai.group_matcher import GroupMatcher, TherapistHandoff
from app.extensions import db
from app.ai import ai_bp


active_bots = {}

@ai_bp.route('/start', methods=['POST'])
@token_required
def start_chat():
    uid = g.user_uid

    session_id = ChatSession.create(uid)

    active_bots[session_id] = ChatbotEngine()
    
    return jsonify({
        'session_id': session_id,
        'message': "hey there. the world can be a lot sometimes. how are you holding up today?"
    })

@ai_bp.route('/message', methods=['POST'])
@token_required
def chat_message():
    data = request.json
    session_id = data.get('session_id')
    user_msg = data.get('message')
    turn_count = data.get('turn_count', 1)
    
    if session_id not in active_bots:

        active_bots[session_id] = ChatbotEngine()
    
    chatbot = active_bots[session_id]
    

    response = chatbot.generate_response(user_msg, turn_count)
    

    ChatSession.add_message(session_id, {'role': 'user', 'content': user_msg})
    ChatSession.add_message(session_id, {'role': 'bot', 'content': response['message']})
    

    if 'extracted_data' in response:

        db.collection('sessions').document(session_id).update({
            'extracted_data': response['extracted_data']
        })

    return jsonify(response)

@ai_bp.route('/match', methods=['POST'])
@token_required
def match_group():
    data = request.json
    session_id = data.get('session_id')
    

    if session_id in active_bots:
        user_data = active_bots[session_id].slots
    else:

        doc = db.collection('sessions').document(session_id).get()
        user_data = doc.to_dict().get('extracted_data', {})

    group = GroupMatcher.match_to_group(user_data)
    insight = GroupMatcher.generate_insight_card(user_data, group)
    
    return jsonify({'group': group, 'insight': insight})