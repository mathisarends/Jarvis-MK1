import os

def find_project_root():
    """Sucht nach dem Root-Ordner des Projekts, indem nach typischen Projektdateien gesucht wird."""
    current_dir = os.getcwd()
    while current_dir != os.path.dirname(current_dir): 
        if ".git" in os.listdir(current_dir) or ".env" in os.listdir(current_dir):  
            return current_dir
        current_dir = os.path.dirname(current_dir)  
    return os.getcwd()  