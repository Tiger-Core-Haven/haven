import os
import json
from datetime import datetime, timedelta
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List, Literal, Optional

# --- Configuration ---
# Make sure to set GOOGLE_API_KEY in your .env
api_key = os.getenv("GOOGLE_API_KEY", "").strip()
client = genai.Client(api_key=api_key)
MODEL_NAME = "gemini-2.5-flash-lite" 

class InsightCard(BaseModel):
    selected_group_id: Literal['navigators', 'anchors', 'mirrors', 'balancers', 'explorers'] = Field(
        description="The ID of the group that best fits the user."
    )
    title: str = Field(description="A short, hitting 2nd-person title (e.g., 'You're carrying the weight of the world').")
    description: str = Field(description="A warm, validating description of why they fit this archetype.")

class GroupThemeAnalysis(BaseModel):
    collective_mood: str = Field(description="2-3 words describing the group's vibe (e.g. 'Anxious but hopeful').")
    group_themes: List[str] = Field(description="Top 4 psychological themes present in this group of people.")
    recommended_focus: List[str] = Field(description="4 specific clinical interventions or discussion points for the therapist.")
    icebreaker_suggestion: str = Field(description="A specific question to open this session.")

# --- Logic Classes ---

class GroupMatcher:
    ARCHETYPE_GROUPS = {
    'navigators': {
        'name': 'The Navigators',
        'description': 'High-performers dealing with career stress & imposter syndrome.',
        'focus': 'Career/Academic Stress',
        'capacity': '6-8 members',
        'emoji': '🧭'
    },
    'anchors': {
        'name': 'The Anchors',
        'description': 'Processing grief, loss, or major life transitions.',
        'focus': 'Grief & Loss',
        'capacity': '5-7 members',
        'emoji': '⚓'
    },
    'mirrors': {
        'name': 'The Mirrors',
        'description': 'Social anxiety, relationship struggles, and self-perception.',
        'focus': 'Social Anxiety & Relationships',
        'capacity': '6-8 members',
        'emoji': '🪞'
    },
    'balancers': {
        'name': 'The Balancers',
        'description': 'Burnout, exhaustion, and work-life boundaries.',
        'focus': 'Burnout & Balance',
        'capacity': '6-8 members',
        'emoji': '⚖️'
    },
    'explorers': {
        'name': 'The Explorers',
        'description': 'Identity crisis, self-esteem, and finding purpose.',
        'focus': 'Identity & Self-Esteem',
        'capacity': '6-8 members',
        'emoji': '🌱'
    }
}

    @staticmethod
    def match_to_group(user_data):
        """
        Uses AI to match a user to a group based on their intake data.
        Returns the group dict AND the generated insight card.
        """
        
        # 1. Construct the Prompt
        # We dump the ARCHETYPE_GROUPS so the AI knows the options
        prompt = f"""
        You are a Clinical Supervisor matching a new client to a therapy group.
        
        AVAILABLE GROUPS:
        {json.dumps(GroupMatcher.ARCHETYPE_GROUPS, indent=2)}
        
        NEW CLIENT PROFILE:
        - Complaint: {user_data.get('primary_complaint')}
        - Duration: {user_data.get('duration')}
        - Severity: {user_data.get('severity')}
        - Goal: {user_data.get('goal')}
        
        TASK:
        1. Analyze the client's profile.
        2. Assign them to the ONE group that fits best.
        3. Write a personalized "Insight Card" that validates their struggle.
        """

        try:
            # 2. Call Gemini
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.4, # Low temp for consistent matching
                    response_mime_type="application/json",
                    response_schema=InsightCard.model_json_schema()
                )
            )
            
            # 3. Parse Result
            result = InsightCard.model_validate_json(response.text)
            
            # 4. Format Output for Frontend
            group_id = result.selected_group_id
            group_info = GroupMatcher.ARCHETYPE_GROUPS.get(group_id, GroupMatcher.ARCHETYPE_GROUPS['navigators'])
            
            # We return the group info, but we attach the AI-generated insight to it
            # (or return it separately depending on your route logic)
            return group_info, result

        except Exception as e:
            print(f"GroupMatching Error: {e}")
            # Fallback to Navigators if AI fails
            fallback_insight = InsightCard(
                selected_group_id='navigators',
                title="We see you working hard",
                description="It looks like you're carrying a lot. The Navigators group is for people exactly like you."
            )
            return GroupMatcher.ARCHETYPE_GROUPS['navigators'], fallback_insight

    @staticmethod
    def generate_insight_card(user_data, group):
        # NOTE: In the new logic, `match_to_group` generates the insight already.
        # This function exists to maintain backward compatibility with your route.
        # If `group` passed here is just the dict, we might need to re-generate or just pass-through.
        
        # Ideally, update your route to unpack the tuple returned by `match_to_group`
        pass 


class TherapistHandoff:
    @staticmethod
    def generate_group_brief(group_def, participants):
        """
        Analyzes a list of participants and generates a clinical briefing for the therapist.
        """
        
        prompt = f"""
        You are a Lead Therapist preparing a briefing document for an upcoming group session.
        
        GROUP CONTEXT:
        Name: {group_def.get('name')}
        Focus: {group_def.get('focus')}
        
        PARTICIPANTS:
        {json.dumps(participants, indent=2)}
        
        TASK:
        Analyze the participants to determine the collective mood, common themes, and clinical focus.
        """

        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7, # Higher temp for creativity in suggestions
                    response_mime_type="application/json",
                    response_schema=GroupThemeAnalysis.model_json_schema()
                )
            )
            
            analysis = GroupThemeAnalysis.model_validate_json(response.text)
            
            # Combine hard data with AI analysis
            return {
                'group_name': group_def.get('name'),
                'focus_area': group_def.get('focus'),
                'session_date': (datetime.now() + timedelta(days=2)).strftime('%A, %B %d, %Y'),
                'session_time': '6:00 PM',
                'participant_count': len(participants),
                
                # AI Generated Fields
                'group_themes': analysis.group_themes,
                'collective_mood': analysis.collective_mood,
                'recommended_focus': analysis.recommended_focus,
                'icebreaker': analysis.icebreaker_suggestion,
                
                'participants': participants
            }

        except Exception as e:
            print(f"Handoff Error: {e}")
            return {
                'group_name': group_def.get('name'),
                'error': "Could not generate AI brief",
                'participants': participants
            }