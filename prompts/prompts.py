NOTE_TAKING_PROMPTS = {
    "summary": """Jesteś asystentem AI, Twoim zadaniem jest stworzenie krótkiego streszczenia (podsumowania) z podanej transkrypcji.
Użyj formatowania Markdown:
- Użyj '# Podsumowanie' jako głównego nagłówka
- Użyj '##' dla podsekcji
- Użyj **pogrubienia** dla kluczowych pojęć
- Użyj *kursywy* dla definicji
- Użyj > dla ważnych cytatów
- Użyj list (-) dla punktów

Transkrypcja:
{transcript}

Wygeneruj treść notatek w stylu "summary" z odpowiednim formatowaniem Markdown.
""",

    "academic": """Jesteś asystentem AI, Twórz notatki akademickie z poniższej transkrypcji.
Użyj formatowania Markdown:
- '# Tytuł' dla głównego tematu
- '##' dla głównych sekcji
- '###' dla podsekcji
- **pogrubienie** dla kluczowych terminów
- *kursywa* dla definicji
- Listy numerowane (1.) dla kroków/procesów
- Listy punktowane (-) dla przykładów
- > dla cytatów i ważnych definicji
- Tabele dla porównań i zestawień

Transkrypcja:
{transcript}
""",

    "outline": """Stwórz szczegółowy konspekt (outline) z poniższej transkrypcji.
Użyj formatowania Markdown:
- '# Konspekt' jako tytuł
- Użyj różnych poziomów nagłówków (##, ###) dla hierarchii
- Listy numerowane i punktowane dla podpunktów
- **Pogrubienie** dla głównych tematów
- *Kursywa* dla dodatkowych informacji

Transkrypcja:
{transcript}
""",

    "mindmap": """Stwórz mind map (w formacie tekstowym, z wcięciami) z poniższej transkrypcji.
Użyj formatowania Markdown:
- '# Mind Map' jako tytuł
- Użyj '##' dla głównych gałęzi
- Użyj wcięć i list (-) dla podgałęzi
- **Pogrubienie** dla kluczowych pojęć
- *Kursywa* dla dodatkowych informacji
- > dla ważnych cytatów lub definicji

Transkrypcja:
{transcript}
""",

    "q_and_a": """Na podstawie poniższej transkrypcji stwórz zestaw pytań i odpowiedzi (Q&A).
Użyj formatowania Markdown:
- '# Pytania i Odpowiedzi' jako tytuł
- '##' dla kategorii pytań (jeśli są)
- **Pytanie:** dla każdego pytania
- *Odpowiedź:* dla każdej odpowiedzi
- Użyj > dla ważnych cytatów z transkrypcji
- Użyj list (-) dla punktowanych odpowiedzi

Transkrypcja:
{transcript}
""",
}

REVIEW_PROMPT = """Oto aktualne notatki, wraz z oryginalną transkrypcją i feedbackiem użytkownika.
Wprowadź żądane poprawki lub rozwiń notatki zgodnie z uwagami.
Zachowaj istniejące formatowanie Markdown i dodaj nowe tam, gdzie to potrzebne.

---
Transkrypcja (oryginalna):
{transcript}

Obecna wersja notatek:
{current_notes}

Feedback użytkownika:
{feedback}

Zwróć nową, poprawioną wersję notatek, zachowując formatowanie Markdown.
"""
