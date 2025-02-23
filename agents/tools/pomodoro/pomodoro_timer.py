import time
import os
import sys
import random
import threading

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from voice_generator import VoiceGenerator

class PomodoroTimer:
    active_timer = None

    def __init__(self, duration_minutes):
        self.duration_seconds = duration_minutes * 60
        self.running = False
        self.voice_generator = VoiceGenerator()
        self.start_time = None
        self.responses = [
            "Ihr Pomodoro-Timer ist beendet. Möchten Sie eine neue Arbeitsphase starten?",
            "Die Konzentrationszeit ist vorbei. Jetzt ist eine kurze Pause angebracht!",
            "Ihr Fokustimer ist abgelaufen. Wollen Sie eine weitere Session beginnen?",
            "Pomodoro beendet! Zeit, sich kurz zu entspannen, bevor es weitergeht.",
            "Gut gemacht! Ihr Timer ist abgelaufen. Bereit für die nächste Runde?",
            "Exzellente Arbeit! Der Timer ist abgelaufen. Nutzen Sie die Pause sinnvoll.",
            "Die aktuelle Arbeitsphase ist abgeschlossen. Wie möchten Sie fortfahren?",
            "Ihr Pomodoro-Timer ist um. Soll ich eine weitere Sitzung für Sie starten?"
        ]

    def start(self):
        if PomodoroTimer.active_timer:
            print("Ein Timer läuft bereits! Möchtest du ihn abbrechen?")
            return

        PomodoroTimer.active_timer = self
        self.running = True
        self.start_time = time.time()
        print(f"Pomodoro-Timer gestartet für {self.duration_seconds // 60} Minuten.")
        threading.Timer(self.duration_seconds, self.play_alarm).start()
    
    def stop(self):
        if self.running:
            print("Pomodoro-Timer wurde gestoppt.")
            self.running = False
            PomodoroTimer.active_timer = None

    def play_alarm(self):
        print("Zeit ist um! Pomodoro beendet.")
        response = random.choice(self.responses)
        self.voice_generator.speak(response)
        PomodoroTimer.active_timer = None

    def get_remaining_time(self):
        if not self.running or self.start_time is None:
            return "Kein aktiver Timer."
        elapsed_time = time.time() - self.start_time
        remaining_time = max(0, self.duration_seconds - elapsed_time)
        return f"Verbleibende Zeit: {int(remaining_time // 60)} Minuten und {int(remaining_time % 60)} Sekunden."


if __name__ == "__main__":
    duration = int(input("Gib die Dauer des Pomodoro-Timers in Minuten ein: "))
    pomodoro = PomodoroTimer(duration)
    pomodoro.start()
