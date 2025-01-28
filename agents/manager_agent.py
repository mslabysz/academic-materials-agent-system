from openai import OpenAI
from agents.note_taking_agent import NoteTakingAgent
from agents.review_agent import ReviewAgent
from agents.translation_agent import TranslationAgent
from storage.storage import VersionedNotesStorage
from agents.state import AgentState

class ManagerAgent:
    """
    Główny 'SUPERVISOR'. Odpowiada za:
    - przechowywanie transkrypcji,
    - wywoływanie NoteTaking i Review,
    - przechowywanie historii notatek (VersionedNotesStorage),
    - koordynację całego procesu.
    """
    def __init__(self, model_name="gpt-4o"):
        self.model_name = model_name
        self.client = OpenAI()
        
        # Inicjalizacja agentów
        self.note_taking_agent = NoteTakingAgent(model_name)
        self.review_agent = ReviewAgent(model_name)
        self.translation_agent = TranslationAgent()
        
        self.storage = VersionedNotesStorage()
        self.transcript = None

    def coordinate_workflow(self, state: AgentState) -> AgentState:
        """Podejmuje decyzję o następnym kroku na podstawie analizy stanu."""
        print("\n[ManagerAgent] Analizuję stan i podejmuję decyzję...")

        notes_preview = str(state['notes'])[:200] + "..." if state['notes'] else "brak"

        prompt = f"""Jako manager systemu, podejmij decyzję o następnym kroku na podstawie:

Stan: {state['status']}
Typ notatek: {state['note_type']}
Jest feedback: {'tak' if state['feedback'] else 'nie'}
Język docelowy: {state['target_language']}
Obecne notatki: {notes_preview}

Aktualna sytuacja:
1. Czy notatki zostały już wygenerowane? {"tak" if state['notes'] else "nie"}
2. Czy jest feedback do uwzględnienia? {"tak" if state['feedback'] else "nie"}
3. Czy potrzebne tłumaczenie? {"tak" if state['target_language'] != "polski" else "nie"}
4. Czy notatki były już tłumaczone? {"tak" if state['status'] == "notes_translated" else "nie"}

Wybierz JEDNO działanie (odpowiedz TYLKO jednym słowem):
- generuj (gdy brak notatek)
- popraw (gdy jest feedback)
- tłumacz (gdy potrzebne tłumaczenie)
- zakończ (gdy wszystko gotowe)"""

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "Jesteś managerem systemu do generowania notatek. Jeśli nie ma notatek, zawsze najpierw należy je wygenerować."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        decision = response.choices[0].message.content.strip().lower()
        print(f"[ManagerAgent] Decyzja: {decision}")
        
        state["decision"] = decision
        return state

    def generate_notes(self, note_type: str, target_lang: str, additional_instructions: str = "") -> str:
        """
        Generuje notatki używając systemu agentowego.
        """
        if not self.transcript:
            raise ValueError("Brak transkrypcji.")

        state = AgentState(
            messages=[],
            transcript=self.transcript,
            notes="",
            feedback=additional_instructions,
            target_language=target_lang,
            note_type=note_type,
            status="started",
            decision=""
        )

        while True:
            # Manager podejmuje decyzję
            state = self.coordinate_workflow(state)
            decision = state["decision"].split()[0]  # Bierzemy tylko pierwsze słowo
            
            print(f"\n[ManagerAgent] Podjęta decyzja: {decision}")
            
            if decision == "generuj":
                state = self.note_taking_agent(state)
                self.storage.add_version(state["notes"])
                state["status"] = "notes_generated"
            elif decision == "tłumacz":
                state = self.translation_agent(state)
                state["status"] = "notes_translated"
            elif decision == "zakończ":
                if not state["notes"]:  # Zabezpieczenie przed zakończeniem bez notatek
                    print("[ManagerAgent] Próba zakończenia bez notatek. Wymuszam generowanie...")
                    state = self.note_taking_agent(state)
                    self.storage.add_version(state["notes"])
                break
            else:
                print(f"[ManagerAgent] Nieznana decyzja: {decision}")
                if not state["notes"]:  # Zabezpieczenie
                    state = self.note_taking_agent(state)
                    self.storage.add_version(state["notes"])
                break

        return state["notes"]

    def refine_notes(self, feedback: str) -> tuple[str, str]:
        """
        Poprawia notatki na podstawie feedbacku, używając systemu agentowego.
        Zwraca tuple (notatki, opis_zmian).
        """
        if not self.storage.has_versions():
            raise ValueError("Brak notatek do poprawienia.")

        state = AgentState(
            messages=[],
            transcript=self.transcript,
            notes=self.storage.get_latest_version(),
            feedback=feedback,
            target_language="polski",
            note_type="review",
            status="review_started",
            decision=""
        )

        print("\n[ManagerAgent] Rozpoczynam proces poprawiania notatek...")
        
        while True:
            # Manager podejmuje decyzję
            state = self.coordinate_workflow(state)
            decision = state["decision"].split()[0]  # Bierzemy tylko pierwsze słowo
            
            print(f"\n[ManagerAgent] Podjęta decyzja: {decision}")
            
            if decision == "popraw":
                state = self.review_agent(state)
                # Zapisujemy poprawioną wersję
                self.storage.add_version(state["notes"])
                # Po poprawieniu kończymy
                break
            elif decision == "tłumacz":
                state = self.translation_agent(state)
            elif decision == "zakończ":
                break
            else:
                print(f"[ManagerAgent] Nieznana decyzja: {decision}")
                break

        return state["notes"], state.get("changes", "Brak opisu zmian.")

    def set_transcript(self, transcript: str):
        """Ustawia transkrypcję do przetworzenia"""
        self.transcript = transcript

    def get_notes_history(self) -> list:
        """Zwraca historię wersji notatek"""
        return self.storage.get_all_versions()

    def get_translation_metrics(self, target_lang: str) -> dict:
        """Returns translation model metrics for specified language"""
        return self.translation_agent.evaluate_model(target_lang)
