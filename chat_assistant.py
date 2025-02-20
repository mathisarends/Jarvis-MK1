from collections import deque
from openai import OpenAI
from voice_generator import VoiceGenerator
from agents.weather_agent import WeatherClient
from agents.fitbit_agent import FitbitAPI

class OpenAIChatAssistant:
    def __init__(self, voice="sage", model="gpt-4o-mini", history_limit=5):
        """Initialisiert den Chat-Assistenten mit OpenAI API, TTS und Konversationsverlauf"""
        self.openai = OpenAI()
        self.model = model
        self.tts = VoiceGenerator(voice=voice)  
        self.weather_client = WeatherClient()

        # System-Prompt mit Anweisungen für das Verhalten
        self.system_prompt = (
            "You are Sage, a highly advanced AI assistant. "
            "Your responses should be as short as possible while still being informative. "
            "You have access to a weather function and can retrieve real-time weather data if necessary. "
            "When providing a weather update, always mention the city name and describe the weather throughout the day, "
            "taking the current time into account to make the response more relevant. "
        )

        self.history = deque(maxlen=history_limit)
        
        self.tools = [{
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
            },
        }]


    def get_response(self, user_input):
        """Sendet den Text an OpenAI GPT mit Function Calling Support"""
        try:
            # Konversationsverlauf aufbauen
            messages = [{"role": "system", "content": self.system_prompt}]
            for user_msg, ai_msg in self.history:
                messages.append({"role": "user", "content": user_msg})
                messages.append({"role": "assistant", "content": ai_msg})
            
            messages.append({"role": "user", "content": user_input})

            response = self.openai.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools
            )

            assistant_message = response.choices[0].message
            
            if assistant_message.tool_calls:
                for tool_call in assistant_message.tool_calls:
                    function_response = self._execute_function(tool_call)
                    
                    messages.append(assistant_message)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": function_response
                    })

                second_response = self.openai.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tools
                )
                
                final_response = second_response.choices[0].message.content
            else:
                final_response = assistant_message.content

            self.history.append((user_input, final_response))
            
            return final_response

        except Exception as e:
            print(f"❌ OpenAI request failed: {e}")
            return "An error occurred during processing."
    
    def _execute_function(self, function_call):
        """Führt die aufgerufene Funktion aus und gibt das Ergebnis zurück"""
        function_name = function_call.function.name

        if function_name == "get_weather":
            weather_data = self.weather_client.get_weather()
            return "\n".join(weather_data)
        else:
            raise ValueError(f"Unknown function: {function_name}")


    def speak_response(self, user_input):
        """Holt die GPT-Antwort und spricht sie aus"""
        response = self.get_response(user_input)
        self.tts.speak(response)
