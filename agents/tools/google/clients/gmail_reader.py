from datetime import datetime, timedelta
import base64
import re
from bs4 import BeautifulSoup
from rapidfuzz import process, fuzz
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))
from agents.tools.google.core.google_auth import GoogleAuth


class GmailReader:
    """Klasse zum Abrufen und Verarbeiten von E-Mails aus der Gmail API."""

    MAX_RESULTS = 500  # Standardmäßig werden maximal 500 Ergebnisse abgerufen.
    USER_ID = "me"

    def __init__(self):
        self.service = GoogleAuth.get_service("gmail", "v1")

    def _get_messages(self, query: str, max_results: int = MAX_RESULTS):
        messages = []
        response = self.service.users().messages().list(userId=self.USER_ID, q=query, maxResults=max_results).execute()
        messages.extend(response.get("messages", []))

        while "nextPageToken" in response:
            response = self.service.users().messages().list(
                userId=self.USER_ID, q=query, maxResults=max_results, pageToken=response["nextPageToken"]
            ).execute()
            messages.extend(response.get("messages", []))

        return messages

    def _get_email_details(self, msg_id: str, format_type: str = "full"):
        return self.service.users().messages().get(userId=self.USER_ID, id=msg_id, format=format_type).execute()

    def get_email_content(self, msg):
        """Extrahiert den lesbaren Inhalt einer E-Mail (bevorzugt text/plain, sonst HTML)."""
        if "payload" not in msg:
            return "⚠️ Kein Inhalt gefunden."

        payload = msg["payload"]

        # Falls die Nachricht direkt im Body liegt (selten der Fall)
        if "body" in payload and payload["body"].get("data"):
            return self._decode_email_body(payload["body"]["data"])

        # Falls es eine multipart Nachricht ist
        if "parts" in payload:
            return self._extract_from_parts(payload["parts"])

        return "⚠️ Kein lesbarer Text gefunden."

    def _extract_from_parts(self, parts):
        """Geht rekursiv durch die E-Mail-Teile und sucht nach `text/plain` oder `text/html` als Fallback."""
        text_content = None
        html_content = None

        for part in parts:
            mime_type = part.get("mimeType", "")
            body_data = part.get("body", {}).get("data")

            if body_data:
                decoded_content = self._decode_email_body(body_data)

                if mime_type == "text/plain":
                    return decoded_content  # Direkt den ersten `text/plain` zurückgeben
                elif mime_type == "text/html":
                    html_content = decoded_content  # Falls kein `text/plain` existiert

            # Falls das aktuelle Part weitere `parts` enthält, rekursiv durchsuchen
            if "parts" in part:
                result = self._extract_from_parts(part["parts"])
                if result:
                    return result

        # Falls kein `text/plain` gefunden wurde, aber `text/html` existiert → Fallback
        if html_content:
            soup = BeautifulSoup(html_content, "html.parser")
            return soup.get_text(separator="\n").strip()

        return "⚠️ Kein lesbarer Text gefunden."

    def _decode_email_body(self, body_data):
        """Dekodiert Base64-kodierten E-Mail-Text."""
        try:
            decoded_content = base64.urlsafe_b64decode(body_data).decode("utf-8", errors="ignore")
            return decoded_content.strip() if decoded_content else "⚠️ Kein lesbarer Text gefunden."
        except Exception as e:
            return f"⚠️ Fehler beim Dekodieren: {str(e)}"

    @staticmethod
    def _clean_text(text: str):
        """Entfernt überflüssige Leerzeilen und leert führende und abschließende Leerzeichen."""
        return "\n".join(line.strip() for line in text.split("\n") if line.strip())

    @staticmethod
    def _extract_email_address(sender_string: str):
        match = re.search(r'<?([\w\.-]+@[\w\.-]+\.\w+)>?', sender_string)
        return match.group(1) if match else sender_string

    def get_unread_primary_emails(self, max_results: int = 5):
        messages = self._get_messages("category:primary is:unread", max_results)
        if not messages:
            return "📭 Keine ungelesenen E-Mails in 'Allgemein' gefunden."

        return "\n".join(self._format_email(msg["id"]) for msg in messages)

    def _format_email(self, msg_id: str):
        msg_data = self._get_email_details(msg_id)
        headers = msg_data["payload"]["headers"]

        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "Kein Betreff")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "Unbekannter Absender")
        date = next((h["value"] for h in headers if h["name"] == "Date"), "Kein Datum")
        content = self.get_email_content(msg_data)

        return f"Betreff: {subject}\nVon: {sender}\nDatum: {date}\nInhalt:\n{content}\n{'=' * 80}"
    
    def get_closest_sender(self, sender_name: str) -> str:
        """Findet die ähnlichste E-Mail-Adresse basierend auf dem eingegebenen Namen."""
        senders = self.get_senders_from_last_week()
        
        if not senders:
            return None

        sender_list = [email.strip("<>") for email in senders.split("\n") if "@" in email]

        closest_match = process.extractOne(sender_name, sender_list, scorer=fuzz.partial_ratio, score_cutoff=60)

        return closest_match[0] if closest_match else None

    def get_senders_from_last_week(self):
        one_week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y/%m/%d')
        messages = self._get_messages(f"after:{one_week_ago}")

        if not messages:
            return "📭 Keine E-Mails in der letzten Woche gefunden."

        sender_addresses = {
            self._extract_email_address(
                next((h["value"] for h in self._get_email_details(msg["id"], "metadata")["payload"]["headers"]
                      if h["name"] == "From"), "Unbekannter Absender")
            )
            for msg in messages
        }

        return self._format_sender_list(sender_addresses)

    @staticmethod
    def _format_sender_list(senders):
        if not senders:
            return "📭 Keine Absender gefunden."
        return f"📧 Gefundene Absender aus der letzten Woche ({len(senders)}):\n" + "\n".join(f"- {email}" for email in sorted(senders))

    def get_emails_from_sender(self, sender_email: str, days: int = 7):
        """Ruft E-Mails von einem bestimmten Absender in den letzten X Tagen ab."""
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y/%m/%d')
        messages = self._get_messages(f"from:{sender_email} after:{start_date}")

        if not messages:
            return f"📭 Keine E-Mails von {sender_email} in den letzten {days} Tagen gefunden."

        emails = [self._format_email(msg["id"]) for msg in messages]
        return f"📧 Gefundene E-Mails von {sender_email} (letzte {days} Tage):\n{'=' * 80}\n" + "\n".join(emails)


if __name__ == "__main__":
    gmail_reader = GmailReader()
    
    print(gmail_reader.get_unread_primary_emails())
    # print(gmail_reader.get_senders_from_last_week())
    # print(gmail_reader.get_emails_from_sender("mathisarends27@gmail.com"))
    
    # matched_sender  = gmail_reader.get_closest_sender("Mathis Ahrens")
    # result = gmail_reader.get_emails_from_sender(matched_sender)
    # print(result)
