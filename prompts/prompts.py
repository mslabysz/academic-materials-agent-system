
NOTE_TAKING_PROMPTS = {
    "summary": """Jesteś asystentem AI, Twoim zadaniem jest stworzenie krótkiego streszczenia (podsumowania) z podanej transkrypcji.
Transkrypcja:
{transcript}
Wygeneruj treść notatek w stylu "summary".
""",

    "academic": """Jesteś asystentem AI, Twórz notatki akademickie z poniższej transkrypcji.
Zadbaj o formalny styl i wyraźną strukturę (punkty, podpunkty, definicje).
Transkrypcja:
{transcript}
""",

    "outline": """Stwórz szczegółowy konspekt (outline) z poniższej transkrypcji:
{transcript}
""",

    "mindmap": """Stwórz mind map (w formacie tekstowym, z wcięciami) z poniższej transkrypcji:
{transcript}
""",

    "q_and_a": """Na podstawie poniższej transkrypcji stwórz zestaw pytań i odpowiedzi (Q&A):
Transkrypcja:
{transcript}
""",
}

REVIEW_PROMPT = """Oto aktualne notatki, wraz z oryginalną transkrypcją i feedbackiem użytkownika.
Wprowadź żądane poprawki lub rozwinij notatki zgodnie z uwagami.

---
Transkrypcja (oryginalna):
{transcript}

Obecna wersja notatek:
{current_notes}

Feedback użytkownika:
{feedback}

Zwróć nową, poprawioną wersję notatek.
"""
