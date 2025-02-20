import datetime
from collections import deque
import json
import asyncio
from openai import OpenAI
from voice_generator import VoiceGenerator
from agents.weather_agent import WeatherClient
from agents.fitbit_agent import FitbitAPI

class OpenAIChatAssistant:
    def __init__(self, voice="sage", model="gpt-4o-mini", history_limit=5):
        """Initialisiert den Chat-Assistenten mit OpenAI API, TTS und Function Calling"""
        self.openai = OpenAI()
        self.model = model
        self.tts = VoiceGenerator(voice=voice)
        self.history = deque(maxlen=history_limit)
        self.fitbit_api = FitbitAPI()
        
        # Definition der verfügbaren Funktionen für das Modell
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get detailed weather data including current temperature and hourly forecast for the user's current location based on their IP address",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_sleep_data",
                    "description": "Get Fitbit sleep data summary for a specific date. If no date is provided, returns data for the last night.",
                    "parameters": {
                        "type": "object",
                        "properties": {},  # Keine Parameter erforderlich
                        "additionalProperties": False
                    },
                    "strict": True
                }
            }
        ]

        self.system_prompt = (
            "You are Sage, a sharp-witted AI assistant designed for voice interactions. "
            "You're quick, a little cheeky, and you don’t waste words. "
            "Your responses should be smooth, natural, and easy to follow when spoken aloud. "
            "No robotic lists—just straight-up useful info with some personality. "
            "You have access to the following functions:\n"
            "1. A weather function that gives the important stuff—temperature, rain, wind—no fluff.\n"
            "2. A Fitbit function that pulls sleep data and breaks it down without getting all clinical about it.\n"
            "When talking about sleep, report total sleep time, time in bed, and deep sleep in **hours, not minutes**. "
            "If something was really off—like way too little deep sleep or a weirdly short night—point it out casually. "
            "No ratings, no ‘good’ or ‘bad’ sleep—just the facts. Keep it snappy, like you’re talking to a friend."
        )


    async def _execute_weather_function(self):
        """Führt die Wetterabfrage asynchron aus"""
        weather_client = WeatherClient()
        return await weather_client._fetch_weather_data()

    def _execute_function(self, function_call):
        """Führt die aufgerufene Funktion aus und gibt das Ergebnis zurück"""
        function_name = function_call.function.name
        arguments = json.loads(function_call.function.arguments)

        if function_name == "get_weather":
            weather_data = asyncio.run(self._execute_weather_function())
            return "\n".join(weather_data)
            
        elif function_name == "get_sleep_data":
            sleep_data = self.fitbit_api.get_sleep_data()
            
            if sleep_data:
                # Formatiere die Schlafdaten in einen lesbaren String
                summary = []
                summary.append("Sleep Summary for last night:")
                summary.append(f"Total Sleep Time: {sleep_data.get('totalMinutesAsleep', 0)} minutes")
                summary.append(f"Total Time in Bed: {sleep_data.get('totalTimeInBed', 0)} minutes")
                summary.append(f"Sleep Efficiency: {sleep_data.get('efficiency', 0)}%")
                
                # Füge Details zu den verschiedenen Schlafphasen hinzu, falls vorhanden
                stages = sleep_data.get('stages', {})
                if stages:
                    summary.append("\nSleep Stages:")
                    for stage, minutes in stages.items():
                        summary.append(f"- {stage}: {minutes} minutes")
                
                return "\n".join(summary)
            else:
                return "No sleep data available for the requested date."
        else:
            raise ValueError(f"Unknown function: {function_name}")

    def get_response(self, user_input):
        """Sendet den Text an OpenAI GPT mit Function Calling Support"""
        try:
            # Konversationsverlauf aufbauen
            messages = [{"role": "system", "content": self.system_prompt}]
            for user_msg, ai_msg in self.history:
                messages.append({"role": "user", "content": user_msg})
                messages.append({"role": "assistant", "content": ai_msg})
            
            messages.append({"role": "user", "content": user_input})

            # Erste Anfrage an das Modell
            response = self.openai.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools
            )

            assistant_message = response.choices[0].message
            
            # Prüfen ob Funktionen aufgerufen werden sollen
            if assistant_message.tool_calls:
                # Funktionsaufrufe ausführen und Ergebnisse sammeln
                for tool_call in assistant_message.tool_calls:
                    function_response = self._execute_function(tool_call)
                    
                    # Funktionsaufruf und Ergebnis zur Nachrichtenhistorie hinzufügen
                    messages.append(assistant_message)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": function_response
                    })

                # Zweite Anfrage mit den Funktionsergebnissen
                second_response = self.openai.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tools
                )
                
                final_response = second_response.choices[0].message.content
            else:
                final_response = assistant_message.content

            # Konversation zur Historie hinzufügen
            self.history.append((user_input, final_response))
            
            return final_response

        except Exception as e:
            print(f"❌ OpenAI request failed: {e}")
            return "An error occurred during processing."

    def speak_response(self, user_input):
        """Holt die GPT-Antwort und spricht sie aus"""
        response = self.get_response(user_input)
        self.tts.speak(response)