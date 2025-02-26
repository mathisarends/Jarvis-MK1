import sys
import os
import base64
from bs4 import BeautifulSoup

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))
from agents.tools.google.core.google_auth import GoogleAuth

class GmailReader:
    """Klasse zum Abrufen ungelesener E-Mails aus der Gmail API"""

    def __init__(self):
        self.service = GoogleAuth.get_service("gmail", "v1")

    def clean_email_content(self, content):
        lines = content.split("\n")
        cleaned_lines = [line.strip() for line in lines if line.strip()]
        return "\n".join(cleaned_lines)

    def get_email_content(self, msg):
        if "payload" not in msg:
            return "⚠️ Kein Inhalt gefunden."

        payload = msg["payload"]
        body = None
        mime_type = None

        if "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain":
                    body = part["body"].get("data")
                    mime_type = "text"
                    break
                elif part["mimeType"] == "text/html":
                    body = part["body"].get("data")
                    mime_type = "html"
        else:
            body = payload["body"].get("data")
            mime_type = payload["mimeType"]

        if body:
            decoded_content = base64.urlsafe_b64decode(body).decode("utf-8", errors="ignore")
            if mime_type == "text/html" or mime_type == "html":
                soup = BeautifulSoup(decoded_content, "html.parser")
                text_content = soup.get_text(separator="\n")
                return self.clean_email_content(text_content)
            else:
                return self.clean_email_content(decoded_content)

        return "⚠️ Kein lesbarer Text gefunden."

    def list_primary_unread_messages(self, max_results=5):
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

# Testlauf
if __name__ == "__main__":
    gmail_reader = GmailReader()
    print(gmail_reader.list_primary_unread_messages(5))