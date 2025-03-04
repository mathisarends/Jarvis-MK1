import random
from audio.sound_player import SoundPlayer

class StandardPhrasePlayer:
    @staticmethod
    def play_randomized_audio(template: str, x_range: tuple[int, int] = (1, 4)):
        """Ersetzt 'x' in der Vorlage mit einer zufälligen Zahl und spielt die Datei ab."""
        random_index = random.randint(*x_range)
        audio_path = template.replace("x", str(random_index))
        sound_player = SoundPlayer(audio_path)
        sound_player.play_audio()
        
    @staticmethod
    def play_volume_audio(self, volume: int):
        """
        Spielt die passende TTS-Datei für die aktuelle Lautstärke ab.
        :param volume: Lautstärke in Prozent (0-100, in 5er-Schritten).
        """
        # Rundet auf den nächsten 5er-Schritt
        rounded_volume = round(volume / 5) * 5
        filename = f"tts_volume_{rounded_volume}.mp3"
        sound_player = SoundPlayer(filename)
        sound_player.play_audio()