from agents.tools.pomodoro.commands.pomodoro_command import PomodoroCommand

class StopPomodoroCommand(PomodoroCommand):
    def execute(self, pomodoro_tool, **kwargs) -> str:
        if not pomodoro_tool.pomodoro_timer or not pomodoro_tool.pomodoro_timer.running:
            return "No active Pomodoro timer to stop."
        pomodoro_tool.pomodoro_timer.stop()
        return "Pomodoro timer stopped."