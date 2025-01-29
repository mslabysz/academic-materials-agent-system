from datetime import datetime

class VersionedNotesStorage:
    """
    Prosty magazyn notatek w pamięci.
    Każda wersja notatek jest zapisywana w liście (versions).
    """
    def __init__(self):
        self.versions = []

    def add_version(self, notes_content: str, feedback_applied: str = ""):
        version_id = len(self.versions) + 1
        self.versions.append({
            "version_id": version_id,
            "notes_content": notes_content,
            "timestamp": datetime.now().isoformat(),
            "feedback_applied": feedback_applied
        })
    
    def get_latest_version(self) -> dict:
        if not self.versions:
            return {}
        return self.versions[-1]
    
    def get_all_versions(self) -> list:
        return self.versions

    def has_versions(self) -> bool:
        """Sprawdza czy są jakieś zapisane wersje"""
        return len(self.versions) > 0
