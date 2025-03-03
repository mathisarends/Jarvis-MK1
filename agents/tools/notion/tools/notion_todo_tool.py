from typing import Dict, Any
from agents.tools.core.tool_definition import ToolDefinition
from agents.tools.core.tool_parameter import ToolParameter
from agents.tools.core.tool_registry import Tool
from agents.tools.core.tool_response import ToolResponse
from agents.tools.notion.managers.notion_todo_manager import NotionTodoManager

class NotionTodoTool(Tool):
    def __init__(self):
        self.todo_manager = NotionTodoManager()
        super().__init__()

    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="notion_todo",
            description="Manage tasks in the Notion To-Do database: add tasks, list all tasks, or list only top priority tasks.",
            parameters={
                "action": ToolParameter(
                    type="string",
                    description="Action to perform: 'get_tasks', 'get_daily_top_tasks' or 'add_task'.",
                    required=True
                ),
                "task_name": ToolParameter(
                    type="string",
                    description="The name of the task to add (only required for 'add_task' action).",
                    required=False
                )
            }
        )

    async def execute(self, parameters: Dict[str, Any]) -> ToolResponse:
        try:
            action = parameters.get("action")

            if action == "get_tasks":
                tasks = await self.todo_manager.get_all_todos()
                if not tasks:
                    return ToolResponse("No tasks found in Notion database.", "Your task list is empty.")
                return ToolResponse(tasks, "These are your current tasks.")

            if action == "get_daily_top_tasks":
                top_tasks = await self.todo_manager.get_daily_top_tasks()
                if not top_tasks:
                    return ToolResponse("No top-priority tasks found.", "You have no 'Daily Top Tasks' at the moment.")
                return ToolResponse(top_tasks, "Here are your 'Daily Top Tasks'.")

            if action == "add_task":
                task_name = parameters.get("task_name")
                if not task_name:
                    return ToolResponse("Error: 'task_name' is required for 'add_task'.", "You must provide a task name.")

                result = await self.todo_manager.add_todo(task_name)
                return ToolResponse(
                    f"Successfully added task: {result}",
                    "The task has been added to your Notion To-Do list.",
                    standard_response_audio_sub_path="./tts_output/todo/tts_todo_x.mp3"
                )

            return ToolResponse(f"Error: Unknown action '{action}'. Supported actions are 'get_tasks', 'get_daily_top_tasks', and 'add_task'.",
                                "Invalid action specified.")

        except Exception as e:
            return ToolResponse(f"Error executing NotionTodoTool: {str(e)}", "An error occurred while processing your request.")
