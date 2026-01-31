from datetime import datetime, timedelta

class GroupMatcher:
    ARCHETYPE_GROUPS = {
        'navigators': {
            'name': 'The Navigators',
            'description': 'For high-performers...',
            'keywords': ['work', 'career', 'stress', 'imposter'],
            'focus': 'Career/Academic Stress',
            'emoji': '🧭'
        },

    }
    
    @staticmethod
    def match_to_group(user_data):
        primary_concern = user_data.get('primary_complaint', '').lower()
        scores = {}
        for group_id, group_info in GroupMatcher.ARCHETYPE_GROUPS.items():
            score = 0
            for keyword in group_info['keywords']:
                if keyword in primary_concern:
                    score += 1
            scores[group_id] = score
        
        if max(scores.values()) > 0:
            return GroupMatcher.ARCHETYPE_GROUPS[max(scores, key=scores.get)]
        return GroupMatcher.ARCHETYPE_GROUPS['navigators']

    @staticmethod
    def generate_insight_card(user_data, group):

        return {
            'title': "You're carrying the weight of everyone's expectations",
            'description': "You're a guardian type..."
        }

class TherapistHandoff:
    @staticmethod
    def generate_group_brief(group, participants):
        return {
            'group_name': group['name'],
            'session_date': (datetime.now() + timedelta(days=2)).strftime('%A, %B %d'),
            'participants': participants 
        }