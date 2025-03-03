import os
import pyaudio
import queue
import time
from google.cloud import speech

class SpeechRecognition:
    def __init__(self, credentials_filename="credentials.json", language="de-DE", silence_timeout=5):
        """
        Initialisiert die Spracherkennungsklasse.

        :param credentials_filename: Name der Google Cloud Credential JSON-Datei
        :param language: Sprache für die Spracherkennung (z. B. "de-DE")
        :param silence_timeout: Zeit in Sekunden ohne erkannte Sprache, bevor die Aufnahme stoppt.
        """
        script_dir = os.path.dirname(os.path.abspath(__file__))
        credentials_path = os.path.join(script_dir, credentials_filename)

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        self.language = language
        self.client = speech.SpeechClient()
        self.audio_queue = queue.Queue()
        self.silence_timeout = silence_timeout

        self.config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code=self.language,
        )

        self.streaming_config = speech.StreamingRecognitionConfig(
            config=self.config, interim_results=True
        )

        self.stop_recording = False

    def _callback(self, in_data, frame_count, time_info, status):
        """Speichert eingehende Audiodaten in der Warteschlange."""
        self.audio_queue.put(in_data)
        return None, pyaudio.paContinue

    def _generate_audio(self):
        """Sendet Audiodaten an Google Speech API."""
        while not self.stop_recording:
            data = self.audio_queue.get()
            yield speech.StreamingRecognizeRequest(audio_content=data)

    def record_user_prompt(self):
        """
        Startet die Sprachaufnahme und gibt das endgültige Transkript zurück.

        :return: String mit dem erkannten Text.
        """
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=int(16000 / 10),
            stream_callback=self._callback,
        )

        print("🎤 Starte Aufnahme... Sprich jetzt!")

        responses = self.client.streaming_recognize(self.streaming_config, self._generate_audio())

        final_transcript = ""
        last_speech_time = time.time()

        for response in responses:
            if not response.results:
                continue

            for result in response.results:
                if result.is_final:
                    transcript = result.alternatives[0].transcript
                    print(f"📝 Finale Transkription: {transcript}")
                    final_transcript += transcript + " "
                    self.stop_recording = True  # Stoppen, sobald finale Transkription erkannt wurde
                    break  # Beende die innere Schleife

            if self.stop_recording:
                break  # Beende die äußere Schleife direkt

            # Falls keine finale Transkription kommt, checke den Timeout
            if time.time() - last_speech_time > self.silence_timeout:
                print("⏳ Keine Sprache erkannt, Aufnahme wird gestoppt.")
                self.stop_recording = True
                break

        stream.stop_stream()
        stream.close()
        p.terminate()

        return final_transcript.strip()


if __name__ == "__main__":
    recorder = SpeechRecognition()
    user_text = recorder.record_user_prompt()
    print(f"\n🎤 Endgültiges Ergebnis: {user_text}")
