import gradio as gr
import matplotlib.pyplot as plt
from agents.manager_agent import ManagerAgent
from metrics.aspect_metrics import NoteAspectEvaluator
from transcribe import get_youtube_transcript, get_audio_transcript
from utils import get_file_paths
import numpy as np

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

    def on_generate_notes(note_type, target_language, additional_instructions):
        """Generuje notatki i pokazuje elementy do poprawiania"""
        notes = manager.generate_notes(note_type, target_language, additional_instructions)
        return [
            notes,
            gr.update(visible=True),  # feedback_input
            gr.update(visible=True),  # refine_button
            gr.update(visible=True),  # changes_output
        ]

    def on_refine_notes(feedback):
        """Poprawia notatki na podstawie feedbacku"""
        try:
            notes, changes = manager.refine_notes(feedback)
            return [
                notes,  # Notatki do wyświetlenia
                gr.update(value=""),  # Czyścimy pole feedback
                gr.update(value=changes, visible=True),  # Pokazujemy opis zmian
            ]
        except Exception as e:
            raise gr.Error(f"Wystąpił błąd: {str(e)}")

    # Interfejs Gradio
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
                        choices=["summary", "academic", "outline", "mindmap", "q_and_a", "flashcards"],
                        value="summary",
                        label="Wybierz styl notatek"
                    )
                    target_language = gr.Dropdown(
                        choices=["polski", "english", "español", "francais"],
                        value="polski",
                        label="Język notatek"
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
                    changes_output = gr.Markdown(
                        label="Wprowadzone zmiany",
                        value="",
                        visible=False
                    )

                with gr.Column(scale=2):
                    notes_output = gr.Markdown(
                        label="Wygenerowane notatki",
                        value="*Tu pojawią się wygenerowane notatki...*",
                    )

        with gr.Tab("3. Historia"):
            history_output = gr.JSON(label="Historia wersji notatek (JSON)")
            get_history_btn = gr.Button("Pokaż historię")
            end_btn = gr.Button("Zakończ proces")

        with gr.Tab("4. Model Metrics"):
            with gr.Row():
                evaluate_btn = gr.Button("Evaluate All Languages")
            
            with gr.Row():
                metrics_scores = gr.Dataframe(
                    headers=["Language", "Precision", "Recall", "F1 Score"],
                    label="Translation Metrics",
                )
                
                metrics_plot = gr.Plot(label="Metrics Comparison")

        with gr.Tab("5. Note Evaluation"):
            with gr.Row():
                evaluate_notes_btn = gr.Button("Evaluate Current Notes")
                
            with gr.Row():
                evaluation_output = gr.Markdown(
                    label="Evaluation Results",
                    value="*Click 'Evaluate Current Notes' to see the evaluation results...*"
                )

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
            inputs=[note_type, target_language, additional_instructions],
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
            fn=on_refine_notes,
            inputs=[feedback_input],
            outputs=[notes_output, feedback_input, changes_output]
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

        def update_metrics():
            languages = ["english", "español", "francais"]
            all_metrics = []
            metrics_data = []
            
            # Zbierz metryki dla każdego języka
            for lang in languages:
                metrics = manager.get_translation_metrics(lang)
                all_metrics.append({
                    'language': lang,
                    'precision': metrics['precision'],
                    'recall': metrics['recall'],
                    'f1_score': metrics['f1_score']
                })
                metrics_data.append([
                    lang,
                    metrics['precision'],
                    metrics['recall'],
                    metrics['f1_score']
                ])
            
            # Stwórz wykres porównawczy
            fig, ax = plt.subplots(figsize=(10, 6))
            x = np.arange(len(languages))
            width = 0.25
            
            # Utworzenie słupków dla każdej metryki
            ax.bar(x - width, [m['precision'] for m in all_metrics], width, label='Precision', color='#2ecc71')
            ax.bar(x, [m['recall'] for m in all_metrics], width, label='Recall', color='#3498db')
            ax.bar(x + width, [m['f1_score'] for m in all_metrics], width, label='F1 Score', color='#9b59b6')
            
            ax.set_ylabel('Scores')
            ax.set_title('Translation Metrics Comparison')
            ax.set_xticks(x)
            ax.set_xticklabels(languages)
            ax.legend()
            ax.set_ylim(0, 1)
            
            # Dodaj wartości na słupkach
            def autolabel(rects):
                for rect in rects:
                    height = rect.get_height()
                    ax.annotate(f'{height:.2f}',
                              xy=(rect.get_x() + rect.get_width() / 2, height),
                              xytext=(0, 3),
                              textcoords="offset points",
                              ha='center', va='bottom', rotation=0)
            
            for container in ax.containers:
                autolabel(container)
            
            plt.tight_layout()
            
            return [metrics_data, fig]

        evaluate_btn.click(
            fn=update_metrics,
            inputs=[],
            outputs=[metrics_scores, metrics_plot]
        )

        async def evaluate_current_notes():
            if not manager.has_valid_transcript():
                return "Error: No transcript available. Please generate notes first."
            
            current_notes = manager.get_latest_notes()
            if not current_notes:
                return "Error: No notes available. Please generate notes first."
            
            evaluator = NoteAspectEvaluator()
            scores = await evaluator.evaluate_notes(manager.transcript, current_notes)
            return evaluator.get_evaluation_summary(scores)

        evaluate_notes_btn.click(
            fn=evaluate_current_notes,
            inputs=[],
            outputs=[evaluation_output]
        )

    return demo

if __name__ == "__main__":
    demo = build_interface()
    demo.launch()
