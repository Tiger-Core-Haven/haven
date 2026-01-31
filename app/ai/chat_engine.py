import random

class ChatbotEngine:
    """
    Warm, empathetic chatbot logic
    """
    def __init__(self):
        self.slots = {
            'primary_complaint': None,
            'duration': None,
            'severity': None,
            'goal': None
        }
        self.confidence_scores = {
            'primary_complaint': 0, 'duration': 0, 'severity': 0, 'goal': 0
        }
        self.conversation_history = []
        
    def analyze_message(self, user_message):
        message_lower = user_message.lower()

        if any(word in message_lower for word in ['anxious', 'anxiety', 'worried', 'nervous']):
            self.slots['primary_complaint'] = 'anxiety'
            self.confidence_scores['primary_complaint'] = 0.8
        elif any(word in message_lower for word in ['stressed', 'pressure', 'overwhelmed', 'busy']):
            self.slots['primary_complaint'] = 'stress'
            self.confidence_scores['primary_complaint'] = 0.8
        elif any(word in message_lower for word in ['sad', 'down', 'empty']):
            self.slots['primary_complaint'] = 'depression'
            self.confidence_scores['primary_complaint'] = 0.8
        elif any(word in message_lower for word in ['work', 'job', 'career', 'boss']):
            self.slots['primary_complaint'] = 'work_stress'
            self.confidence_scores['primary_complaint'] = 0.7

        if any(word in message_lower for word in ['months', 'years', 'long time', 'always']):
            self.slots['duration'] = 'chronic'
            self.confidence_scores['duration'] = 0.7
        elif any(word in message_lower for word in ['recently', 'lately', 'past week', 'few days']):
            self.slots['duration'] = 'recent'
            self.confidence_scores['duration'] = 0.7

        severe_words = ['really', 'very', 'extremely', "can't", 'unbearable']
        if any(word in message_lower for word in severe_words):
            self.slots['severity'] = 'high'
            self.confidence_scores['severity'] = 0.6

        return self.get_overall_confidence()
    
    def get_overall_confidence(self):
        return sum(self.confidence_scores.values()) / 4
    
    def generate_response(self, user_message, turn_count):
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
        
        if confidence > 0.8 or turn_count >= 4:
            msg = responses[4][random.randint(0, len(responses[4]) - 1)]
            return {
                'message': msg,
                'ready_for_next_phase': True,
                'extracted_data': self.slots
            }
        
        turn = min(turn_count, 3)
        msg = responses[turn][random.randint(0, len(responses[turn]) - 1)]
        return {
            'message': msg,
            'ready_for_next_phase': False
        }
