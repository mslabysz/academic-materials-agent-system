from openai import OpenAI
from prompts.prompts import NOTE_TAKING_PROMPTS
from agents.state import AgentState  # W każdym pliku agenta
class NoteTakingAgent:
    """
    Agent do generowania notatek na podstawie transkrypcji.
    """
    def __init__(self, model_name="gpt-4o"):
        self.model_name = model_name
        self.client = OpenAI()

    def __call__(self, state: AgentState) -> AgentState:
        """
        Metoda wywoływana przez LangGraph do przetworzenia stanu.
        """
        print(f"\n[NoteTakingAgent] Rozpoczynam generowanie notatek typu: {state['note_type']}")
        
        prompt = NOTE_TAKING_PROMPTS[state["note_type"]].format(
            transcript=state["transcript"]
        )
        
        if state.get("additional_instructions"):
            prompt += f"\n\nDodatkowe instrukcje: {state['additional_instructions']}"

        print("[NoteTakingAgent] Wysyłam zapytanie do modelu...")
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        notes = response.choices[0].message.content.strip()
        print(f"[NoteTakingAgent] Wygenerowano notatki o długości {len(notes)} znaków")
        
        # Aktualizacja stanu
        state["notes"] = notes
        state["status"] = "notes_generated"
        
        return state
