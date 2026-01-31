import os
import json
from datetime import datetime
from flask import request, jsonify, g
from app.auth.utils import token_required
from app.models import User, ChatSession

from app.ai.chat_engine import ChatbotEngine 
from app.ai.group_matcher import GroupMatcher, TherapistHandoff
from app.extensions import db
from app.ai import ai_bp
from app.email.service import send_email



active_bots = {}

def _get_session_doc(session_id):
    doc = db.collection('sessions').document(session_id).get()
    return doc if doc.exists else None

def _get_user_email_from_session(session_id):
    doc = _get_session_doc(session_id)
    if not doc:
        return None
    user_id = doc.to_dict().get('user_id')
    if not user_id:
        return None
    user = User.get_by_id(user_id)
    return user.email if user else None


def _get_or_create_bot(session_id):
    if session_id in active_bots:
        return active_bots[session_id]
    
    bot = ChatbotEngine()
    
    try:
        past_messages = ChatSession.get_messages(session_id) 
        for msg in past_messages:
            role = "user" if msg['role'] == 'user' else "assistant"
            bot.conversation_history.append({
                "role": role,
                "content": [{"text": msg['content']}]
            })
    except Exception as e:
        print(f"Could not rehydrate history: {e}")

    active_bots[session_id] = bot
    return bot

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
    
    chatbot = _get_or_create_bot(session_id)
    
    response = chatbot.generate_response(user_msg)
    
    # save to db
    ChatSession.add_message(session_id, {'role': 'user', 'content': user_msg})
    ChatSession.add_message(session_id, {'role': 'bot', 'content': response['message']})
    
    # check for extracted data
    if response.get('ready_for_next_phase') and response.get('extracted_data'):
        # Save the extraction to the DB immediately
        db.collection('sessions').document(session_id).update({
            'extracted_data': response['extracted_data'],
            'status': 'ready_to_match'
        })

    return jsonify(response)

@ai_bp.route('/match', methods=['POST'])
@token_required
def match_group():
    data = request.json
    session_id = data.get('session_id')
    
    if not session_id:
        return jsonify({'error': 'session_id is required'}), 400
    
    doc = _get_session_doc(session_id)
    if not doc:
        return jsonify({'error': 'Invalid session'}), 400
        
    session_data = doc.to_dict()
    user_data = session_data.get('extracted_data', {})

    if not user_data and session_id in active_bots:
        pass

    if not user_data:
        return jsonify({'error': 'No clinical data extracted yet. Chat more.'}), 400

    group, insight_object = GroupMatcher.match_to_group(user_data)

    # Convert Pydantic object to dict for JSON serialization
    insight_dict = insight_object.model_dump()

    # Send Email
    email = _get_user_email_from_session(session_id)
    if email:
        app_base_url = os.getenv("APP_BASE_URL", "http://localhost:5000")
        send_email(
            to_email=email,
            subject="your haven group is ready",
            template_name="group_match.html",
            context={
                "preheader": f"your match is in: {group['name']}",
                "group_name": group["name"],
                "group_focus": group["focus"],
                "group_capacity": group["capacity"],
                "group_description": group["description"],
                "group_emoji": group.get("emoji", ""),
                
                # Updated to use the AI-generated insight
                "insight_title": insight_dict["title"],
                "insight_description": insight_dict["description"],
                
                "cta_url": f"{app_base_url}/dashboard",
                "cta_label": "see your match"
            },
            tags=[{"name": "type", "value": "group_match"}]
        )
    
    return jsonify({'group': group, 'insight': insight_dict})

@ai_bp.route('/assessment/bubble', methods=['POST'])
@token_required
def bubble_assessment():
    data = request.json
    session_id = data.get('session_id')
    selected_bubbles = data.get('selected_bubbles', [])

    if not session_id:
        return jsonify({'error': 'session_id is required'}), 400

    # Update DB
    db.collection('sessions').document(session_id).set({
        'stressors': selected_bubbles
    }, merge=True)

    return jsonify({'status': 'success', 'message': 'Assessment data recorded'})

@ai_bp.route('/assessment/mood', methods=['POST'])
@token_required
def mood_assessment():
    data = request.json
    session_id = data.get('session_id')
    mood_level = data.get('mood_level', 50)

    if not session_id:
        return jsonify({'error': 'session_id is required'}), 400

    # Update DB
    db.collection('sessions').document(session_id).set({
        'mood_level': mood_level
    }, merge=True)

    return jsonify({'status': 'success', 'message': 'Mood data recorded'})

@ai_bp.route('/scheduling/available-slots', methods=['GET'])
@token_required
def available_slots():
    # In a real app, this would query a Calendar API
    slots = [
        {'day': 'Tuesday', 'time': '6:00 PM', 'available': True},
        {'day': 'Wednesday', 'time': '7:00 PM', 'available': True},
        {'day': 'Thursday', 'time': '6:00 PM', 'available': True},
        {'day': 'Saturday', 'time': '10:00 AM', 'available': True}
    ]
    return jsonify({'slots': slots})

@ai_bp.route('/booking/confirm', methods=['POST'])
@token_required
def confirm_booking():
    data = request.json
    session_id = data.get('session_id')
    time_slot = data.get('time_slot')
    group_name = data.get('group_name', 'Your Group')
    price = data.get('price')

    if not session_id or not time_slot:
        return jsonify({'error': 'session_id and time_slot are required'}), 400

    booking_ref = db.collection('bookings').document()
    booking_ref.set({
        'session_id': session_id,
        'user_id': g.user_uid,
        'time_slot': time_slot,
        'group_name': group_name,
        'price': price,
        'created_at': datetime.utcnow().isoformat()
    })

    session_date = ""
    session_time = ""
    if isinstance(time_slot, dict):
        session_date = time_slot.get("day", "")
        session_time = time_slot.get("time", "")
    elif isinstance(time_slot, str):
        session_date = time_slot

    email = _get_user_email_from_session(session_id)
    if email:
        app_base_url = os.getenv("APP_BASE_URL", "http://localhost:5000")
        send_email(
            to_email=email,
            subject="your haven session is confirmed",
            template_name="booking_confirmed.html",
            context={
                "preheader": "your session is booked.",
                "group_name": group_name,
                "session_date": session_date or "scheduled session",
                "session_time": session_time,
                "price": price,
                "booking_id": booking_ref.id,
                "cta_url": f"{app_base_url}/session/{booking_ref.id}",
                "cta_label": "view your session"
            },
            tags=[{"name": "type", "value": "booking_confirmed"}]
        )

    return jsonify({
        'status': 'success',
        'booking_id': booking_ref.id,
        'message': 'Booking confirmed'
    })

@ai_bp.route('/therapist/dashboard/<group_id>', methods=['GET'])
@token_required
def therapist_dashboard(group_id):
    # This is currently mock data. 
    # In production, query db.collection('bookings').where('group_id', '==', group_id)
    participants = [
        {
            'name': 'Mani',
            'age': 22,
            'occupation': 'Student',
            'primary_complaint': 'work_stress',
            'duration': 'recent',
            'severity': 'high',
            'triggers': ['Failure', 'Not meeting expectations'],
            'therapeutic_needs': 'Validation on hard work, permission to rest'
        },
        {
            'name': 'Sarah',
            'age': 26,
            'occupation': 'Designer',
            'primary_complaint': 'anxiety',
            'duration': 'chronic',
            'severity': 'moderate',
            'triggers': ['Comparison with peers'],
            'therapeutic_needs': 'Confidence building, perspective on growth'
        },
        {
            'name': 'Alex',
            'age': 24,
            'occupation': 'Engineer',
            'primary_complaint': 'burnout',
            'duration': 'recent',
            'severity': 'high',
            'triggers': ['Always-on work culture'],
            'therapeutic_needs': 'Boundary setting strategies, work-life balance'
        }
    ]

    group_def = GroupMatcher.ARCHETYPE_GROUPS.get(group_id, GroupMatcher.ARCHETYPE_GROUPS.get('navigators'))
    
    # Generate the brief using the LLM (TherapistHandoff class)
    # This might take 3-5 seconds, so in production, this should be an async job.
    brief = TherapistHandoff.generate_group_brief(group_def, participants)
    
    return jsonify(brief)

@ai_bp.route('/therapist/download-brief/<group_id>', methods=['GET'])
@token_required
def download_brief(group_id):
    # This would generate the PDF using a library like WeasyPrint or ReportLab
    return jsonify({
        'status': 'success',
        'message': 'PDF generation would happen here',
        'url': f'/downloads/brief_{group_id}.pdf'
    })