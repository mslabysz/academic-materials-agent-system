from openai import OpenAI
from prompts.prompts import REVIEW_PROMPT
from agents.state import AgentState

class ReviewAgent:
    """
    Agent do poprawek i rozbudowy notatek na podstawie feedbacku użytkownika.
    """
    def __init__(self, model_name="gpt-4o"):
        self.model_name = model_name
        self.client = OpenAI()

    def __call__(self, state: AgentState) -> AgentState:
        """
        Metoda wywoływana przez LangGraph do przetworzenia stanu.
        """
        if not state["feedback"]:
            return state

        print(f"\n[ReviewAgent] Rozpoczynam poprawianie notatek")
        print(f"[ReviewAgent] Otrzymany feedback: {state['feedback']}")
        
        final_prompt = REVIEW_PROMPT.format(
            transcript=state["transcript"],
            current_notes=state["notes"],
            feedback=state["feedback"]
        ) + "\n\nPo wprowadzeniu zmian, opisz krótko (w 2-3 zdaniach) jakie zmiany zostały wprowadzone. Odpowiedź sformatuj tak:\n[NOTES]\n<tutaj notatki>\n[CHANGES]\n<tutaj opis zmian>"

        print("[ReviewAgent] Wysyłam zapytanie do modelu...")
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": final_prompt}
            ],
            temperature=0.7
        )
        
        print("[ReviewAgent] Otrzymano odpowiedź od modelu")
        full_response = response.choices[0].message.content.strip()
        
        try:
            notes_part = full_response.split("[NOTES]")[1].split("[CHANGES]")[0].strip()
            changes_description = full_response.split("[CHANGES]")[1].strip()
        except IndexError:
            notes_part = full_response
            changes_description = "Nie udało się wyodrębnić opisu zmian."
        
        print(f"[ReviewAgent] Wygenerowano poprawione notatki o długości {len(notes_part)} znaków")
        print(f"[ReviewAgent] Wygenerowano opis zmian o długości {len(changes_description)} znaków")
        
        # Aktualizacja stanu
        state["notes"] = notes_part
        state["changes"] = changes_description
        state["status"] = "notes_reviewed"
        
        return state
