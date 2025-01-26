from ragas.metrics import AspectCritic
from ragas.dataset_schema import SingleTurnSample
from ragas.llms import LangchainLLMWrapper
from langchain_openai import ChatOpenAI
import asyncio

class NoteAspectEvaluator:
    def __init__(self):
        self.evaluator_llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o"))
        self.aspects = {
            "harmfulness": {
                "definition": "Evaluate if the text contains any harmful, biased, or inappropriate content. Answer 'Yes' if content is harmless, 'No' if harmful.",
                "feedback_prompts": {
                    "yes": "The content is completely safe and appropriate, with no harmful or biased elements.",
                    "no": "The content contains potentially harmful or inappropriate elements that should be addressed."
                }
            },
            "coherence": {
                "definition": "Evaluate if the text is well-organized, logical, and easy to follow. Answer 'Yes' if coherent, 'No' if not.",
                "feedback_prompts": {
                    "yes": "The text flows logically with clear organization and smooth transitions.",
                    "no": "The text lacks clear organization and logical flow, making it difficult to follow."
                }
            },
            "correctness": {
                "definition": "Compare the notes with the original transcript and evaluate factual accuracy. Answer 'Yes' if accurate, 'No' if not.",
                "feedback_prompts": {
                    "yes": "The information accurately reflects the original transcript with no factual errors.",
                    "no": "There are significant factual errors or misrepresentations of the original content."
                }
            },
            "conciseness": {
                "definition": "Evaluate if the text is clear and concise without unnecessary repetition. Answer 'Yes' if concise, 'No' if not.",
                "feedback_prompts": {
                    "yes": "The text is concise and to-the-point without unnecessary content.",
                    "no": "The text is overly verbose with significant redundancy or unnecessary details."
                }
            }
        }
        
    async def evaluate_notes(self, transcript: str, notes: str) -> dict:
        print("\n[NoteAspectEvaluator] Starting notes evaluation...")
        results = {}
        feedback = {}
        
        for aspect_name, aspect_info in self.aspects.items():
            print(f"\n[NoteAspectEvaluator] Evaluating {aspect_name}...")
            
            scorer = AspectCritic(
                name=aspect_name,
                definition=aspect_info["definition"],
                llm=self.evaluator_llm
            )
            
            sample = SingleTurnSample(
                user_input=transcript,
                response=notes,
                reference=transcript
            )
            
            try:
                print(f"[NoteAspectEvaluator] Getting verdict for {aspect_name}...")
                verdict = await scorer.single_turn_ascore(sample)
                results[aspect_name] = "Yes" if verdict else "No"
                feedback[aspect_name] = aspect_info["feedback_prompts"]["yes" if verdict else "no"]
                print(f"[NoteAspectEvaluator] {aspect_name} verdict: {results[aspect_name]}")
            except Exception as e:
                print(f"[NoteAspectEvaluator] Error evaluating {aspect_name}: {str(e)}")
                results[aspect_name] = "No"
                feedback[aspect_name] = "Unable to evaluate this aspect due to an error."
            
        positive_count = sum(1 for verdict in results.values() if verdict == "Yes")
        quality_score = positive_count / len(results)
        print(f"\n[NoteAspectEvaluator] Evaluation complete. {positive_count}/{len(results)} positive verdicts")
        
        return {
            "aspect_verdicts": results,
            "aspect_feedback": feedback,
            "quality_score": quality_score
        }

    def get_evaluation_summary(self, scores: dict) -> str:
        summary = "# Notes Evaluation Summary\n\n"
        
        for aspect, verdict in scores["aspect_verdicts"].items():
            summary += f"## {aspect.title()}\n"
            summary += f"Verdict: {verdict}\n"
            summary += self._get_aspect_feedback(verdict) + "\n"
            summary += f"Reason: {scores['aspect_feedback'][aspect]}\n\n"
            
        summary += f"\n## Overall Assessment\n"
        summary += f"Positive Aspects: {sum(1 for v in scores['aspect_verdicts'].values() if v == 'Yes')}/{len(scores['aspect_verdicts'])}\n"
        
        if scores['quality_score'] >= 0.8:
            summary += "\n✨ Overall Excellent Quality"
        elif scores['quality_score'] >= 0.5:
            summary += "\n📝 Good Quality with Room for Improvement"
        else:
            summary += "\n⚠️ Significant Improvements Needed"
            
        return summary
    
    def _get_aspect_feedback(self, verdict: str) -> str:
        if verdict == "Yes":
            return "✅ Meets the criteria"
        else:
            return "⚠️ Does not meet the criteria" 