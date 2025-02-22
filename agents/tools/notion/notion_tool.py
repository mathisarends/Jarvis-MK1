from typing import Dict, Any
from agents.tools.core.tool_definition import ToolDefinition
from agents.tools.core.tool_parameter import ToolParameter
from agents.tools.core.tool_registry import Tool
from agents.tools.core.tool_response import ToolResponse
from agents.tools.notion.notion_client import NotionClient


class NotionTool(Tool):
    def __init__(self):
        self.notion_agent = NotionClient()
        super().__init__()

    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="notion",
            description="Manage tasks in Notion database including retrieving and adding tasks.",
            parameters={
                "action": ToolParameter(
                    type="string",
                    description="The action to perform: 'get_tasks' or 'add_task'",
                    required=True
                ),
                "task_name": ToolParameter(
                    type="string",
                    description="The name of the task to add (only required for add_task action)",
                    required=False
                )
            }
        )

    async def execute(self, parameters: Dict[str, Any]) -> ToolResponse:
        
        task_behavior = """
        When presenting task information:
        1. Analyze and prioritize tasks based on priority
        2. Suggest the next 2-3 most important tasks to focus on
        3. Use phrases like "I recommend focusing on..." or "Your priority tasks are..."
        4. If presenting multiple tasks, organize them in a clear, structured manner
        5. Consider task dependencies and project context in recommendations
        """
        
        try:
            action = parameters.get("action")
            
            if action == "get_tasks":
                tasks = self.notion_agent.get_database_entries_and_delete_completed()
                if not tasks:
                    return "No tasks found in Notion database."
                return ToolResponse(tasks, task_behavior)
                
            elif action == "add_task":
                task_name = parameters.get("task_name")
                if not task_name:
                    return "Error: task_name is required for add_task action"
                    
                self.notion_agent.add_database_entry(task_name)
                
                return ToolResponse(
                    f"Successfully added task: '{task_name}'",
                    task_behavior
                )
                
            else:
                return f"Error: Unknown action '{action}'. Supported actions are 'get_tasks' and 'add_task'."
                
        except Exception as e:
            return f"Error executing Notion tool: {str(e)}"