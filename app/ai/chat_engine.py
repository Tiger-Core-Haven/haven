import boto3
import json
import re

# Initialize Bedrock Client
bedrock_client = boto3.client(
    service_name='bedrock-runtime', 
    region_name='us-east-1' 
)

class ChatbotEngine:
    """
    Therapist Chatbot powered by AWS Bedrock (Claude 3.5 Sonnet)
    """
    def __init__(self):
        # Using Sonnet for better adherence to complex "consent" instructions
        self.model_id = "us.anthropic.claude-3-5-sonnet-20240620-v1:0" 
        self.conversation_history = []
        
        self.system_prompt = """
        You are a warm, empathetic intake facilitator for 'Haven', a digital group therapy platform.
        Your goal is to gather insights about the user to match them with a support group.

        YOUR PROCESS (Must be followed in order):
        1. EXPLORE: Ask gentle, open-ended questions to understand their:
           - Primary struggle (Anxiety, Burnout, Grief, etc.)
           - Duration (How long has this been happening?)
           - Severity (Impact on daily life)
           - Goal (Venting, strategies, or connection?)
        
        2. SUMMARIZE & CONSENT (Crucial):
           - Once you have a clear picture, DO NOT immediately end the session.
           - Instead, summarize what you have heard in a validating way.
           - Explicitly ask: "Does that sound about right? If you're ready, I can look for a group that matches this profile."
        
        3. FINALIZE:
           - ONLY set "ready_for_next_phase" to TRUE if the user explicitly confirms (e.g., "Yes", "Go ahead").
           - If they hesitate, continue listening.

        OUTPUT RULES:
        - You must output ONLY valid JSON.
        - Do not include markdown formatting (like ```json).
        - Structure:
        {
            "message": "Your conversational response here (lowercase, warm, human-like)",
            "ready_for_next_phase": boolean,
            "extracted_data": {
                "primary_complaint": "summary string or null",
                "duration": "summary string or null",
                "severity": "low/med/high or null",
                "goal": "summary string or null"
            }
        }
        """

    def generate_response(self, user_message):
        self.conversation_history.append({
            "role": "user",
            "content": [{"text": user_message}]
        })

        try:
            response = bedrock_client.converse(
                modelId=self.model_id,
                messages=self.conversation_history,
                system=[{"text": self.system_prompt}],
                inferenceConfig={"temperature": 0.5, "maxTokens": 512}
            )

            ai_response_text = response['output']['message']['content'][0]['text']
            
            # Robust JSON extraction using Regex
            json_match = re.search(r'\{.*\}', ai_response_text, re.DOTALL)
            
            if json_match:
                clean_json = json_match.group(0)
                parsed_data = json.loads(clean_json)
            else:
                # Fallback if the model is chatty but valid
                # We attempt to treat the whole text as the message if JSON fails
                parsed_data = {
                    "message": ai_response_text,
                    "ready_for_next_phase": False,
                    "extracted_data": {}
                }

            # Save assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": [{"text": parsed_data['message']}]
            })

            return parsed_data

        except Exception as e:
            print(f"Bedrock Error: {e}")
            return {
                "message": "i'm having a little trouble connecting right now. could you say that again?",
                "ready_for_next_phase": False,
                "extracted_data": {}
            }