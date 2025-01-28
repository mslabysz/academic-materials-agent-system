from openai import OpenAI
from agents.note_taking_agent import NoteTakingAgent
from agents.review_agent import ReviewAgent
from agents.translation_agent import TranslationAgent
from storage.storage import VersionedNotesStorage
from agents.state import AgentState
from agents.base_agent import BaseAgent
from langgraph.graph import StateGraph

class ManagerAgent(BaseAgent):
    """
    Główny 'SUPERVISOR'. Odpowiada za:
    - przechowywanie transkrypcji,
    - wywoływanie NoteTaking i Review,
    - przechowywanie historii notatek (VersionedNotesStorage),
    - koordynację całego procesu.
    """
    def __init__(self, model_name="gpt-4o"):
        super().__init__("ManagerAgent", model_name)
        self.transcript = None
        self.storage = VersionedNotesStorage()
        
        # Inicjalizacja agentów
        self.note_taking_agent = NoteTakingAgent(model_name)
        self.review_agent = ReviewAgent(model_name)
        self.translation_agent = TranslationAgent()
        
        # Tworzenie workflow
        self.workflow = self.create_workflow()

<<<<<<< HEAD
    def create_workflow(self) -> StateGraph:
        """Tworzy graf przepływu pracy"""
        # Definiujemy dozwolone klucze do aktualizacji
        config = {
            "notes": "append",
            "status": "overwrite",
            "decision": "overwrite",
            "messages": "append",
            "memory": "append"
        }
        
        # Używamy dict zamiast AgentState
        workflow = StateGraph(dict, config)
        
        # Dodajemy węzły
        workflow.add_node("manager", self.process)
        workflow.add_node("note_taking", self.note_taking_agent)
        workflow.add_node("review", self.review_agent)
        workflow.add_node("translation", self.translation_agent)
        workflow.add_node("end", lambda x: x)
        
        # Dodajemy krawędzie warunkowe
        workflow.add_conditional_edges(
            "manager",
            lambda x: x["decision"],
            {
                "generuj": "note_taking",
                "popraw": "review",
                "tłumacz": "translation",
                "zakończ": "end"
            }
        )
        
        # Wszystkie agenty wracają do managera po wykonaniu zadania
        workflow.add_edge("note_taking", "manager")
        workflow.add_edge("review", "manager")
        workflow.add_edge("translation", "manager")
        
        workflow.set_entry_point("manager")
        workflow.set_finish_point("end")
        
        return workflow.compile()

    def process(self, state: dict) -> dict:
        """Główna logika managera"""
        print("\n[ManagerAgent] Analizuję stan i podejmuję decyzję...")

        notes_preview = str(state.get("notes", ""))[:200] + "..." if state.get("notes") else "brak"
        
        prompt = f"""Jako manager systemu, podejmij decyzję o następnym kroku na podstawie:

Stan: {state.get("status")}
Typ notatek: {state.get("note_type")}
Jest feedback: {'tak' if state.get("feedback") else 'nie'}
Język docelowy: {state.get("target_language")}
Obecne notatki: {notes_preview}

Aktualna sytuacja:
1. Czy notatki zostały już wygenerowane? {"tak" if state.get("notes") else "nie"}
2. Czy jest feedback do uwzględnienia? {"tak" if state.get("feedback") else "nie"}
3. Czy potrzebne tłumaczenie? {"tak" if state.get("target_language") != "polski" else "nie"}
4. Czy notatki były już poprawione? {"tak" if state.get("status") == "notes_reviewed" else "nie"}
5. Czy notatki były już tłumaczone? {"tak" if state.get("status") == "notes_translated" else "nie"}

Wybierz JEDNO działanie (odpowiedz TYLKO jednym słowem):
- generuj (gdy brak notatek)
- popraw (gdy jest feedback i notatki NIE były jeszcze poprawione)
- tłumacz (gdy potrzebne tłumaczenie i notatki NIE były jeszcze tłumaczone)
- zakończ (gdy wszystko gotowe lub notatki były już poprawione/tłumaczone)"""

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "Jesteś managerem systemu do generowania notatek. Jeśli notatki były już poprawione lub przetłumaczone, zawsze wybierz 'zakończ'."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        decision = response.choices[0].message.content.strip().lower()
        print(f"[ManagerAgent] Decyzja: {decision}")
        
        state["decision"] = decision
        return state
=======
    def has_valid_transcript(self) -> bool:
        """
        Sprawdza czy jest dostępna prawidłowa transkrypcja.
        """
        return bool(self.transcript and isinstance(self.transcript, str) and len(self.transcript.strip()) > 0)

    def set_transcript(self, transcript: str):
        """
        Ustawia transkrypcję do użycia przez agenta.
        """
        self.transcript = transcript
>>>>>>> f084a25 (metrics)

    def get_transcript(self) -> str:
        """
        Zwraca aktualną transkrypcję.
        """
        return self.transcript if self.has_valid_transcript() else ""

    def generate_notes(self, note_type: str, target_lang: str, additional_instructions: str = "") -> str:
        """Generuje notatki używając systemu agentowego"""
        if not self.transcript:
            raise ValueError("Brak transkrypcji.")

        initial_state = {
            "transcript": self.transcript,
            "note_type": note_type,
            "target_language": target_lang,
            "feedback": additional_instructions,
            "status": "started"
        }

        # Uruchamiamy workflow używając .invoke()
        final_state = self.workflow.invoke(initial_state)
        
        # Zapisujemy wygenerowane notatki
        if final_state["notes"]:
            self.storage.add_version(final_state["notes"])
        
        return final_state["notes"]

    def refine_notes(self, feedback: str) -> tuple[str, str]:
        """Poprawia notatki na podstawie feedbacku"""
        if not self.transcript:
            raise ValueError("Brak transkrypcji.")

        if not self.storage.has_versions():
            raise ValueError("Brak notatek do poprawienia.")

        latest = self.storage.get_latest_version()
        initial_state = {
            "transcript": self.transcript,
            "notes": latest["notes_content"] if isinstance(latest, dict) else latest,
            "feedback": feedback,
            "status": "review_started",
            "target_language": "polski",
            "note_type": "review",
            "messages": [],
            "memory": {},
            "decision": ""
        }

        # Uruchamiamy workflow używając .invoke()
        final_state = self.workflow.invoke(initial_state)
        
        # Zapisujemy poprawione notatki
        if final_state["notes"]:
            self.storage.add_version(final_state["notes"], feedback)
        
        changes = final_state.get("memory", {}).get("ReviewAgent", {}).get("changes", "")
        return final_state["notes"], changes

    def set_transcript(self, transcript: str):
        """Ustawia transkrypcję"""
        self.transcript = transcript

    def get_latest_notes(self) -> str:
        """Pobiera ostatnią wersję notatek"""
        return self.storage.get_latest_version()

    def get_notes_history(self) -> list[str]:
        """Pobiera historię notatek"""
        return self.storage.get_all_versions()

    def get_translation_metrics(self, target_lang: str) -> dict:
        """Returns translation model metrics for specified language"""
        return self.translation_agent.evaluate_model(target_lang)

    def get_latest_notes(self) -> str:
        """
        Pobiera najnowszą wersję notatek.
        """
        if not self.storage.has_versions():
            return ""
        
        latest = self.storage.get_latest_version()
        return latest.get("notes_content", "")
