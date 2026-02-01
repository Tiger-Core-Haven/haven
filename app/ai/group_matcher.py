import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Literal, Optional, Dict, Any
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from app.ai.selected_model import SELECTED_MODEL

# --- Configuration ---
api_key = os.getenv("GOOGLE_API_KEY", "").strip()
client = genai.Client(api_key=api_key)
MODEL_NAME = SELECTED_MODEL

logger = logging.getLogger(__name__)

# --- Pydantic Models ---

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
    def match_to_group(user_data: Dict[str, Any]):
        prompt = f"""
        You are a Clinical Supervisor matching a new client to a therapy group.
        
        AVAILABLE GROUPS:
        {json.dumps(GroupMatcher.ARCHETYPE_GROUPS, indent=2)}
        
        NEW CLIENT PROFILE:
        - Complaint: {user_data.get('primary_complaint', 'General Stress')}
        - Duration: {user_data.get('duration', 'Unknown')}
        - Severity: {user_data.get('severity', 'Moderate')}
        - Goal: {user_data.get('goal', 'Support')}
        
        TASK:
        1. Analyze the client's profile.
        2. Assign them to the ONE group that fits best.
        3. Write a personalized "Insight Card" that validates their struggle.
        """

        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.4,
                    response_mime_type="application/json",
                    response_schema=InsightCard
                )
            )
            result = response.parsed
            group_id = result.selected_group_id
            group_info = GroupMatcher.ARCHETYPE_GROUPS.get(group_id, GroupMatcher.ARCHETYPE_GROUPS['navigators'])
            return group_info, result

        except Exception as e:
            logger.error(f"GroupMatching Error: {e}")
            fallback_insight = InsightCard(
                selected_group_id='navigators',
                title="We see you working hard",
                description="It looks like you're carrying a lot. The Navigators group is for people exactly like you."
            )
            return GroupMatcher.ARCHETYPE_GROUPS['navigators'], fallback_insight


class TherapistHandoff:
    @staticmethod
    def generate_group_brief(group_def: Dict[str, Any], participants: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generates JSON data for the dashboard visualizer.
        """
        clean_participants = []
        for p in participants:
            clean_participants.append({
                "concern": p.get('primary_concern'),
                "severity": p.get('severity'),
                "stressors": p.get('stressors'),
                "goals": p.get('conversation_summary')
            })

        prompt = f"""
        You are a Lead Therapist preparing a dashboard summary.
        GROUP: {group_def.get('name')}
        PARTICIPANTS: {json.dumps(clean_participants)}
        TASK: JSON output for mood, themes, and focus.
        """

        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7, 
                    response_mime_type="application/json",
                    response_schema=GroupThemeAnalysis
                )
            )
            return response.parsed.model_dump()
        except Exception:
            # Simple fallback
            return {
                'group_themes': ['Stress', 'Anxiety'],
                'collective_mood': 'Mixed',
                'recommended_focus': ['Introductions'],
                'icebreaker_suggestion': 'How are you?'
            }

    @staticmethod
    def generate_detailed_handoff_report(group_def: Dict[str, Any], participants: List[Dict[str, Any]]) -> str:
        """
        Generates a long-form text report suitable for a PDF download.
        """
        # Prepare detailed context
        context_str = ""
        for p in participants:
            context_str += f"- Participant: {p.get('name', 'Anonymous')}\n"
            context_str += f"  - Complaint: {p.get('primary_concern')}\n"
            context_str += f"  - Stressors: {', '.join(p.get('stressors', []))}\n"
            context_str += f"  - Goals: {p.get('conversation_summary')}\n"
            context_str += f"  - Mood Level: {p.get('mood_level')}/100\n\n"

        prompt = f"""
        You are a Clinical Supervisor. Write a formal "Group Session Briefing Document" for a therapist who is about to lead this group.
        
        GROUP DETAILS:
        Name: {group_def.get('name')}
        Focus: {group_def.get('focus')}
        Target Population: {group_def.get('description')}
        
        PARTICIPANT INSIGHTS:
        {context_str}
        
        TASK:
        Write a structured report (plain text, no markdown **) that includes:
        1. Executive Summary (The overall "vibe" and clinical urgency of the group).
        2. Key Themes (3-4 psychological threads tying these people together).
        3. Participant Snapshots (Brief 1-sentence clinical note on each person).
        4. Proposed Session Structure (Icebreaker, Core Activity, Closing).
        5. Risk Factors (Any severity flags to watch out for).
        
        Make it professional, empathetic, and actionable.
        """

        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.5,
                    response_mime_type="text/plain" 
                )
            )
            return response.text
        except Exception as e:
            return f"Error generating report: {str(e)}"