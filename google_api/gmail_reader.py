import os
import pickle
import base64
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

class GmailReader:
    """Klasse zum Abrufen ungelesener E-Mails aus der Gmail API"""

    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
    
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.credentials_file = os.path.join(base_dir, "credentials.json")
        self.token_file = os.path.join(base_dir, "token.pickle")
        self.service = self.get_gmail_service()
        
    def get_gmail_service(self):
        """Authentifiziert den Nutzer und gibt den Gmail-Service zurück"""
        creds = None

        if os.path.exists(self.token_file):
            with open(self.token_file, "rb") as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, self.SCOPES)
                creds = flow.run_local_server(port=0)

            with open(self.token_file, "wb") as token:
                pickle.dump(creds, token)

        return build("gmail", "v1", credentials=creds)

    def clean_email_content(self, content):
        """Entfernt überflüssige Leerzeilen aus dem E-Mail-Text"""
        lines = content.split("\n")
        cleaned_lines = [line.strip() for line in lines if line.strip()]
        return "\n".join(cleaned_lines)

    def get_email_content(self, msg):
        """Extrahiert den Text-Inhalt einer E-Mail und bereinigt ihn"""
        if "payload" not in msg:
            return "⚠️ Kein Inhalt gefunden."

        payload = msg["payload"]
        body = None

        if "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain":
                    body = part["body"].get("data")
                    break
        else:
            body = payload["body"].get("data")

        if body:
            decoded_content = base64.urlsafe_b64decode(body).decode("utf-8", errors="ignore")
            return self.clean_email_content(decoded_content)
        else:
            return "⚠️ Kein lesbarer Text gefunden."

    def list_primary_unread_messages(self, max_results=5):
        """Listet ungelesene E-Mails aus der Kategorie 'Allgemein' auf und gibt sie als String zurück"""
        query = "category:primary is:unread"
        results = self.service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
        messages = results.get("messages", [])

        if not messages:
            return "📭 Keine ungelesenen E-Mails in 'Allgemein' gefunden."

        output_parts = []
        for msg in messages:
            msg_data = self.service.users().messages().get(userId="me", id=msg["id"], format="full").execute()
            headers = msg_data["payload"]["headers"]

            subject = next((h["value"] for h in headers if h["name"] == "Subject"), "Kein Betreff")
            sender = next((h["value"] for h in headers if h["name"] == "From"), "Unbekannter Absender")
            date = next((h["value"] for h in headers if h["name"] == "Date"), "Kein Datum")
            content = self.get_email_content(msg_data)

            email_info = [
                f"Betreff: {subject}",
                f"Von: {sender}",
                f"Datum: {date}",
                f"Inhalt:\n{content}",
                "=" * 80
            ]
            output_parts.append("\n".join(email_info))

        return "\n".join(output_parts)

if __name__ == "__main__":
    reader = GmailReader()
    email_text = reader.list_primary_unread_messages(5)
    print(email_text)  # Nur zum Testen