import logging
import sys

# TODO: Den hier auch wirklich für das logging überall verwenden
def setup_global_logging(log_file="app.log"):
    """Richtet globales Logging für das gesamte Projekt ein."""
    
    # 🚀 Entfernt doppelte Handler
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(
        level=logging.INFO,  
        format="%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(log_file),  
            logging.StreamHandler(sys.stdout)  
        ]
    )

    # Aktiviert detailliertes Logging für HTTP-Requests (requests -> urllib3)
    logging.getLogger("urllib3").setLevel(logging.DEBUG)
    logging.getLogger("requests").setLevel(logging.DEBUG)

    logging.info("📜 Globales Logging eingerichtet!")

    # Reduziert unnötige Logs von Drittanbieter-Bibliotheken
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)

setup_global_logging()