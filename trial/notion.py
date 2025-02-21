import os
import requests
from dotenv import load_dotenv

load_dotenv()


NOTION_TOKEN = os.getenv("NOTION_SECRET")
PAGE_ID = "608a67e42e3a469eb17925e8bf075a33"


HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def check_page_access():
    """Testet, ob die API Zugriff auf die Notion-Seite hat."""
    url = f"https://api.notion.com/v1/pages/{PAGE_ID}"
    
    response = requests.get(url, headers=HEADERS)
    
    print("Status-Code:", response.status_code)
    print("Antwort:", response.text)

# Test ausführen
check_page_access()