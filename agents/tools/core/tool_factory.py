from agents.tools.fitbit.fitbit_tool import FitbitTool
from agents.tools.google.tools.gmail_emails_from_sender_tool import GmailEmailsFromSenderTool
from agents.tools.google.tools.gmail_reader_tool import GmailReaderTool
from agents.tools.google.tools.google_calendar_tool import GoogleCalendarTool
from agents.tools.google.tools.youtube_tool import YoutubeTool
from agents.tools.notion.tools.notion_clipboard_tool import NotionClipboardTool
from agents.tools.notion.tools.notion_idea_tool import NotionIdeaTool
from agents.tools.notion.tools.notion_second_brain_tool import NotionSecondBrainTool
from agents.tools.notion.tools.notion_todo_tool import NotionTodoTool
from agents.tools.pomodoro.pomodoro_tool import PomodoroTool
from agents.tools.spotify.spotify_tool import SpotifyTool
from agents.tools.volume_regulation.volume_control_tool import VolumeControlTool
from agents.tools.weather.weather_tool import WeatherTool

class ToolFactory:
    @staticmethod
    def create_notion_tools():
        return [
            NotionClipboardTool(),
            NotionIdeaTool(),
            NotionTodoTool(),
            NotionSecondBrainTool()
        ]
        
    @staticmethod
    def create_google_tools():
        return [
            GmailReaderTool(),
            GmailEmailsFromSenderTool(),
            GoogleCalendarTool(),
            YoutubeTool()
        ]
    
    @staticmethod
    def create_all_tools():
        tools = []
        tools.extend(ToolFactory.create_notion_tools())
        tools.extend(ToolFactory.create_google_tools())
        tools.append(WeatherTool())
        tools.append(FitbitTool())
        # tools.append(SpotifyTool())
        tools.append(PomodoroTool())
        tools.append(VolumeControlTool())
        return tools