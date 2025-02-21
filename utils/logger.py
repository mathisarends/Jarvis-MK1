import logging
import sys

def setup_global_logging(log_file="app.log"):
    """Richtet globales Logging für das gesamte Projekt ein."""
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),  
            logging.StreamHandler(sys.stdout)  
        ]
    )

    # Aktiviert detailliertes Logging für alle HTTP-Requests (requests -> urllib3)
    logging.getLogger("urllib3").setLevel(logging.DEBUG)

    logging.getLogger("requests").setLevel(logging.DEBUG)

    logging.info("📜 Globales Logging eingerichtet!")

    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)


setup_global_logging()

