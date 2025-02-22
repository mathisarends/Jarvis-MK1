import json

class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register_tool(self, name, handler):
        self.tools[name] = handler

    def execute(self, function_call):
        function_name = function_call.function.name
        arguments = json.loads(function_call.function.arguments)

        if function_name in self.tools:
            return self.tools[function_name](arguments)
        
        raise ValueError(f"Unknown function: {function_name}")
