from collections import deque
from datetime import datetime
import json
import re
import traceback
from openai import OpenAI
from agents.tools.core.tool_factory import ToolFactory
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
        """
        Streamt die Antwort vom API und verarbeitet sie in optimierten Chunks für TTS.
        
        Verwendet natürliche Sprachpausen für die Segmentierung, mit Präferenz für:
        1. Vollständige Sätze
        2. Logische Sprachteileinheiten
        3. Optimale Chunk-Größen für beste Audioqualität
        """
        
        MIN_CHUNK_SIZE = 80
        OPTIMAL_CHUNK_SIZE = 150
        MAX_CHUNK_SIZE = 250
        
        # Natürliche Unterbrechungsmuster in Präferenzreihenfolge
        BREAK_PATTERNS = [
            r'(?<=[.!?])\s+(?=[A-Z"„\'])',
            r'(?<=[.!?])\s+',
            r'(?<=[:;])\s+',
            r'(?<=,)\s+(?=[und|oder|aber|denn|sondern|weil|dass|wenn])',
            r'(?<=,)\s+',
            r'(?<=–|—)\s+',
            r'\n+',
        ]
        
        try:
            stream = self._create_chat_stream(messages)
            
            full_response = ""
            buffer = ""
            processed_segments = set()
            
            for chunk in stream:
                delta_content = self._extract_delta_content(chunk)
                if not delta_content:
                    continue
                    
                buffer += delta_content
                full_response += delta_content
                
                if len(buffer) < MIN_CHUNK_SIZE:
                    continue
                    
                buffer = self._process_buffer(buffer, processed_segments, 
                                            MIN_CHUNK_SIZE, OPTIMAL_CHUNK_SIZE, 
                                            MAX_CHUNK_SIZE, BREAK_PATTERNS)
            
            self._process_remaining_buffer(buffer, processed_segments)
            
            self.history.append((messages[-1]["content"], full_response))
            
            return full_response
            
        except Exception as e:
            error_message = f"❌ Fehler: {str(e)}"
            detailed_trace = traceback.format_exc()  # Stacktrace erfassen
            print(error_message)
            print(detailed_trace)  # Stacktrace in die Konsole ausgeben
            return f"{error_message}\n{detailed_trace}"


    def _create_chat_stream(self, messages):
        """Erstellt den Chat-Stream mit der OpenAI API"""
        return self.openai.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True
        )

    def _extract_delta_content(self, chunk):
        if not hasattr(chunk.choices[0].delta, 'content') or chunk.choices[0].delta.content is None:
            return None
        return chunk.choices[0].delta.content

    def _process_buffer(self, buffer, processed_segments, min_size, optimal_size, max_size, break_patterns):
        if len(buffer) < optimal_size:
            return buffer
        
        chunk_text, new_buffer = self._find_optimal_chunk(buffer, min_size, optimal_size, 
                                                        max_size, break_patterns)
        
        if chunk_text and chunk_text not in processed_segments:
            processed_segments.add(chunk_text)
            self.tts.speak(chunk_text)
        
        return new_buffer

    def _find_optimal_chunk(self, text, min_size, optimal_size, max_size, break_patterns):
        for pattern in break_patterns:
            matches = list(re.finditer(pattern, text))
            optimal_matches = [m for m in matches if m.end() >= min_size]
            
            if optimal_matches:
                best_match = self._select_best_match(optimal_matches, optimal_size)
                split_pos = best_match.end()
                
                return text[:split_pos].strip(), text[split_pos:]
        
        if len(text) > max_size:
            last_space = text.rfind(' ', min_size, max_size)
            if last_space > min_size:
                return text[:last_space].strip(), text[last_space:].lstrip()
        
        return None, text

    def _select_best_match(self, matches, optimal_size):
        best_match = None
        best_distance = float('inf')
        
        for match in matches:
            distance = abs(match.end() - optimal_size)
            if distance < best_distance:
                best_distance = distance
                best_match = match
        
        return best_match

    def _process_remaining_buffer(self, buffer, processed_segments):
        remaining_text = buffer.strip()
        if remaining_text and remaining_text not in processed_segments:
            self.tts.speak(remaining_text)
        
    async def speak_response(self, user_input):
        """Gets a streaming response and speaks it sentence by sentence"""
        response = await self.get_streaming_response(user_input)
        return response