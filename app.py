"""
Haven - AI-Orchestrated Group Therapy Matching System
Backend API with Flask and AI Integration
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
from datetime import datetime, timedelta
import random

app = Flask(__name__)
CORS(app)

# =====================================================
# AI CHATBOT SYSTEM WITH SLOT FILLING
# =====================================================

class ChatbotEngine:
    """
    Warm, empathetic chatbot that uses slot-filling strategy
    to understand user's mental health concerns
    """
    
    def __init__(self):
        self.slots = {
            'primary_complaint': None,  # What's wrong?
            'duration': None,            # How long?
            'severity': None,            # 1-10?
            'goal': None                 # Vent or fix?
        }
        self.confidence_scores = {
            'primary_complaint': 0,
            'duration': 0,
            'severity': 0,
            'goal': 0
        }
        self.conversation_history = []
        
    def get_system_prompt(self):
        """System prompt that enforces warm, non-robotic tone"""
        return """You are a warm, empathetic friend helping someone through a tough time.

RULES:
1. NO clinical jargon. Never use: "symptoms", "diagnosis", "disorder"
   USE: "feelings", "challenges", "heavy days"
2. Use lowercase for warmth: "hey, tell me more" not "Please elaborate"
3. ALWAYS validate before asking: 
   "that sounds incredibly draining. i'm sorry you're dealing with that. has it been going on for a while?"
4. Keep responses SHORT (2-3 sentences max)
5. You are NOT a doctor. You're a supportive friend.
6. Your goal: gently discover their struggle through conversation

Extract information for these slots:
- primary_complaint: What's bothering them? (anxiety, stress, grief, burnout, relationships)
- duration: How long has this been happening?
- severity: How bad is it? (1-10 scale or descriptive)
- goal: Do they want to vent or actively fix this?

Be natural. Be human. Be kind."""

    def analyze_message(self, user_message):
        """
        Analyze user message for slot filling
        In production, this would call OpenAI/HuggingFace API
        """
        message_lower = user_message.lower()
        
        # Extract primary complaint
        if any(word in message_lower for word in ['anxious', 'anxiety', 'worried', 'nervous']):
            self.slots['primary_complaint'] = 'anxiety'
            self.confidence_scores['primary_complaint'] = 0.8
        elif any(word in message_lower for word in ['stressed', 'pressure', 'overwhelmed', 'busy']):
            self.slots['primary_complaint'] = 'stress'
            self.confidence_scores['primary_complaint'] = 0.8
        elif any(word in message_lower for word in ['sad', 'depressed', 'down', 'empty']):
            self.slots['primary_complaint'] = 'depression'
            self.confidence_scores['primary_complaint'] = 0.8
        elif any(word in message_lower for word in ['work', 'job', 'career', 'boss']):
            self.slots['primary_complaint'] = 'work_stress'
            self.confidence_scores['primary_complaint'] = 0.7
        
        # Extract duration
        if any(word in message_lower for word in ['months', 'years', 'long time', 'always']):
            self.slots['duration'] = 'chronic'
            self.confidence_scores['duration'] = 0.7
        elif any(word in message_lower for word in ['recently', 'lately', 'past week', 'few days']):
            self.slots['duration'] = 'recent'
            self.confidence_scores['duration'] = 0.7
        
        # Extract severity (simple sentiment analysis)
        severe_words = ['really', 'very', 'extremely', 'can\'t', 'unbearable']
        if any(word in message_lower for word in severe_words):
            self.slots['severity'] = 'high'
            self.confidence_scores['severity'] = 0.6
        
        return self.get_overall_confidence()
    
    def get_overall_confidence(self):
        """Calculate overall confidence in understanding the user"""
        filled_slots = sum(1 for score in self.confidence_scores.values() if score > 0)
        total_confidence = sum(self.confidence_scores.values()) / 4
        return total_confidence
    
    def generate_response(self, user_message, turn_count):
        """
        Generate empathetic response based on conversation stage
        In production, this would use OpenAI API with the system prompt
        """
        self.analyze_message(user_message)
        confidence = self.get_overall_confidence()
        
        responses = {
            1: [
                "that sounds really heavy. i'm sorry you're dealing with that. how long has this been going on?",
                "i hear you. that must be exhausting to carry around. has it been like this for a while?",
                "thank you for trusting me with this. how long have you been feeling this way?"
            ],
            2: [
                "that makes sense. it's hard when things pile up like that. on a scale of 1-10, how overwhelming does it feel right now?",
                "i can imagine how draining that must be. when you wake up in the morning, how heavy does it feel?",
                "i appreciate you sharing that. what would a good day look like for you?"
            ],
            3: [
                "i'm starting to see the picture. are you looking for someone to just listen, or do you want to actively work on this?",
                "thank you for being so open. do you feel like you need space to vent, or are you ready to explore solutions?",
                "i'm glad you're here. what do you think you need most right now—to be heard, or to find a path forward?"
            ],
            4: [
                "i think i really understand where you're coming from now. you're not alone in this—there are others who feel exactly what you're feeling. would you like me to connect you with them?",
                "thank you for trusting me with all of this. i have an idea of a group that deals with exactly what you're going through. want to see?",
                "i've been listening carefully, and i think i know some people who would really get you. ready to meet your tribe?"
            ]
        }
        
        # Exit condition: high confidence or 4+ turns
        if confidence > 0.8 or turn_count >= 4:
            return {
                'message': responses[4][random.randint(0, 2)],
                'ready_for_next_phase': True,
                'confidence': confidence,
                'extracted_data': self.slots
            }
        
        turn = min(turn_count, 3)
        return {
            'message': responses[turn][random.randint(0, len(responses[turn])-1)],
            'ready_for_next_phase': False,
            'confidence': confidence
        }


# =====================================================
# GROUP MATCHING & CATEGORIZATION
# =====================================================

class GroupMatcher:
    """
    Intelligent group formation based on therapeutic needs
    """
    
    ARCHETYPE_GROUPS = {
        'navigators': {
            'name': 'The Navigators',
            'description': 'For high-performers dealing with career stress, imposter syndrome, and performance pressure.',
            'keywords': ['work', 'career', 'stress', 'imposter', 'performance', 'anxiety'],
            'focus': 'Career/Academic Stress',
            'capacity': '6-8 members',
            'emoji': '🧭'
        },
        'anchors': {
            'name': 'The Anchors',
            'description': 'For those processing grief, loss, or major life transitions.',
            'keywords': ['grief', 'loss', 'death', 'transition', 'change', 'moving'],
            'focus': 'Grief & Loss',
            'capacity': '5-7 members',
            'emoji': '⚓'
        },
        'mirrors': {
            'name': 'The Mirrors',
            'description': 'For those struggling with social anxiety, relationships, and self-perception.',
            'keywords': ['social', 'anxiety', 'relationships', 'friends', 'lonely', 'connection'],
            'focus': 'Social Anxiety & Relationships',
            'capacity': '6-8 members',
            'emoji': '🪞'
        },
        'balancers': {
            'name': 'The Balancers',
            'description': 'For those experiencing burnout and struggling with work-life boundaries.',
            'keywords': ['burnout', 'tired', 'exhausted', 'boundaries', 'overworked'],
            'focus': 'Burnout & Balance',
            'capacity': '6-8 members',
            'emoji': '⚖️'
        },
        'explorers': {
            'name': 'The Explorers',
            'description': 'For those figuring out identity, self-esteem, and who they want to be.',
            'keywords': ['identity', 'self', 'confidence', 'worth', 'purpose', 'meaning'],
            'focus': 'Identity & Self-Esteem',
            'capacity': '6-8 members',
            'emoji': '🌱'
        }
    }
    
    @staticmethod
    def match_to_group(user_data):
        """
        Match user to appropriate group based on their concerns
        """
        primary_concern = user_data.get('primary_complaint', '').lower()
        
        # Score each group
        scores = {}
        for group_id, group_info in GroupMatcher.ARCHETYPE_GROUPS.items():
            score = 0
            for keyword in group_info['keywords']:
                if keyword in primary_concern:
                    score += 1
            scores[group_id] = score
        
        # Return highest scoring group
        if max(scores.values()) > 0:
            best_group = max(scores, key=scores.get)
        else:
            # Default to navigators for demo
            best_group = 'navigators'
        
        return GroupMatcher.ARCHETYPE_GROUPS[best_group]
    
    @staticmethod
    def generate_insight_card(user_data, group):
        """
        Generate personalized insight card
        """
        insights = {
            'navigators': {
                'archetype': 'The Navigator',
                'title': "You're carrying the weight of everyone's expectations",
                'description': "You're a guardian type—protective, driven, but tired. You set incredibly high standards for yourself, and right now, it feels like you're constantly proving your worth. That's exhausting. The good news? You're not alone in this."
            },
            'anchors': {
                'archetype': 'The Anchor',
                'title': "You're holding onto something heavy",
                'description': "Loss has a way of making us feel untethered. You're trying to find solid ground again, and that takes time. There's no rush. Others in your group understand what it means to carry grief while still moving forward."
            },
            'mirrors': {
                'archetype': 'The Mirror',
                'title': "You're searching for connection",
                'description': "Social situations feel like a performance, and you're tired of the script. You want genuine connection but don't always know how to bridge that gap. Your group gets it—they're learning too."
            },
            'balancers': {
                'archetype': 'The Balancer',
                'title': "You're running on empty",
                'description': "You've been going and going and going. The lines between work and rest have blurred, and you can't remember the last time you felt truly recharged. Your group knows what it's like to hit empty."
            },
            'explorers': {
                'archetype': 'The Explorer',
                'title': "You're figuring out who you are",
                'description': "Identity feels fluid right now. You're questioning old beliefs, trying on new perspectives, and that uncertainty is uncomfortable. Your group is on the same journey of self-discovery."
            }
        }
        
        group_key = [k for k, v in GroupMatcher.ARCHETYPE_GROUPS.items() if v['name'] == group['name']][0]
        return insights.get(group_key, insights['navigators'])


# =====================================================
# THERAPIST HANDOFF SYSTEM
# =====================================================

class TherapistHandoff:
    """
    Generate comprehensive briefing materials for therapists
    """
    
    @staticmethod
    def generate_participant_profile(user_data):
        """Generate individual participant summary"""
        return {
            'name': user_data.get('name', 'Anonymous'),
            'age': user_data.get('age', 'N/A'),
            'occupation': user_data.get('occupation', 'N/A'),
            'primary_concern': user_data.get('primary_complaint', 'General wellness'),
            'duration': user_data.get('duration', 'Unknown'),
            'severity': user_data.get('severity', 'Moderate'),
            'trigger_words': user_data.get('triggers', []),
            'needs': user_data.get('therapeutic_needs', 'Support and validation'),
            'conversation_summary': user_data.get('conversation_summary', '')
        }
    
    @staticmethod
    def generate_group_brief(group, participants):
        """Generate comprehensive group briefing"""
        return {
            'group_name': group['name'],
            'focus_area': group['focus'],
            'session_date': (datetime.now() + timedelta(days=2)).strftime('%A, %B %d, %Y'),
            'session_time': '6:00 PM',
            'participant_count': len(participants),
            'group_themes': [
                'Performance pressure',
                'Fear of failure',
                'Work-life balance',
                'Imposter syndrome'
            ],
            'collective_mood': 'High anxiety, low energy',
            'recommended_focus': [
                'Validate their struggles without pathologizing',
                'Address perfectionism and self-worth',
                'Create space for vulnerability',
                'Discuss boundary-setting strategies'
            ],
            'participants': [TherapistHandoff.generate_participant_profile(p) for p in participants]
        }


# =====================================================
# API ENDPOINTS
# =====================================================

# In-memory storage (use database in production)
active_sessions = {}
user_data_store = {}

@app.route('/')
def index():
    """Serve the main application"""
    return render_template('haven-app.html')

@app.route('/api/chat/start', methods=['POST'])
def start_chat():
    """Initialize a new chat session"""
    session_id = f"session_{datetime.now().timestamp()}"
    active_sessions[session_id] = ChatbotEngine()
    
    return jsonify({
        'session_id': session_id,
        'message': "hey there. the world can be a lot sometimes. how are you holding up today?"
    })

@app.route('/api/chat/message', methods=['POST'])
def chat_message():
    """Process user message and generate response"""
    data = request.json
    session_id = data.get('session_id')
    user_message = data.get('message')
    turn_count = data.get('turn_count', 1)
    
    if session_id not in active_sessions:
        return jsonify({'error': 'Invalid session'}), 400
    
    chatbot = active_sessions[session_id]
    response = chatbot.generate_response(user_message, turn_count)
    
    # Store conversation history
    chatbot.conversation_history.append({
        'role': 'user',
        'message': user_message,
        'timestamp': datetime.now().isoformat()
    })
    chatbot.conversation_history.append({
        'role': 'bot',
        'message': response['message'],
        'timestamp': datetime.now().isoformat()
    })
    
    return jsonify(response)

@app.route('/api/assessment/bubble', methods=['POST'])
def bubble_assessment():
    """Process bubble popper game results"""
    data = request.json
    session_id = data.get('session_id')
    selected_bubbles = data.get('selected_bubbles', [])
    
    # Store assessment data
    if session_id in active_sessions:
        chatbot = active_sessions[session_id]
        chatbot.slots['stressors'] = selected_bubbles
    
    return jsonify({
        'status': 'success',
        'message': 'Assessment data recorded'
    })

@app.route('/api/assessment/mood', methods=['POST'])
def mood_assessment():
    """Process mood slider results"""
    data = request.json
    session_id = data.get('session_id')
    mood_level = data.get('mood_level', 50)
    
    if session_id in active_sessions:
        chatbot = active_sessions[session_id]
        chatbot.slots['mood_level'] = mood_level
    
    return jsonify({
        'status': 'success',
        'message': 'Mood data recorded'
    })

@app.route('/api/matching/find-group', methods=['POST'])
def find_group():
    """Match user to appropriate therapy group"""
    data = request.json
    session_id = data.get('session_id')
    
    if session_id not in active_sessions:
        return jsonify({'error': 'Invalid session'}), 400
    
    chatbot = active_sessions[session_id]
    user_data = chatbot.slots
    
    # Match to group
    matched_group = GroupMatcher.match_to_group(user_data)
    
    # Generate insight card
    insight = GroupMatcher.generate_insight_card(user_data, matched_group)
    
    return jsonify({
        'group': matched_group,
        'insight': insight
    })

@app.route('/api/scheduling/available-slots', methods=['GET'])
def get_available_slots():
    """Get available therapy session time slots"""
    slots = [
        {'day': 'Tuesday', 'time': '6:00 PM', 'available': True},
        {'day': 'Wednesday', 'time': '7:00 PM', 'available': True},
        {'day': 'Thursday', 'time': '6:00 PM', 'available': True},
        {'day': 'Saturday', 'time': '10:00 AM', 'available': True}
    ]
    
    return jsonify({'slots': slots})

@app.route('/api/booking/confirm', methods=['POST'])
def confirm_booking():
    """Confirm therapy session booking and process payment"""
    data = request.json
    session_id = data.get('session_id')
    time_slot = data.get('time_slot')
    payment_info = data.get('payment_info')
    
    # In production: Process with Stripe API
    booking_id = f"booking_{datetime.now().timestamp()}"
    
    return jsonify({
        'status': 'success',
        'booking_id': booking_id,
        'message': 'Booking confirmed and payment processed'
    })

@app.route('/api/therapist/dashboard/<group_id>', methods=['GET'])
def therapist_dashboard(group_id):
    """Get therapist dashboard data for a group"""
    # Mock participant data
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
    
    group = GroupMatcher.ARCHETYPE_GROUPS.get(group_id, GroupMatcher.ARCHETYPE_GROUPS['navigators'])
    brief = TherapistHandoff.generate_group_brief(group, participants)
    
    return jsonify(brief)

@app.route('/api/therapist/download-brief/<group_id>', methods=['GET'])
def download_brief(group_id):
    """Generate and download PDF briefing material"""
    # In production: Generate actual PDF with ReportLab
    return jsonify({
        'status': 'success',
        'message': 'PDF generation would happen here',
        'url': f'/downloads/brief_{group_id}.pdf'
    })


# =====================================================
# MAIN
# =====================================================

if __name__ == '__main__':
    app.run(debug=True, port=5000)
