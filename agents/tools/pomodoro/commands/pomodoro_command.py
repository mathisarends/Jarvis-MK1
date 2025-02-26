from abc import ABC, abstractmethod

class PomodoroCommand(ABC):
    @abstractmethod
    def execute(self, pomodoro_tool, **kwargs) -> str:
        pass
