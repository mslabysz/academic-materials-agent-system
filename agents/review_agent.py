from agents.base_agent import BaseAgent
from prompts.prompts import REVIEW_PROMPT

class ReviewAgent(BaseAgent):
    """
    Agent do poprawek i rozbudowy notatek na podstawie feedbacku użytkownika.
    """
    def __init__(self, model_name="gpt-4"):
        super().__init__("ReviewAgent", model_name)

    def __call__(self, state: dict) -> dict:
        """Główna logika poprawiania notatek"""
        if not state.get("feedback"):
            return state

        print(f"[ReviewAgent] Otrzymany feedback: {state['feedback']}")
        
        final_prompt = REVIEW_PROMPT.format(
            transcript=state["transcript"],
            current_notes=state["notes"],
            feedback=state["feedback"]
        ) + "\n\nPo wprowadzeniu zmian, opisz krótko (w 2-3 zdaniach) jakie zmiany zostały wprowadzone. Odpowiedź sformatuj tak:\n[NOTES]\n<tutaj notatki>\n[CHANGES]\n<tutaj opis zmian>"

        print("[ReviewAgent] Wysyłam zapytanie do modelu...")
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant specialized in reviewing and improving notes."},
                {"role": "user", "content": final_prompt}
            ],
            temperature=0.7
        )
        
        full_response = response.choices[0].message.content.strip()
        
        try:
            notes_part = full_response.split("[NOTES]")[1].split("[CHANGES]")[0].strip()
            changes_description = full_response.split("[CHANGES]")[1].strip()
            
            # Aktualizacja stanu
            state["notes"] = notes_part
            if "memory" not in state:
                state["memory"] = {}
            if "ReviewAgent" not in state["memory"]:
                state["memory"]["ReviewAgent"] = {}
            state["memory"]["ReviewAgent"]["changes"] = changes_description
            state["status"] = "notes_reviewed"
            
            # Informuj managera o zmianach
            if "messages" not in state:
                state["messages"] = []
            state["messages"].append({
                "from_agent": self.name,
                "to_agent": "ManagerAgent",
                "content": {
                    "status": "completed",
                    "changes_made": changes_description
                }
            })
            
        except IndexError:
            print("[ReviewAgent] Nie udało się wyodrębnić opisu zmian")
            state["notes"] = full_response
            state["memory"] = {"ReviewAgent": {"changes": "Nie udało się wyodrębnić opisu zmian."}}
            state["status"] = "notes_reviewed"
        
        return state
