from agents.note_taking_agent import NoteTakingAgent
from agents.review_agent import ReviewAgent
from agents.translation_agent import TranslationAgent
from agents.workflow import create_notes_workflow, AgentState
from storage.storage import VersionedNotesStorage
from agents.state import AgentState  # W każdym pliku agenta

class ManagerAgent:
    """
    Główny 'SUPERVISOR'. Odpowiada za:
    - przechowywanie transkrypcji,
    - wywoływanie NoteTaking i Review,
    - przechowywanie historii notatek (VersionedNotesStorage),
    - koordynację całego procesu.
    """
    def __init__(self, model_name="gpt-4o"):
        # Inicjalizacja agentów
        self.note_taking_agent = NoteTakingAgent(model_name)
        self.review_agent = ReviewAgent(model_name)
        self.translation_agent = TranslationAgent()
        
        # Inicjalizacja workflow i storage
        self.workflow = create_notes_workflow(model_name)
        self.storage = VersionedNotesStorage()
        self.transcript = None

    def set_transcript(self, transcript: str):
        """Ustawia transkrypcję do przetworzenia"""
        self.transcript = transcript

    def generate_notes(self, note_type: str, target_lang: str, additional_instructions: str = "") -> str:
        """
        Generuje notatki używając workflow LangGraph
        """
        if not self.transcript:
            raise ValueError("Brak transkrypcji. Najpierw ustaw transkrypcję (set_transcript).")

        # Przygotowanie stanu początkowego
        initial_state: AgentState = {
            "messages": [],
            "transcript": self.transcript,
            "notes": "",
            "feedback": "",
            "additional_instructions": additional_instructions,
            "target_language": target_lang,
            "note_type": note_type,
            "status": "started",
            "changes": "",
            "error": None
        }

        # Uruchomienie workflow
        try:
            final_state = self.workflow.invoke(initial_state)
            
            # Sprawdzenie czy nie wystąpił błąd
            if final_state.get("error"):
                raise ValueError(f"Błąd w workflow: {final_state['error']}")
            
            # Zapisanie wyniku
            self.storage.add_version(final_state["notes"])
            return final_state["notes"]
            
        except Exception as e:
            print(f"[ManagerAgent] Wystąpił błąd: {str(e)}")
            raise

    def refine_notes(self, feedback: str) -> tuple[str, str]:
        """
        Poprawia notatki na podstawie feedbacku
        """
        if not self.storage.has_versions():
            raise ValueError("Brak notatek do poprawienia.")

        current_notes = self.storage.get_latest_version()
        
        # Przygotowanie stanu dla workflow
        state: AgentState = {
            "messages": [],
            "transcript": self.transcript,
            "notes": current_notes,
            "feedback": feedback,
            "target_language": "polski",  # Domyślnie nie tłumaczymy przy poprawkach
            "note_type": "review",
            "status": "review_started",
            "changes": "",
            "error": None
        }

        # Uruchomienie workflow tylko dla review
        try:
            final_state = self.review_agent(state)
            
            if final_state.get("error"):
                raise ValueError(f"Błąd w review: {final_state['error']}")
            
            # Zapisanie wyniku
            self.storage.add_version(final_state["notes"])
            return final_state["notes"], final_state["changes"]
            
        except Exception as e:
            print(f"[ManagerAgent] Wystąpił błąd podczas poprawiania: {str(e)}")
            raise

    def get_notes_history(self) -> list:
        """Zwraca historię wersji notatek"""
        return self.storage.get_all_versions()

    def get_translation_metrics(self, target_lang: str) -> dict:
        """Returns translation model metrics for specified language"""
        return self.translation_agent.evaluate_model(target_lang)
