from transformers import pipeline
from metrics.metrics import TranslationMetrics
from datasets import load_dataset
from data.translation_test_data import TEST_DATA

class TranslationAgent:
    def __init__(self):
        self.translators = {
            "en": pipeline("translation", model="Helsinki-NLP/opus-mt-pl-en"),
            "es": pipeline("translation", model="Helsinki-NLP/opus-mt-pl-es")
        }
        self.metrics_calculator = TranslationMetrics()
        self.latest_metrics = {}
        self.test_data = TEST_DATA

    def translate(self, text: str, target_lang: str) -> str:
        """
        Tłumaczy tekst na wybrany język
        """
        if target_lang not in self.translators:
            raise ValueError(f"Nieobsługiwany język: {target_lang}")

        lines = text.split('\n')
        translated_lines = []
        total_lines = len([l for l in lines if l.strip()])
        current_line = 0

        print(f"\n[TranslationAgent] Rozpoczynam tłumaczenie {total_lines} linii...")

        for line in lines:
            if line.strip() == '':
                translated_lines.append(line)
                continue

            current_line += 1
            print(f"[TranslationAgent] Tłumaczenie linii {current_line}/{total_lines}")

            translated = self.translators[target_lang](line)[0]['translation_text']
            translated_lines.append(translated)

        print("[TranslationAgent] Zakończono tłumaczenie")
        return '\n'.join(translated_lines)

    def evaluate_model(self, target_lang: str):
        """
        Evaluate model performance using test dataset
        """
        lang_code = {
            "english": "en",
            "español": "es"
        }.get(target_lang)

        if not lang_code or lang_code not in self.translators:
            raise ValueError(f"Unsupported language: {target_lang}")

        print(f"\n[TranslationAgent] Rozpoczynam ewaluację modelu dla języka: {target_lang}")
        print(f"[TranslationAgent] Liczba par testowych: {len(self.test_data[lang_code])}")
        
        predictions = []
        references = []
        
        for i, (source, reference) in enumerate(self.test_data[lang_code], 1):
            prediction = self.translators[lang_code](source)[0]['translation_text']
            predictions.append(prediction)
            references.append(reference)
            
            # Wyświetl każde tłumaczenie
            print(f"[TranslationAgent] Test {i}/{len(self.test_data[lang_code])}: '{source}' -> '{prediction}' (expected: '{reference}')")
            
            # Co 10 testów pokaż podsumowanie postępu
            if i % 10 == 0:
                print(f"\n[TranslationAgent] Postęp: {i}/{len(self.test_data[lang_code])} ({(i/len(self.test_data[lang_code])*100):.1f}%)")
                print("=" * 80 + "\n")
        
        print("\n[TranslationAgent] Obliczam metryki...")
        all_metrics = self.metrics_calculator.calculate_metrics(predictions, references)
        
        # tylko znormalizowane metryki
        self.latest_metrics = {
            'precision': all_metrics['precision'],
            'recall': all_metrics['recall'],
            'f1_score': all_metrics['f1_score']
        }
        
        print("\n[TranslationAgent] Podsumowanie ewaluacji:")
        print(f"- Precision: {self.latest_metrics['precision']:.2f}")
        print(f"- Recall: {self.latest_metrics['recall']:.2f}")
        print(f"- F1 Score: {self.latest_metrics['f1_score']:.2f}")
        print("\n[TranslationAgent] Zakończono ewaluację")
        
        return self.latest_metrics

    def get_latest_metrics(self):
        return self.latest_metrics