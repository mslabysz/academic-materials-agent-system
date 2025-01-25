import gradio as gr
import os
from agents.manager_agent import ManagerAgent
from transcribe import get_youtube_transcript, get_audio_transcript
from utils import get_file_paths


def build_interface():
    manager = ManagerAgent()

    def download_txt_file(content, filename):
        if not content:
            raise gr.Error("Brak treści do zapisania.")
        full_path, filename = get_file_paths(content, filename)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return full_path

    # Funkcja pomocnicza do generowania transkrypcji
    def transcribe_source(youtube_url, audio_file):
        """
        Zwraca (transkrypcja, ścieżka pliku) w zależności od wyboru użytkownika.
        """
        transcript, path = "", ""
        if youtube_url:
            transcript, path = get_youtube_transcript(youtube_url)
        elif audio_file is not None:
            transcript, path = get_audio_transcript(audio_file.name)
        else:
            raise ValueError("Nie podano źródła audio/wideo.")

        manager.set_transcript(transcript)
        # Zwracamy komponenty do aktualizacji
        return [
            transcript,
            path,
            gr.update(interactive=True, label="2. Generowanie notatek")
        ]

    def on_generate_notes(note_type, additional_instructions):
        """Generuje notatki i pokazuje elementy do poprawiania"""
        notes = manager.generate_notes(note_type, additional_instructions)
        return [
            notes,
            gr.update(visible=True),  # feedback_input
            gr.update(visible=True),  # refine_button
            gr.update(visible=True),  # changes_output
        ]

    # Funkcja do refinacji/poprawek
    def refine_notes(feedback):
        """
        Funkcja do poprawiania notatek na podstawie feedbacku.
        """
        try:
            notes, changes = manager.refine_notes(feedback)
            return notes, changes
        except Exception as e:
            return f"Wystąpił błąd: {str(e)}", "Nie udało się wygenerować opisu zmian."

    def update_tab_state(interactive):
        """Aktualizuje stan drugiego taba"""
        label = "2. Generowanie notatek" if interactive else "2. Generowanie notatek (najpierw pobierz transkrypcję)"
        return gr.Tab.update(interactive=interactive, label=label)

    def on_transcript_received():
        """Callback wywoływany po pomyślnym pobraniu transkrypcji"""
        update_tab_state(True)

    # Interfejs

    with gr.Blocks() as demo:
        gr.Markdown("## Aplikacja do notatek z nagrań audio/YouTube")

        with gr.Tab("1. Wybór źródła"):
            youtube_url = gr.Textbox(label="Link do YouTube (opcjonalnie)")
            audio_file = gr.File(label="Plik audio (opcjonalnie)")

            transcript_output = gr.Textbox(label="Transkrypcja (podgląd)", interactive=False)
            transcript_path_output = gr.Textbox(label="Zapisana ścieżka pliku transkrypcji", interactive=False)

            transcribe_btn = gr.Button("Pobierz transkrypcję")
            transcript_download_btn = gr.Button("Pobierz transkrypcję do pliku txt", interactive=False)
            transcript_file = gr.File(label="Plik do pobrania", visible=False)

        tab_2 = gr.Tab("2. Generowanie notatek (najpierw pobierz transkrypcję)", interactive=False)
        with tab_2:
            with gr.Row():
                with gr.Column(scale=1):
                    note_type = gr.Radio(
                        choices=["summary", "academic", "outline", "mindmap", "q_and_a"],
                        value="summary",
                        label="Wybierz styl notatek"
                    )
                    additional_instructions = gr.Textbox(
                        label="Dodatkowe instrukcje",
                        placeholder="Np. 'Zwróć uwagę na...'",
                        lines=2
                    )
                    generate_notes_btn = gr.Button("Generuj notatki", size="lg")
                    notes_download_btn = gr.Button("Pobierz notatki do pliku txt", interactive=False)
                    notes_file = gr.File(label = "Plik do pobrania", visible = False)

                    # Elementy początkowo ukryte
                    feedback_input = gr.Textbox(
                        label="Feedback do notatek",
                        placeholder="Wpisz sugestie zmian...",
                        lines=2,
                        visible=False
                    )
                    refine_button = gr.Button("Popraw notatki", visible=False)
                    changes_output = gr.Textbox(
                        label="Wprowadzone zmiany",
                        lines=2,
                        interactive=False,
                        visible=False
                    )

                with gr.Column(scale=2):
                    notes_output = gr.Textbox(
                        label="Wygenerowane notatki",
                        lines=25,
                        show_label=False
                    )

        with gr.Tab("3. Historia"):
            history_output = gr.JSON(label="Historia wersji notatek (JSON)")
            get_history_btn = gr.Button("Pokaż historię")
            end_btn = gr.Button("Zakończ proces")

        # --- Akcje ---

        transcribe_btn.click(
            fn=transcribe_source,
            inputs=[youtube_url, audio_file],
            outputs=[transcript_output, transcript_path_output, tab_2]
        ).then(
            lambda: gr.update(interactive=True),
            None,
            [transcript_download_btn]
        )

        generate_notes_btn.click(
            fn=on_generate_notes,
            inputs=[note_type, additional_instructions],
            outputs=[
                notes_output,
                feedback_input,
                refine_button,
                changes_output
            ]
        ).then(
            lambda: gr.update(interactive=True),
            None,
            [notes_download_btn]
        )

        transcript_download_btn.click(
            fn=lambda x: download_txt_file(x, "transcript"),
            inputs=[transcript_output],
            outputs=[transcript_file]
        ).then(
            lambda: (gr.update(interactive=True), gr.update(visible=True)),
            None,
            [transcript_download_btn,transcript_file]
        )

        notes_download_btn.click(
            fn=lambda x: download_txt_file(x, "notes"),
            inputs=[notes_output],
            outputs=[notes_file]
        ).then(
            lambda: (gr.update(interactive=True), gr.update(visible=True)),
            None,
            [notes_download_btn,notes_file]
        )

        refine_button.click(
            fn=refine_notes,
            inputs=[feedback_input],
            outputs=[notes_output, changes_output]
        )

        def get_history():
            return manager.get_notes_history()

        get_history_btn.click(
            fn=get_history,
            inputs=[],
            outputs=[history_output]
        )

        def end_process():
            return "Proces zakończony. Możesz zamknąć aplikację."

        end_btn.click(
            fn=end_process,
            inputs=[],
            outputs=[]
        )

    return demo

if __name__ == "__main__":
    demo = build_interface()
    demo.launch()
