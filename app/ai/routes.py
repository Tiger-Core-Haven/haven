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

def _summarize_mood(mood_level):
    if mood_level is None:
        return "No mood data yet"
    if mood_level < 33:
        return "Low energy, heavy mood"
    if mood_level < 66:
        return "Mixed energy, thoughtful"
    return "Bright energy, hopeful"

def _collect_themes(sessions):
    counts = {}
    for s in sessions:
        for item in s.get('stressors', []) or []:
            counts[item] = counts.get(item, 0) + 1
    top = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:3]
    return [name for name, _ in top]


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
    
    # 2. Convert Pydantic object to Dict for JSON serialization
    insight = insight_object.model_dump()

    # 3. Send Email
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
                
                # Updated fields from AI insight
                "insight_title": insight["title"],
                "insight_description": insight["description"],
                
                "cta_url": f"{app_base_url}/dashboard",
                "cta_label": "see your match"
            },
            tags=[{"name": "type", "value": "group_match"}]
        )
    
    return jsonify({'group': group, 'insight': insight})

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
        'group_id': data.get('group_id'),
        'price': price,
        'created_at': datetime.utcnow().isoformat()
    })

    db.collection('sessions').document(session_id).set({
        'booking_id': booking_ref.id,
        'booking_time_slot': time_slot,
        'booking_created_at': datetime.utcnow().isoformat(),
        'matched_group_name': group_name,
        'matched_group_id': data.get('group_id')
    }, merge=True)

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
    user = User.get_by_id(g.user_uid)
    if not user or user.role != 'therapist':
        return jsonify({'error': 'Forbidden'}), 403

    sessions_query = db.collection('sessions').where('matched_group_id', '==', group_id).stream()
    sessions = []
    participants = []
    for doc in sessions_query:
        data = doc.to_dict()
        data['id'] = doc.id
        sessions.append(data)

        user = User.get_by_id(data.get('user_id')) if data.get('user_id') else None
        extracted = data.get('extracted_data', {}) or {}
        participants.append({
            'name': getattr(user, 'display_name', None) or (user.email.split("@")[0] if user and user.email else "Member"),
            'email': user.email if user else None,
            'primary_concern': extracted.get('primary_complaint') or 'General wellness',
            'duration': extracted.get('duration') or 'Unknown',
            'severity': extracted.get('severity') or 'Moderate',
            'stressors': data.get('stressors', []),
            'mood_level': data.get('mood_level'),
            'conversation_summary': extracted.get('goal') or ''
        })

    group_def = GroupMatcher.ARCHETYPE_GROUPS.get(group_id, GroupMatcher.ARCHETYPE_GROUPS.get('navigators'))
    group_def = dict(group_def or {})
    group_def['id'] = group_id

    moods = [p.get('mood_level') for p in participants if p.get('mood_level') is not None]
    avg_mood = round(sum(moods) / len(moods)) if moods else None
    mood_summary = _summarize_mood(avg_mood)
    themes = _collect_themes(sessions)

    brief = TherapistHandoff.generate_group_brief(group_def, participants)
    brief.update({
        'session_count': len(sessions),
        'themes': themes,
        'average_mood': avg_mood,
        'mood_summary': mood_summary
    })
    return jsonify(brief)

@ai_bp.route('/therapist/download-brief/<group_id>', methods=['GET'])
@token_required
def download_brief(group_id):
    user = User.get_by_id(g.user_uid)
    if not user or user.role != 'therapist':
        return jsonify({'error': 'Forbidden'}), 403
    # This would generate the PDF using a library like WeasyPrint or ReportLab
    return jsonify({
        'status': 'success',
        'message': 'PDF generation would happen here',
        'url': f'/downloads/brief_{group_id}.pdf'
    })
