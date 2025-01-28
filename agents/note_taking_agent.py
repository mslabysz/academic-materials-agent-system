from agents.base_agent import BaseAgent
from prompts.prompts import NOTE_TAKING_PROMPTS

class NoteTakingAgent(BaseAgent):
    def __init__(self, model_name="gpt-4o"):
        super().__init__("NoteTakingAgent", model_name)

    def __call__(self, state: dict) -> dict:
        """Główna logika generowania notatek"""
        print(f"\n[NoteTakingAgent] Rozpoczynam generowanie notatek typu: {state.get('note_type')}")
        
        prompt = NOTE_TAKING_PROMPTS[state["note_type"]].format(
            transcript=state["transcript"]
        )
        
        if state.get("feedback"):  # Dodatkowe instrukcje
            prompt += f"\n\nDodatkowe instrukcje: {state['feedback']}"

        print("[NoteTakingAgent] Wysyłam zapytanie do modelu...")
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant specialized in note-taking."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        notes = response.choices[0].message.content.strip()
        print(f"[NoteTakingAgent] Wygenerowano notatki o długości {len(notes)} znaków")
        
        # Aktualizacja stanu
        state["notes"] = notes
        state["status"] = "notes_generated"
        
        # Informuj managera o zakończeniu
        if "messages" not in state:
            state["messages"] = []
        state["messages"].append({
            "from_agent": self.name,
            "to_agent": "ManagerAgent",
            "content": {
                "status": "completed",
                "notes_length": len(notes)
            }
        })
        
        return state
