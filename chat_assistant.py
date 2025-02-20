import datetime
from collections import deque
from openai import OpenAI
from voice_generator import VoiceGenerator
from agents.weather_agent import WeatherClient

class OpenAIChatAssistant:
    def __init__(self, voice="sage", model="gpt-4o-mini", history_limit=5):
        """Initialisiert den Chat-Assistenten mit OpenAI API, TTS und Konversationsverlauf"""
        self.openai = OpenAI()
        self.model = model
        self.tts = VoiceGenerator(voice=voice)  # Text-to-Speech
        self.weather_client = WeatherClient()  # Wetter-Client

        # System-Prompt mit Anweisungen für das Verhalten
        self.system_prompt = (
            "You are Sage, a highly advanced AI assistant. "
            "Your responses should be as short as possible while still being informative. "
            "You have access to a weather function and can retrieve real-time weather data if necessary. "
            "When providing a weather update, always mention the city name and describe the weather throughout the day, "
            "taking the current time into account to make the response more relevant. "
            "Always respond in English, regardless of the user's language."
        )

        # Konversationsverlauf speichern (maximal `history_limit` Einträge)
        self.history = deque(maxlen=history_limit)

    def get_response(self, user_input):
        """Sendet den Text an OpenAI GPT und gibt die Antwort zurück, inklusive kurzem Konversationsverlauf"""
        try:
            # Falls eine Wetteranfrage erkannt wird, Wetterdaten hinzufügen
            if "wetter" in user_input.lower() or "wie ist das wetter" in user_input.lower():
                current_time = datetime.datetime.now().strftime("%H:%M")
                weather_info = self.weather_client.get_weather()
                weather_text = "\n".join(weather_info)
                user_input += f"\n\nCurrent time: {current_time}\nWeather report:\n{weather_text}"

            # Konversationsverlauf in das Nachrichtenformat umwandeln
            messages = [{"role": "system", "content": self.system_prompt}]
            for user_msg, ai_msg in self.history:
                messages.append({"role": "user", "content": user_msg})
                messages.append({"role": "assistant", "content": ai_msg})
            
            messages.append({"role": "user", "content": user_input})

            response = self.openai.chat.completions.create(
                model=self.model,
                messages=messages
            )

            ai_response = response.choices[0].message.content

            # Neuesten User-Prompt + Antwort speichern
            self.history.append((user_input, ai_response))

            return ai_response

        except Exception as e:
            print(f"❌ OpenAI request failed: {e}")
            return "An error occurred during processing."

    def speak_response(self, user_input):
        """Holt die GPT-Antwort und spricht sie aus"""
        response = self.get_response(user_input)
        self.tts.speak(response)
