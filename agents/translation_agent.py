from transformers import pipeline
from metrics.metrics import TranslationMetrics
from datasets import load_dataset
from data.translation_test_data import TEST_DATA
from agents.state import AgentState  # W każdym pliku agenta
from agents.base_agent import BaseAgent

class TranslationAgent(BaseAgent):
    def __init__(self):
        super().__init__("TranslationAgent", "")  # Nie używamy OpenAI
        self.translators = {
            "en": pipeline("translation", model="Helsinki-NLP/opus-mt-pl-en"),
            "es": pipeline("translation", model="Helsinki-NLP/opus-mt-pl-es"),
            "fr": pipeline("translation", model="Helsinki-NLP/opus-mt-pl-fr")
        }
        self.metrics_calculator = TranslationMetrics()
        self.latest_metrics = {}
        self.test_data = TEST_DATA

    def __call__(self, state: dict) -> dict:
        """Główna logika tłumaczenia"""
        if state["target_language"] == "polski":
            return state

        lang_code = {
            "english": "en",
            "español": "es",
            "francais": "fr"
        }.get(state["target_language"].lower())

        if not lang_code or lang_code not in self.translators:
            raise ValueError(f"Unsupported language: {state['target_language']}")

        lines = state["notes"].split('\n')
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

            translated = self.translators[lang_code](line)[0]['translation_text']
            translated_lines.append(translated)

        print("[TranslationAgent] Zakończono tłumaczenie")
        
        # Aktualizacja stanu
        state["notes"] = '\n'.join(translated_lines)
        state["status"] = "notes_translated"
        
        # Informuj managera o zakończeniu
        if "messages" not in state:
            state["messages"] = []
        state["messages"].append({
            "from_agent": self.name,
            "to_agent": "ManagerAgent",
            "content": {
                "status": "completed",
                "target_language": state["target_language"]
            }
        })
        
        return state

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

    def evaluate_translations(self):
        """
        Ewaluacja jakości tłumaczeń na podstawie danych testowych.
        """
<<<<<<< HEAD
        results = {}
        for lang_code, translator in self.translators.items():
            print(f"\nEwaluacja tłumaczenia dla języka: {lang_code}")
            test_cases = self.test_data.get(lang_code, [])
=======
        lang_code = {
            "english": "en",
            "español": "es",
            "francais": "fr"
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
>>>>>>> f084a25 (metrics)
            
            if not test_cases:
                print(f"Brak danych testowych dla języka {lang_code}")
                continue

            translations = []
            references = []

            for test_case in test_cases:
                source = test_case['source']
                reference = test_case['target']
                
                translation = translator(source)[0]['translation_text']
                translations.append(translation)
                references.append(reference)

            metrics = self.metrics_calculator.calculate_metrics(translations, references)
            results[lang_code] = metrics
            print(f"Metryki dla {lang_code}: {metrics}")

        self.latest_metrics = results
        return results

    def get_latest_metrics(self):
        """
        Zwraca ostatnie obliczone metryki.
        """
        return self.latest_metrics