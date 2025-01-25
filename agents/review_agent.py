from openai import OpenAI
from prompts.prompts import REVIEW_PROMPT

class ReviewAgent:
    """
    Agent do poprawek i rozbudowy notatek na podstawie feedbacku użytkownika.
    """
    def __init__(self, model_name="gpt-4o"):
        self.model_name = model_name
        self.client = OpenAI()

    def refine_notes(self, transcript: str, current_notes: str, feedback: str) -> tuple[str, str]:
        """
        Na podstawie transkrypcji, obecnych notatek i feedbacku, zwraca krotkę (nowe_notatki, opis_zmian).
        """
        print(f"\n[ReviewAgent] Rozpoczynam poprawianie notatek")
        print(f"[ReviewAgent] Otrzymany feedback: {feedback}")
        
        final_prompt = REVIEW_PROMPT.format(
            transcript=transcript,
            current_notes=current_notes,
            feedback=feedback
        ) + "\n\nPo wprowadzeniu zmian, opisz krótko (w 2-3 zdaniach) jakie zmiany zostały wprowadzone. Odpowiedź sformatuj tak:\n[NOTES]\n<tutaj notatki>\n[CHANGES]\n<tutaj opis zmian>"

        print("[ReviewAgent] Wysyłam zapytanie do modelu...")
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": final_prompt}
            ],
            temperature=0.7
        )
        
        print("[ReviewAgent] Otrzymano odpowiedź od modelu")
        full_response = response.choices[0].message.content.strip()
        
        # Rozdzielamy odpowiedź na notatki i opis zmian
        try:
            notes_part = full_response.split("[NOTES]")[1].split("[CHANGES]")[0].strip()
            changes_description = full_response.split("[CHANGES]")[1].strip()
        except IndexError:
            # Jeśli format odpowiedzi jest nieprawidłowy, zwracamy całość jako notatki
            notes_part = full_response
            changes_description = "Nie udało się wyodrębnić opisu zmian."
        
        print(f"[ReviewAgent] Wygenerowano poprawione notatki o długości {len(notes_part)} znaków")
        print(f"[ReviewAgent] Wygenerowano opis zmian o długości {len(changes_description)} znaków")
        return notes_part, changes_description
