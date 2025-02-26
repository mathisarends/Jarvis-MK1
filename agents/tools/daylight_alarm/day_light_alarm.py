import threading
import time
from datetime import datetime, timedelta

# Start on daylight alarm

class DayLightAlarm:
    def __init__(self, alarm_time: str, callback):
        """
        Erstellt einen nicht-blockierenden Wecker.
        
        :param alarm_time: Die Weckzeit im Format "HH:MM" (24-Stunden-Format).
        :param callback: Die Funktion, die ausgeführt wird, wenn der Wecker klingelt.
        """
        self.alarm_time = self._parse_time(alarm_time)
        self.callback = callback
        self.thread = threading.Thread(target=self._wait_for_alarm, daemon=True)
        self.running = True

    def _parse_time(self, alarm_time: str) -> datetime:
        now = datetime.now()
        alarm_datetime = datetime.strptime(alarm_time, "%H:%M").replace(year=now.year, month=now.month, day=now.day)

        if alarm_datetime < now:
            alarm_datetime += timedelta(days=1)
        
        return alarm_datetime

    def _wait_for_alarm(self):
        while self.running:
            now = datetime.now()
            if now >= self.alarm_time:
                self.callback()
                break
            time.sleep(1)  

    def start(self):
        self.thread.start()

    def cancel(self):
        self.running = False


if __name__ == "__main__":
    alarm = DayLightAlarm("6:59", lambda: print("Guten Morgen! Zeit aufzustehen! ☀️"))
    alarm.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Alarm abgebrochen.")



