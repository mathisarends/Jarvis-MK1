import os
import uuid
from openai import OpenAI
from io import BytesIO

class TTSFileGenerator:
    def __init__(self, voice="nova", output_dir="tts_output"):
        """Initialisiert den TTS-Dateigenerator mit OpenAI API und definiert das Ausgabe-Verzeichnis."""
        self.openai = OpenAI()
        self.voice = voice
        self.output_dir = output_dir
        
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_speech_file(self, text, category="general", file_format="mp3"):
        """Erstellt eine Sprachdatei aus dem gegebenen Text und speichert sie im entsprechenden Unterordner."""
        if not text.strip():
            raise ValueError("Der eingegebene Text ist leer.")
        
        try:
            category_dir = os.path.join(self.output_dir, category)
            os.makedirs(category_dir, exist_ok=True)
            
            unique_id = str(uuid.uuid4())[:8]
            file_name = f"tts_{unique_id}.{file_format}"
            file_path = os.path.join(category_dir, file_name)
            
            response = self.openai.audio.speech.create(
                model="tts-1",
                voice=self.voice,
                input=text
            )
            
            with open(file_path, "wb") as file:
                file.write(response.content)
            
            print(f"✅ Sprachdatei gespeichert: {file_path}")
            return file_path
        
        except Exception as e:
            print(f"❌ Fehler bei der Sprachgenerierung: {e}")
            return None

if __name__ == "__main__":
    tts = TTSFileGenerator()

    # Clipboard
    tts.generate_speech_file("Selbstverständlich. Text in Zwischenablage kopiert.", category="clipboard")
    tts.generate_speech_file("Bestätigung: Inhalt zur Zwischenablage hinzugefügt.", category="clipboard")
    tts.generate_speech_file("Verstanden. Die Informationen wurden zum temporären Speicherort transferiert.", category="clipboard")
    tts.generate_speech_file("Anfrage bearbeitet: Die Zwischenablage wurde mit dem gewünschten Text aktualisiert.", category="clipboard")
    tts.generate_speech_file("Verstanden. Die Textdaten sind nun für weitere Operationen im Zwischenspeicher verfügbar.", category="clipboard")

    # TODO: Elemente
    tts.generate_speech_file("Zustimmung. Das angegebene TODO-Element ist nun in der Datenbank hinterlegt.", category="todo")
    tts.generate_speech_file("Operation erfolgreich: Das TODO wurde dem Verzeichnis der ausstehenden Aufgaben hinzugefügt.", category="todo")
    tts.generate_speech_file("Die Speicherung des TODO-Elements wurde abgeschlossen. Die Aufgabe ist nun in Ihrem persönlichen Aufgabenbereich verfügbar", category="todo")
    tts.generate_speech_file("Bestätigung: Das neue TODO-Element wurde erfolgreich in das System integriert.", category="todo")

    # Second Brain
    tts.generate_speech_file("Selbstverständlich. Die Informationen wurden in Ihrem Second Brain archiviert.", category="second_brain")
    tts.generate_speech_file("Bestätigung: Das Element wurde erfolgreich in Ihr Wissensmanagement-System integriert.", category="second_brain")
    tts.generate_speech_file("Operation erfolgreich: Der Eintrag wurde Ihrer persönlichen Wissensdatenbank hinzugefügt.", category="second_brain")
    tts.generate_speech_file("Anfrage bearbeitet: Das selektierte Material wurde in Ihr persönliches Wissensarchiv einsortiert.", category="second_brain")

    # Ideen
    tts.generate_speech_file("Selbstverständlich. Ihre Idee wurde in der Datenbank für zukünftige Referenz gesichert.", category="ideen")
    tts.generate_speech_file("Operation erfolgreich: Der Ideeneintrag wurde Ihrer Sammlung kreativer Konzepte hinzugefügt.", category="ideen")
    tts.generate_speech_file("Eintragung bestätigt. Das Ideen-Element wurde Ihrem persönlichen Ideenarchiv hinzugefügt und zur Analyse vorbereitet.", category="ideen")
    tts.generate_speech_file("Gemäß Ihrer Eingabe wurde der Ideenvorschlag in das System für Ideengenerierung und -management transferiert.", category="ideen")
