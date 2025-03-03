from gpiozero import LED
from pixel_ring import pixel_ring
import threading


class PixelRingController:
    _instance = None
    _lock = threading.Lock()  

    def __new__(cls, power_pin=5, brightness=10):
        """Stellt sicher, dass nur eine Instanz existiert (Singleton)."""
        with cls._lock:  
            if cls._instance is None:
                cls._instance = super(PixelRingController, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self, power_pin=5, brightness=10):
        """Initialisiert den PixelRing nur einmal."""
        if not self._initialized:
            self.power = LED(power_pin)
            self.power.on()
            self.pixel_ring = pixel_ring
            self.pixel_ring.set_brightness(brightness)
            self._initialized = True  
            print("PixelRingController initialized.")

    def wakeup(self):
        self.pixel_ring.wakeup()

    def think(self):
        self.pixel_ring.think()

    def speak(self):
        self.pixel_ring.speak()

    def off(self):
        self.pixel_ring.off()

    def cleanup(self):
        self.pixel_ring.off()
        self.power.off()
        print("Cleanup done. PixelRing and power off.")
