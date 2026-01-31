from datetime import datetime, timedelta

class GroupMatcher:
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
        primary_concern = user_data.get('primary_complaint', '').lower()
        scores = {}
        for group_id, group_info in GroupMatcher.ARCHETYPE_GROUPS.items():
            score = 0
            for keyword in group_info['keywords']:
                if keyword in primary_concern:
                    score += 1
            scores[group_id] = score

        if max(scores.values()) > 0:
            best_id = max(scores, key=scores.get)
        else:
            best_id = 'navigators'

        group = dict(GroupMatcher.ARCHETYPE_GROUPS[best_id])
        group['id'] = best_id
        return group

    @staticmethod
    def generate_insight_card(user_data, group):
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

        group_key = None
        for key, info in GroupMatcher.ARCHETYPE_GROUPS.items():
            if info['name'] == group['name']:
                group_key = key
                break
        return insights.get(group_key, insights['navigators'])

class TherapistHandoff:
    @staticmethod
    def generate_group_brief(group, participants):
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
            'participants': participants
        }
