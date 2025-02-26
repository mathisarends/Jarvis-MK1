from agents.tools.pomodoro.commands.pomodoro_command import PomodoroCommand
from agents.tools.pomodoro.pomodoro_timer import PomodoroTimer

class StartPomodoroCommand(PomodoroCommand):
    def execute(self, pomodoro_tool, **kwargs) -> str:
        duration_minutes = kwargs.get("duration_minutes")
        if not duration_minutes:
            return "Error: 'duration_minutes' is required for starting a timer."
        elif pomodoro_tool.pomodoro_timer and pomodoro_tool.pomodoro_timer.running:
            return "A Pomodoro timer is already running. Stop it before starting a new one."
        else:
            pomodoro_tool.pomodoro_timer = PomodoroTimer(duration_minutes)
            pomodoro_tool.pomodoro_timer.start()
            return f"Pomodoro timer started for {duration_minutes} minutes."


class StopPomodoroCommand(PomodoroCommand):
    def execute(self, pomodoro_tool, **kwargs) -> str:
        if not pomodoro_tool.pomodoro_timer or not pomodoro_tool.pomodoro_timer.running:
            return "No active Pomodoro timer to stop."
        pomodoro_tool.pomodoro_timer.stop()
        return "Pomodoro timer stopped."


class StatusPomodoroCommand(PomodoroCommand):
    def execute(self, pomodoro_tool, **kwargs) -> str:
        if not pomodoro_tool.pomodoro_timer or not pomodoro_tool.pomodoro_timer.running:
            return "No active Pomodoro timer."
        return pomodoro_tool.pomodoro_timer.get_remaining_time()
