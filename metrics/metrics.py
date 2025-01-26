from sklearn.metrics import precision_score, recall_score, f1_score
from sacrebleu.metrics import BLEU
from datasets import load_dataset
import numpy as np

class TranslationMetrics:
    def __init__(self):
        self.bleu = BLEU()
        self.metrics = {
            'bleu_score': 0.0,
            'precision': 0.0,
            'recall': 0.0,
            'f1_score': 0.0
        }
        
    def calculate_metrics(self, predictions, references):
        # Calculate BLEU score
        bleu_score = self.bleu.corpus_score(predictions, [references])
        self.metrics['bleu_score'] = round(bleu_score.score, 2)
        
        # Convert text to token-level binary classifications for other metrics
        # This is a simplified approach - in real scenarios you might want more sophisticated tokenization
        pred_tokens = [p.split() for p in predictions]
        ref_tokens = [r.split() for r in references]
        
        # Create binary arrays for token-level matching
        y_true = []
        y_pred = []
        
        for pred, ref in zip(pred_tokens, ref_tokens):
            ref_set = set(ref)
            y_true.extend([1 if token in ref_set else 0 for token in pred])
            y_pred.extend([1] * len(pred))
        
        # Calculate metrics
        self.metrics['precision'] = round(precision_score(y_true, y_pred, zero_division=0), 2)
        self.metrics['recall'] = round(recall_score(y_true, y_pred, zero_division=0), 2)
        self.metrics['f1_score'] = round(f1_score(y_true, y_pred, zero_division=0), 2)
        
        return self.metrics

    def get_metrics(self):
        return self.metrics