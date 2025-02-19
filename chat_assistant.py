from openai import OpenAI
from voice_generator import VoiceGenerator

class OpenAIChatAssistant:
    def __init__(self, voice="sage", model="gpt-4o"):
        """Initialisiert den Chat-Assistenten mit OpenAI API und Text-to-Speech"""
        self.openai = OpenAI()
        self.model = model
        self.tts = VoiceGenerator(voice=voice)  # Text-to-Speech-Klasse
        
        self.system_prompt = (
            "You are Sage, a highly advanced AI assistant. "
            "Your responses should be as short as possible while still being informative. "
            "If a technical problem occurs, provide a practical solution. "
            "If asked about your identity, respond: 'I am Sage, your AI assistant.'"
        )


    def get_response(self, user_input):
        """Sendet den Text an OpenAI GPT und gibt die Antwort zurück"""
        try:
            response = self.openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_input}
                ]
            )
            answer = response.choices[0].message.content
            return answer

        except Exception as e:
            print(f"❌ OpenAI request failed: {e}")
            return "An error occurred during processing."

    def speak_response(self, user_input):
        """Holt die GPT-Antwort und spricht sie aus"""
        response = self.get_response(user_input)
        self.tts.speak(response)