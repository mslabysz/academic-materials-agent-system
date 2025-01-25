from transformers import pipeline

class TranslationAgent:
    def __init__(self):
        self.translators = {
            "en": pipeline("translation", model="Helsinki-NLP/opus-mt-pl-en"),
            "es": pipeline("translation", model="Helsinki-NLP/opus-mt-pl-es")
        }

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