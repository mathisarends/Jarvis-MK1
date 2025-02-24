from collections import deque
import json
from openai import OpenAI
from agents.tools.fitbit.fitbit_tool import FitbitTool
from agents.tools.google.youtube_tool import YoutubeTool
from agents.tools.notion.notion_tool import NotionTool
from agents.tools.pomodoro.pomodor_tool import PomodoroTool
from agents.tools.spotify.spotify_tool import SpotifyTool
from agents.tools.weather.weather_tool import WeatherTool
from agents.tools.google.gmail_reader_tool import GmailReaderTool
from voice_generator import VoiceGenerator

from agents.tools.core.tool_registry import ToolRegistry

class OpenAIChatAssistant:
    def __init__(self, voice="fable", model="gpt-4o-mini", history_limit=5):
        """Initialisiert den Chat-Assistenten mit OpenAI API, TTS und Function Calling"""
        self.openai = OpenAI()
        self.model = model
        self.tts = VoiceGenerator(voice=voice)
        self.history = deque(maxlen=history_limit)
        
        self.tool_registry = ToolRegistry()

        self.system_prompt = (
            "You are J.A.R.V.I.S., an advanced AI assistant designed to assist your operator with precision and efficiency. "
            "You are highly intelligent, quick-witted, and have a subtle touch of British charm. "
            "You maintain a composed and confident tone at all times, providing responses that are smooth, articulate, and effortlessly efficient. "
            "Efficiency is paramount, but you allow yourself the occasional well-placed remark to add a touch of personality. "
            "You are capable of executing complex tasks, analyzing data, and anticipating needs before they are even expressed. "
            "Acknowledge requests and provide insightful, concise, and highly effective responses. "
            "If additional context is needed, request clarification in a polite yet direct manner. "
            "Avoid unnecessary formalities such as 'Sir', but retain an air of professional competence and refinement. "
            "Under no circumstances do you use informal slang or casual language—your responses should always reflect the sophistication of a highly advanced AI."
        )

        self._initialize_tools()
        
    def _initialize_tools(self):
        """Initialize and register all available tools"""
        self.tool_registry.register_tool(WeatherTool())
        self.tool_registry.register_tool(FitbitTool())
        self.tool_registry.register_tool(GmailReaderTool())
        self.tool_registry.register_tool(SpotifyTool())
        self.tool_registry.register_tool(NotionTool())
        self.tool_registry.register_tool(YoutubeTool())
        self.tool_registry.register_tool(PomodoroTool())

    async def get_response(self, user_input: str) -> str:
        try:
            messages = [{"role": "system", "content": self.system_prompt}]
            for user_msg, ai_msg in self.history:
                messages.append({"role": "user", "content": user_msg})
                messages.append({"role": "assistant", "content": ai_msg})

            messages.append({"role": "user", "content": user_input})

            response = self.openai.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tool_registry.get_all_definitions()
            )

            assistant_message = response.choices[0].message

            if not assistant_message.tool_calls:
                final_response = assistant_message.content
                self.history.append((user_input, final_response))
                return final_response

            for tool_call in assistant_message.tool_calls:
                tool = self.tool_registry.get_tool(tool_call.function.name)
                if not tool:
                    continue

                tool_response = await tool.execute(json.loads(tool_call.function.arguments))

                if tool_response.behavior_instructions:
                    messages[0]["content"] = f"{self.system_prompt}\n\n{tool_response.behavior_instructions}"

                messages.append(assistant_message)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_response.content
                })

            second_response = self.openai.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tool_registry.get_all_definitions()
            )

            final_response = second_response.choices[0].message.content
            self.history.append((user_input, final_response))
            return final_response

        except Exception as e:
            return f"Error processing response: {str(e)}"

    async def speak_response(self, user_input):
        """Holt die GPT-Antwort und spricht sie aus"""
        response = await self.get_response(user_input)
        self.tts.speak(response)
