from openai import OpenAI
from prompts.prompts import NOTE_TAKING_PROMPTS

class NoteTakingAgent:
    """
    Agent do tworzenia wstępnych notatek.
    """
    def __init__(self, model_name="gpt-4o"):
        self.model_name = model_name
        self.client = OpenAI()
    
    def run(self, transcript: str, note_type: str, additional_instructions: str = "") -> str:
        """
        Generuje notatki na podstawie transkrypcji oraz zadanego typu notatek (summary, academic, outline, mindmap, q_and_a).
        """
        print(f"\n[NoteTakingAgent] Rozpoczynam generowanie notatek typu: {note_type}")
        if additional_instructions:
            print(f"[NoteTakingAgent] Dodatkowe instrukcje: {additional_instructions}")
        
        prompt_template = NOTE_TAKING_PROMPTS.get(note_type, NOTE_TAKING_PROMPTS["summary"])
        final_prompt = prompt_template.format(transcript=transcript)
        if additional_instructions:
            final_prompt += f"\nDodatkowe instrukcje: {additional_instructions}\n"

        print("[NoteTakingAgent] Wysyłam zapytanie do modelu...")
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": final_prompt}
            ],
            temperature=0.7
        )
        print("[NoteTakingAgent] Otrzymano odpowiedź od modelu")
        notes = response.choices[0].message.content.strip()
        print(f"[NoteTakingAgent] Wygenerowano notatki o długości {len(notes)} znaków")
        return notes
