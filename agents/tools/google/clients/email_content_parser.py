import base64
from bs4 import BeautifulSoup

class EmailContentParser:
    """Hilfsklasse zum Dekodieren und Extrahieren von E-Mail-Inhalten"""

    @staticmethod
    def parse_email_content(msg):
        """Extrahiert den Klartext einer E-Mail (bevorzugt `text/plain`, sonst bereinigtes `text/html`)."""
        payload = msg.get("payload", {})

        plain_text = EmailContentParser._get_text_part(payload, "text/plain")
        if plain_text:
            return plain_text

        html_text = EmailContentParser._get_text_part(payload, "text/html")
        if html_text:
            return EmailContentParser._html_to_text(html_text)

        return "⚠️ Kein lesbarer Text gefunden."

    @staticmethod
    def _get_text_part(payload, mime_type):
        """Sucht nach einer `text/plain` oder `text/html` Nachricht und dekodiert sie."""
        if payload.get("mimeType") == mime_type and "body" in payload:
            return EmailContentParser._decode_base64(payload["body"].get("data"))

        # Falls multipart: Durchsuche alle Teile
        for part in payload.get("parts", []):
            if part.get("mimeType") == mime_type:
                return EmailContentParser._decode_base64(part["body"].get("data"))

        return None

    @staticmethod
    def _decode_base64(body_data):
        """Dekodiert Base64-kodierten Text."""
        if not body_data:
            return None
        try:
            return base64.urlsafe_b64decode(body_data).decode("utf-8", errors="ignore").strip()
        except Exception:
            return None

    @staticmethod
    def _html_to_text(html_content):
        """Wandelt HTML in reinen Text um, entfernt unnötige Inhalte."""
        soup = BeautifulSoup(html_content, "html.parser")

        # Entferne unnötige HTML-Tags
        for tag in soup(["style", "script", "footer", "nav", "img"]):
            tag.decompose()

        # Extrahiere nur den reinen Text
        return soup.get_text(separator="\n", strip=True)
