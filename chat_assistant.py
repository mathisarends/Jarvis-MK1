from collections import deque
from datetime import datetime
import json
import traceback
from openai import OpenAI
from agents.tools.core.tool_factory import ToolFactory
from text_to_speech_streamer import TextToSpeechStreamer
from voice_generator import VoiceGenerator

from agents.tools.core.tool_registry import ToolRegistry

class OpenAIChatAssistant:
    def __init__(self, voice="fable", model="gpt-4o-mini", history_limit=5):
        """Initialisiert den Chat-Assistenten mit OpenAI API, TTS und Function Calling"""
        self.openai = OpenAI()
        self.model = model
        self.voice_generator = VoiceGenerator()
        self.tts_streamer = TextToSpeechStreamer(self.voice_generator)
        self.history = deque(maxlen=history_limit)
        
        self.tool_registry = ToolRegistry()

        self.system_prompt = (
            "Du bist Jarvis, eine fortschrittliche KI-Assistenz. "
            "Du kommunizierst ausschließlich auf Deutsch, es sei denn, es wird ausdrücklich nach Englisch gefragt. "
            "Deine Antworten sind für die Sprachausgabe optimiert – sie sind natürlich, flüssig und prägnant. "
            "Halte deine Sätze klar und strukturiert. Falls Kontext fehlt, frage direkt nach. "
            
            "Falls der Nutzer längere Texte diktiert oder von dir generieren lässt, wie eine Ideensammlung, einen E-Mail-Entwurf oder eine Einkaufsliste, "
            "schlage vor, diese im NotionClipboardTool zu speichern, falls gewünscht. "
            "Falls der Text eine konkrete Aufgabe enthält (z. B. eine To-Do-Liste oder Handlungsaufforderung), "
            "biete zusätzlich an, die relevanten Punkte direkt ins NotionTodoTool zu übertragen. "
            
            "Falls in einer Diskussion gute Ideen aufkommen, die es sich lohnt festzuhalten, "
            "schlage vor, diese im NotionIdeaTool zu speichern."
        )

        for tool in ToolFactory.create_all_tools():
            self.tool_registry.register_tool(tool)
        
        
    def get_system_prompt_with_current_date(self):
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        return (
            f"{self.system_prompt}\n\n"
            f"Note: The current date is {current_date}. "
            f"Use this as reference for any date-related reasoning."
        )
    
    async def get_streaming_response(self, user_input: str):
        """Gets a streaming response from OpenAI for the final response"""
        try:
            messages = [
                {"role": "system", "content": self.get_system_prompt_with_current_date()}
            ]
            
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
                return self._stream_response(messages)

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

            # After tool execution, use streaming for the final response
            return self._stream_response(messages)

        except Exception as e:
            return f"Error processing response: {str(e)}"
    
    def _stream_response(self, messages):
        try:
            stream = self.openai.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True
            )
            
            full_response = self.tts_streamer.process_openai_stream(stream)
            
            self.history.append((messages[-1]["content"], full_response))
            
            return full_response
            
        except Exception as e:
            error_message = f"❌ Fehler: {str(e)}"
            detailed_trace = traceback.format_exc()
            print(error_message)
            print(detailed_trace)
            return f"{error_message}\n{detailed_trace}"
        
    async def speak_response(self, user_input):
        """Gets a streaming response and speaks it sentence by sentence"""
        response = await self.get_streaming_response(user_input)
        return response