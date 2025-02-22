from collections import deque
import json
from openai import OpenAI
from agents.tools.weather.weather_tool import WeatherTool
from agents.tools.fitbit.sleep_tool import SleepTool
from agents.tools.google.gmail_reader_tool import GmailReaderTool
from voice_generator import VoiceGenerator
from agents.spotify_player import SpotifyPlayer
from agents.notion_agent import NotionAgent

from agents.tools.core.tool_registry import ToolRegistry

class OpenAIChatAssistant:
    def __init__(self, voice="fable", model="gpt-4o-mini", history_limit=5):
        """Initialisiert den Chat-Assistenten mit OpenAI API, TTS und Function Calling"""
        self.openai = OpenAI()
        self.model = model
        self.tts = VoiceGenerator(voice=voice)
        self.history = deque(maxlen=history_limit)
        self.spotify_player = SpotifyPlayer()
        self.notion_agent = NotionAgent()
        
        self.tool_registry = ToolRegistry()

        # Definition der verfügbaren Funktionen für das Modell
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "play_song",
                    "description": "Plays a song on Spotify by searching for the specified track and artist.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The song title and optionally the artist. Example: 'Blinding Lights by The Weeknd'"
                            }
                        },
                        "required": ["query"],
                        "strict": True
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_notion_tasks",
                    "description": "Retrieves a list of tasks from the Notion database.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                        "additionalProperties": False
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "add_notion_task",
                    "description": "Adds a new task to the Notion database.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_name": {
                                "type": "string",
                                "description": "The name of the task to add to the Notion database."
                            }
                        },
                        "required": ["task_name"],
                        "strict": True
                    }
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
            "3. A Spotify function that lets you play music by searching for songs and artists.\n"
            "4. A Gmail function that fetches the latest unread emails from the primary inbox.\n"
            "5. A Notion function that can fetch a list of tasks from a database."
            "It can also add new tasks when requested."
            "When reporting emails, summarize key details: Subject, Sender, and Timestamp. "
            "Do not read entire emails unless explicitly requested."
        )
        
        self._initialize_tools()
        
    def _initialize_tools(self):
        """Initialize and register all available tools"""
        self.tool_registry.register_tool(WeatherTool())
        self.tool_registry.register_tool(SleepTool())
        self.tool_registry.register_tool(GmailReaderTool())

    def _execute_function(self, function_call):
        """Führt die aufgerufene Funktion aus und gibt das Ergebnis zurück"""
        function_name = function_call.function.name
        arguments = json.loads(function_call.function.arguments)

        if function_name == "play_song":
            query = arguments.get("query")
            if query:
                self.spotify_player.play_track(query)
                return f"Playing {query} on Spotify."
            return "No song specified."
        
        elif function_name == "get_notion_tasks":
            return self.notion_agent.get_database_entries_and_delete_completed()

        elif function_name == "add_notion_task":
            task_name = arguments.get("task_name")
            if task_name:
                self.notion_agent.add_database_entry(task_name)
                return f"Task '{task_name}' added to Notion."
            return "No task name provided."

        else:
            raise ValueError(f"Unknown function: {function_name}")

    async def get_response(self, user_input: str) -> str:
        """Sends text to OpenAI GPT with support for both legacy and new tools"""
        try:
            messages = [{"role": "system", "content": self.system_prompt}]
            for user_msg, ai_msg in self.history:
                messages.append({"role": "user", "content": user_msg})
                messages.append({"role": "assistant", "content": ai_msg})

            messages.append({"role": "user", "content": user_input})

            # Combine both legacy tools and new registry tools
            all_tools = [
                *self.tools,  # Legacy tools
                *self.tool_registry.get_all_definitions()
            ]

            response = self.openai.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=all_tools
            )

            assistant_message = response.choices[0].message

            if assistant_message.tool_calls:
                for tool_call in assistant_message.tool_calls:
                    # Try new registry first
                    tool = self.tool_registry.get_tool(tool_call.function.name)
                    print(tool)
                    if tool:
                        # Execute new-style tool
                        function_response = await tool.execute(
                            json.loads(tool_call.function.arguments)
                        )
                    else:
                        # Fall back to legacy tool execution
                        function_response = self._execute_function(tool_call)

                    messages.append(assistant_message)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": function_response
                    })

                # Get final response after tool execution
                second_response = self.openai.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=all_tools  # Use combined tools again
                )
                
                final_response = second_response.choices[0].message.content
            else:
                final_response = assistant_message.content

            self.history.append((user_input, final_response))
            return final_response

        except Exception as e:
            print(f"❌ OpenAI request failed: {e}")
            return "An error occurred during processing."

    async def speak_response(self, user_input):
        """Holt die GPT-Antwort und spricht sie aus"""
        response = await self.get_response(user_input)
        self.tts.speak(response)
