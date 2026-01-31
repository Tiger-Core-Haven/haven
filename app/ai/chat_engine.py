import os
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import Literal, Optional

class ExtractedData(BaseModel):
    primary_complaint: Optional[str] = Field(None, description="The user's main struggle (e.g. Anxiety, Burnout).")
    duration: Optional[str] = Field(None, description="How long the issue has persisted.")
    severity: Optional[Literal["low", "medium", "high"]] = Field(None, description="Subjective severity.")
    goal: Optional[str] = Field(None, description="What the user wants (venting, solutions, etc).")

class TherapyResponse(BaseModel):
    message: str = Field(description="The warm, empathetic, lowercase response to the user.")
    ready_for_next_phase: bool = Field(description="Set to True ONLY if the user explicitly consents to moving forward.")
    extracted_data: ExtractedData

class ChatbotEngine:
    """
    Therapist Chatbot powered by Google Gemini 2.5 Flash
    (Uses Native Pydantic Structured Outputs)
    """
    def __init__(self):
        raw_key = os.getenv("GOOGLE_API_KEY")
        if not raw_key:
            raise ValueError("GOOGLE_API_KEY not found")
        
        self.client = genai.Client(api_key=raw_key.strip())
        
        self.system_instruction = """
        You are a mental wellness intake facilitator for a digital group therapy platform.

        Your role is not to diagnose, treat, or give clinical advice. You are here to listen, reflect, and gently guide the user toward clarity and appropriate group support.

        Core Principles:

        Maintain a calm, warm, non-judgmental tone.

        Use simple, human language. Avoid clinical jargon.

        Ask open-ended questions that help users articulate emotions, stressors, goals, and patterns.

        Validate emotions without reinforcing negative beliefs.

        Never escalate into crisis intervention unless explicitly required (assume non-emergency context).

        Conversational Goals:

        Understand the primary emotional concern (e.g., anxiety, burnout, grief, social stress).

        Identify context (academic, work, relationships, identity, life transitions).

        Detect intensity and persistence (frequency, duration, impact on daily life).

        Clarify the user’s intent (venting, reflection, growth, support).

        Collect timezone and general availability in a natural way.

        Questioning Strategy:

        Start broad, then gently narrow.

        Ask no more than 6–8 meaningful questions total.

        Reflect back insights occasionally (“It sounds like…”).

        Avoid rapid-fire questioning.

        Timezone & Availability:

        At an appropriate moment, naturally ask where the user is located or what timezone they’re in.

        Later, ask about general availability windows (morning / afternoon / evening).

        Ending the Intake:

        End the conversation only when you have sufficient clarity on:

        Main concern

        Desired support style

        Timezone + rough availability

        When ending, summarize what you understood in 2–3 sentences.

        Ask for consent before moving to group matching.
        """

        # forced schema
        self.chat = self.client.chats.create(
            model="gemini-2.5-flash-lite",
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                temperature=0.5,
                response_mime_type="application/json",
                response_schema=TherapyResponse.model_json_schema()
            )
        )

    def generate_response(self, user_message: str) -> dict:
        try:
            response = self.chat.send_message(user_message)
            
            structured_response = TherapyResponse.model_validate_json(response.text)
            
            return structured_response.model_dump()

        except Exception as e:
            print(f"Gemini Error: {e}")
            return {
                "message": "i'm having a little trouble connecting right now. could you say that again?",
                "ready_for_next_phase": False,
                "extracted_data": {
                    "primary_complaint": None,
                    "duration": None,
                    "severity": None,
                    "goal": None
                }
            }