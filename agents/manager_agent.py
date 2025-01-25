from agents.note_taking_agent import NoteTakingAgent
from agents.review_agent import ReviewAgent
from agents.translation_agent import TranslationAgent
from storage.storage import VersionedNotesStorage

class ManagerAgent:
    """
    Główny 'zarządca'. Odpowiada za:
    - przechowywanie transkrypcji,
    - wywoływanie NoteTaking i Review,
    - przechowywanie historii notatek (VersionedNotesStorage),
    - koordynację całego procesu.
    """
    def __init__(self, model_name="gpt-4o"):
        self.note_taking_agent = NoteTakingAgent(model_name)
        self.review_agent = ReviewAgent(model_name)
        self.translation_agent = TranslationAgent()
        self.storage = VersionedNotesStorage()
        self.transcript = None
        self.has_transcript = False

    def set_transcript(self, transcript: str):
        """Ustawia transkrypcję i aktualizuje flage."""
        self.transcript = transcript
        self.has_transcript = True
        print("[ManagerAgent] Zapisano nową transkrypcję")

    def has_valid_transcript(self) -> bool:
        """Sprawdza czy jest dostępna transkrypcja."""
        return self.has_transcript

    def generate_notes(self, note_type: str, target_lang: str, additional_instructions: str = "") -> str:
        if not self.transcript:
            raise ValueError("Brak transkrypcji. Najpierw ustaw transkrypcję (set_transcript).")
        
        print(f"\n[ManagerAgent] Rozpoczynam proces generowania notatek typu: {note_type}")
        notes = self.note_taking_agent.run(
            transcript=self.transcript,
            note_type=note_type,
            additional_instructions=additional_instructions
        )
        if target_lang != "polski":
            lang_code = {
                "english": "en",
                "español": "es"
            }.get(target_lang)

            if lang_code:
                print(f"[ManagerAgent] Rozpoczynam tłumaczenie na język: {target_lang}")
                notes = self.translation_agent.translate(notes, lang_code)
                print("[ManagerAgent] Zakończono tłumaczenie")

        self.storage.add_version(notes)
        print("[ManagerAgent] Zapisano nową wersję notatek")
        return notes

    def refine_notes(self, feedback: str) -> tuple[str, str]:
        if not self.transcript:
            raise ValueError("Brak transkrypcji. Najpierw ustaw transkrypcję (set_transcript).")

        print("\n[ManagerAgent] Rozpoczynam proces poprawiania notatek")
        current_version = self.storage.get_latest_version()
        if not current_version:
            raise ValueError("Brak notatek do poprawy. Najpierw wygeneruj notatki.")
        
        current_notes = current_version["notes_content"]
        refined_notes, changes_description = self.review_agent.refine_notes(
            transcript=self.transcript,
            current_notes=current_notes,
            feedback=feedback
        )
        self.storage.add_version(refined_notes, feedback_applied=feedback)
        print("[ManagerAgent] Zapisano nową wersję poprawionych notatek")
        return refined_notes, changes_description

    def get_latest_notes(self) -> str:
        latest = self.storage.get_latest_version()
        return latest.get("notes_content", "")

    def get_notes_history(self) -> list:
        return self.storage.get_all_versions()
