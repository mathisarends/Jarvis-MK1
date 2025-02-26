from collections import deque
import json
import re
from openai import OpenAI
from agents.tools.fitbit.fitbit_tool import FitbitTool
from agents.tools.google.youtube_tool import YoutubeTool
from agents.tools.notion.tools.notion_clipboard_tool import NotionClipboardTool
from agents.tools.notion.tools.notion_idea_tool import NotionIdeaTool
from agents.tools.notion.tools.notion_todo_tool import NotionTodoTool
from agents.tools.pomodoro.pomodor_tool import PomodoroTool
from agents.tools.spotify.spotify_tool import SpotifyTool
from agents.tools.weather.weather_tool import WeatherTool
from agents.tools.google.gmail_reader_tool import GmailReaderTool
from voice_generator import VoiceGenerator
import re

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
        self.tool_registry.register_tool(YoutubeTool())
        self.tool_registry.register_tool(PomodoroTool())
        self.tool_registry.register_tool(NotionClipboardTool())
        self.tool_registry.register_tool(NotionIdeaTool())
        self.tool_registry.register_tool(NotionTodoTool())
    
    def _split_into_sentences(self, text):
        """Split text into sentences for better TTS streaming"""
        # Match sentence endings (period, question mark, exclamation mark)
        # followed by a space or end of string
        sentences = re.findall(r'[^.!?]+[.!?](?:\s|$)', text + ' ')
        
        # Handle any remaining text that might not end with punctuation
        remaining_text = text
        for sentence in sentences:
            remaining_text = remaining_text.replace(sentence, '', 1)
        
        if remaining_text.strip():
            sentences.append(remaining_text.strip())
            
        return [s.strip() for s in sentences if s.strip()]

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
    
    async def get_streaming_response(self, user_input: str):
        """Gets a streaming response from OpenAI for the final response"""
        try:
            # First handle any tool calls as before
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
                # For responses without tool calls, use streaming
                return self._stream_response(messages)

            # Handle tool calls
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
        """Streamt die Antwort und bereitet TTS mit optimierten Chunks vor"""
        try:
            stream = self.openai.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True
            )
            
            full_response = ""
            buffer = ""
            processed_segments = set()  
            
            MIN_CHUNK_SIZE = 80 
            OPTIMAL_CHUNK_SIZE = 150  
            MAX_CHUNK_SIZE = 250 
            

            break_patterns = [
                r'(?<=[.!?])\s+(?=[A-Z"„\'])',  
                r'(?<=[.!?])\s+',               
                r'(?<=[:;])\s+',                
                r'(?<=,)\s+(?=[und|oder|aber|denn|sondern|weil|dass|wenn])',  
                r'(?<=,)\s+',                   
                r'(?<=–|—)\s+',                 
                r'\n+',                         
            ]
            
            
            for chunk in stream:
                if not hasattr(chunk.choices[0].delta, 'content') or chunk.choices[0].delta.content is None:
                    continue
                    
                delta_content = chunk.choices[0].delta.content
                buffer += delta_content
                full_response += delta_content
                
                if len(buffer) < MIN_CHUNK_SIZE:
                    continue
                    
                # Suche nach natürlichen Bruchpunkten
                chunk_found = False
                
                # Prüfe erst, ob wir einen optimalen oder größeren Chunk haben können
                if len(buffer) >= OPTIMAL_CHUNK_SIZE:
                    for pattern in break_patterns:
                        # Suche nach Matches nach dem MIN_CHUNK_SIZE
                        matches = list(re.finditer(pattern, buffer))
                        
                        # Filtere Matches, die im optimalen Bereich liegen
                        optimal_matches = [m for m in matches if m.end() >= MIN_CHUNK_SIZE]
                        
                        if optimal_matches:
                            # Versuche einen Match nahe der optimalen Größe zu finden
                            best_match = None
                            best_distance = float('inf')
                            
                            for match in optimal_matches:
                                # Bevorzuge Matches, die näher an OPTIMAL_CHUNK_SIZE sind
                                distance = abs(match.end() - OPTIMAL_CHUNK_SIZE)
                                if distance < best_distance:
                                    best_distance = distance
                                    best_match = match
                            
                            if best_match:
                                split_pos = best_match.end()
                                chunk_text = buffer[:split_pos].strip()
                                
                                # Prüfe, ob es ein sinnvoller Chunk und kein Duplikat ist
                                if chunk_text and chunk_text not in processed_segments:
                                    processed_segments.add(chunk_text)
                                    self.tts.speak(chunk_text)
                                    
                                # Behalte den Rest im Buffer
                                buffer = buffer[split_pos:]
                                chunk_found = True
                                break
                
                # Wenn der Buffer zu groß wird, ohne einen Bruch zu finden, erzwinge einen Bruch
                if not chunk_found and len(buffer) > MAX_CHUNK_SIZE:
                    # Finde das letzte Leerzeichen nach MIN_CHUNK_SIZE
                    last_space = buffer.rfind(' ', MIN_CHUNK_SIZE, MAX_CHUNK_SIZE)
                    if last_space > MIN_CHUNK_SIZE:
                        chunk_text = buffer[:last_space].strip()
                        
                        # Verarbeite, wenn kein Duplikat
                        if chunk_text and chunk_text not in processed_segments:
                            processed_segments.add(chunk_text)
                            self.tts.speak(chunk_text)
                        
                        # Behalte den Rest im Buffer
                        buffer = buffer[last_space:].lstrip()
            
            # Verarbeite den restlichen Text im Buffer
            if buffer.strip() and buffer.strip() not in processed_segments:
                self.tts.speak(buffer.strip())
                
            # Füge zur History hinzu
            self.history.append((messages[-1]["content"], full_response))
            
            return full_response
            
        except Exception as e:
            error_message = f"Fehler beim Streamen der Antwort: {str(e)}"
            print(error_message)
            return error_message
        
    async def speak_response(self, user_input):
        """Gets a streaming response and speaks it sentence by sentence"""
        response = await self.get_streaming_response(user_input)
        return response