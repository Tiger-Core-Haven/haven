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
        elif any(word in message_lower for word in ['stressed', 'pressure', 'overwhelmed']):
            self.slots['primary_complaint'] = 'stress'
            self.confidence_scores['primary_complaint'] = 0.8

        
        return self.get_overall_confidence()
    
    def get_overall_confidence(self):
        return sum(self.confidence_scores.values()) / 4
    
    def generate_response(self, user_message, turn_count):
        self.analyze_message(user_message)
        confidence = self.get_overall_confidence()
        
        responses = {
            1: ["that sounds really heavy...", "i hear you..."],
            2: ["that makes sense...", "i can imagine..."],
            3: ["i'm starting to see...", "thank you for being open..."],
            4: ["i think i understand...", "ready to meet your tribe?"]
        }
        
        if confidence > 0.8 or turn_count >= 4:

            msg = responses[4][random.randint(0, len(responses[4])-1)]
            return {
                'message': msg,
                'ready_for_next_phase': True,
                'extracted_data': self.slots
            }
        
        turn = min(turn_count, 3)
        msg = responses[turn][random.randint(0, len(responses[turn])-1)]
        return {
            'message': msg,
            'ready_for_next_phase': False
        }