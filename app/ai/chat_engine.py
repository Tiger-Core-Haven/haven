import json
import os
import re
from typing import Optional, Literal

from google import genai
from pydantic import BaseModel, Field, ValidationError

from app.ai.selected_model import SELECTED_MODEL

class ExtractedData(BaseModel):
    primary_complaint: Optional[str] = Field(None, description="Main struggle (e.g. anxiety, burnout)")
    duration: Optional[str] = Field(None, description="How long it has been happening")
    severity: Optional[Literal["low", "medium", "high"]] = Field(None, description="Perceived severity")
    goal: Optional[str] = Field(None, description="What the user wants: venting, solutions, connection")


class TherapyResponse(BaseModel):
    message: str = Field(description="Warm, empathetic, lowercase response")
    ready_for_next_phase: bool = Field(description="True only if user explicitly consents")
    extracted_data: ExtractedData


class ChatbotEngine:
    f"""
    Therapist Chatbot powered by Google ({SELECTED_MODEL})
    (Uses Native Pydantic Structured Outputs)
    """
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found")

        self.client = genai.Client(api_key=api_key.strip())
        self.model_id = os.getenv("GEMINI_MODEL", SELECTED_MODEL)
        self.conversation_history = []

        self.system_prompt = (
            "You are a warm, empathetic intake facilitator for 'Haven', a digital group therapy platform.\n"
            "You are not a clinician. Avoid clinical jargon. Use lowercase, short sentences.\n\n"
            "Goals:\n"
            "1) Understand primary concern, duration, severity, and goal.\n"
            "2) Summarize and ask for consent before moving forward.\n"
            "3) Set ready_for_next_phase = true ONLY if the user explicitly agrees.\n\n"
            "Return ONLY valid JSON in this format:\n"
            "{\n"
            '  "message": "string",\n'
            '  "ready_for_next_phase": boolean,\n'
            '  "extracted_data": {\n'
            '    "primary_complaint": "string or null",\n'
            '    "duration": "string or null",\n'
            '    "severity": "low|medium|high or null",\n'
            '    "goal": "string or null"\n'
            "  }\n"
            "}\n"
        )

    def _build_prompt(self, user_message: str) -> str:
        self.conversation_history.append({"role": "user", "content": user_message})
        convo_lines = []
        for item in self.conversation_history[-10:]:
            role = item["role"]
            content = item["content"]
            convo_lines.append(f"{role.upper()}: {content}")
        convo_text = "\n".join(convo_lines)
        return f"{self.system_prompt}\nConversation:\n{convo_text}\n\nReturn JSON only."

    @staticmethod
    def _extract_text(response) -> str:
        if hasattr(response, "text") and response.text:
            return response.text
        if hasattr(response, "candidates") and response.candidates:
            parts = response.candidates[0].content.parts
            if parts and hasattr(parts[0], "text"):
                return parts[0].text
        return ""

    @staticmethod
    def _parse_json(text: str) -> dict:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("No JSON found in response")
        return json.loads(match.group(0))

    def generate_response(self, user_message: str) -> dict:
        prompt = self._build_prompt(user_message)
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            text = self._extract_text(response)
            data = self._parse_json(text)

            parsed = TherapyResponse.model_validate(data)
            self.conversation_history.append({"role": "assistant", "content": parsed.message})
            return parsed.model_dump()

        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            return {
                "message": "i'm having a little trouble understanding that. could you say it a different way?",
                "ready_for_next_phase": False,
                "extracted_data": {
                    "primary_complaint": None,
                    "duration": None,
                    "severity": None,
                    "goal": None
                }
            }
        except Exception as e:
            return {
                "message": "i'm having a little trouble connecting right now. could you try again in a moment?",
                "ready_for_next_phase": False,
                "extracted_data": {
                    "primary_complaint": None,
                    "duration": None,
                    "severity": None,
                    "goal": None
                }
            }
