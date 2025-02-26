from agents.tools.pomodoro.commands.pomodoro_command import PomodoroCommand

class StatusPomodoroCommand(PomodoroCommand):
    def execute(self, pomodoro_tool, **kwargs) -> str:
        if not pomodoro_tool.pomodoro_timer or not pomodoro_tool.pomodoro_timer.running:
            return "No active Pomodoro timer."
        return pomodoro_tool.pomodoro_timer.get_remaining_time()