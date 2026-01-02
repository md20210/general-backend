"""
RAGAS-based RAG Evaluation Service

This service uses RAGAS (Retrieval-Augmented Generation Assessment) to evaluate
the quality of RAG system responses using professional metrics:
- Faithfulness: No hallucinations (answer based on retrieved context)
- Answer Relevancy: How well the answer addresses the question
- Context Precision: Quality of retrieved chunks
- Context Recall: Coverage of relevant information

Uses Grok API for evaluation (cost-effective and high-quality).
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama

logger = logging.getLogger(__name__)


class RAGASEvaluator:
    """RAGAS-based evaluator for RAG systems using Grok API"""

    def __init__(self, provider: str = "grok"):
        """
        Initialize RAGAS evaluator with specified LLM provider.

        Args:
            provider: "ollama" (local, DSGVO-compliant) or "grok" (cloud API)
        """
        self.provider = provider

        if provider == "ollama":
            # Use local Ollama (DSGVO-compliant)
            from langchain_community.llms import Ollama
            self.evaluator_llm = Ollama(
                model="llama3.2:3b",
                base_url=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
                temperature=0.0,
            )
            logger.info("✅ RAGAS Evaluator initialized with LOCAL Ollama (DSGVO-compliant)")
        else:
            # Use Grok API (cloud, faster/better but not DSGVO-compliant)
            self.grok_api_key = os.getenv("GROK_API_KEY")
            if not self.grok_api_key:
                logger.warning("GROK_API_KEY not found, falling back to Ollama")
                from langchain_community.llms import Ollama
                self.evaluator_llm = Ollama(
                    model="llama3.2:3b",
                    base_url=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
                    temperature=0.0,
                )
                self.provider = "ollama"
            else:
                # Grok uses OpenAI-compatible API
                self.evaluator_llm = ChatOpenAI(
                    model="grok-beta",
                    openai_api_key=self.grok_api_key,
                    openai_api_base="https://api.x.ai/v1",
                    temperature=0.0,
                )
                logger.info("✅ RAGAS Evaluator initialized with Grok API")

        # Define metrics to use
        self.metrics = [
            faithfulness,        # No hallucinations
            answer_relevancy,    # Answers the question
            context_precision,   # Retrieved chunks are relevant
            context_recall,      # All relevant info retrieved
        ]

    def evaluate_single(
        self,
        question: str,
        answer: str,
        contexts: List[str],
        ground_truth: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a single RAG response using RAGAS metrics.

        Args:
            question: User's question
            answer: Generated answer
            contexts: List of retrieved context chunks (text)
            ground_truth: Optional reference answer (improves context_recall)

        Returns:
            Dictionary with metric scores and overall assessment
        """
        try:
            # Create dataset in RAGAS format
            data = {
                'question': [question],
                'answer': [answer],
                'contexts': [contexts],  # List of chunk texts
            }

            # Add ground truth if available (improves context_recall metric)
            if ground_truth:
                data['ground_truth'] = [ground_truth]

            dataset = Dataset.from_dict(data)

            # Run RAGAS evaluation
            logger.info(f"Running RAGAS evaluation for question: '{question[:50]}...'")

            # Select metrics based on available data
            metrics_to_use = [faithfulness, answer_relevancy, context_precision]
            if ground_truth:
                metrics_to_use.append(context_recall)

            result = evaluate(
                dataset=dataset,
                metrics=metrics_to_use,
                llm=self.evaluator_llm,
            )

            # Extract scores
            scores = {
                'faithfulness': float(result['faithfulness']) if 'faithfulness' in result else None,
                'answer_relevancy': float(result['answer_relevancy']) if 'answer_relevancy' in result else None,
                'context_precision': float(result['context_precision']) if 'context_precision' in result else None,
                'context_recall': float(result['context_recall']) if 'context_recall' in result and ground_truth else None,
            }

            # Calculate overall score (weighted average)
            valid_scores = [v for v in scores.values() if v is not None]
            overall_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0

            logger.info(f"RAGAS scores: {scores}, Overall: {overall_score:.2f}")

            return {
                'scores': scores,
                'overall_score': overall_score,
                'evaluation_method': 'ragas_grok',
                'metrics_used': [m for m, v in scores.items() if v is not None]
            }

        except Exception as e:
            logger.error(f"RAGAS evaluation failed: {e}")
            return {
                'scores': {},
                'overall_score': 0.0,
                'error': str(e),
                'evaluation_method': 'ragas_grok_failed'
            }

    def compare_systems(
        self,
        question: str,
        answer_a: str,
        answer_b: str,
        contexts_a: List[str],
        contexts_b: List[str],
        ground_truth: Optional[str] = None,
        system_a_name: str = "System A",
        system_b_name: str = "System B"
    ) -> Dict[str, Any]:
        """
        Compare two RAG systems using RAGAS metrics.

        Args:
            question: User's question
            answer_a: Answer from system A (e.g., pgvector)
            answer_b: Answer from system B (e.g., Elasticsearch)
            contexts_a: Retrieved chunks from system A
            contexts_b: Retrieved chunks from system B
            ground_truth: Optional reference answer
            system_a_name: Name of system A
            system_b_name: Name of system B

        Returns:
            Comparison results with winner and detailed scores
        """
        # Evaluate both systems
        eval_a = self.evaluate_single(question, answer_a, contexts_a, ground_truth)
        eval_b = self.evaluate_single(question, answer_b, contexts_b, ground_truth)

        # Determine winner
        score_a = eval_a['overall_score']
        score_b = eval_b['overall_score']

        if abs(score_a - score_b) < 0.05:  # Within 5% = tie
            winner = "tie"
            confidence = "high" if abs(score_a - score_b) < 0.02 else "medium"
        elif score_a > score_b:
            winner = system_a_name
            confidence = "high" if (score_a - score_b) > 0.15 else "medium"
        else:
            winner = system_b_name
            confidence = "high" if (score_b - score_a) > 0.15 else "medium"

        # Build comparison result
        comparison = {
            'question': question,
            'winner': winner,
            'confidence': confidence,
            system_a_name: {
                'overall_score': score_a,
                'scores': eval_a['scores'],
                'answer': answer_a
            },
            system_b_name: {
                'overall_score': score_b,
                'scores': eval_b['scores'],
                'answer': answer_b
            },
            'score_difference': abs(score_a - score_b),
            'evaluation_method': 'ragas_grok_comparison'
        }

        # Add detailed reasoning
        reasoning_parts = []

        # Compare each metric
        for metric in ['faithfulness', 'answer_relevancy', 'context_precision', 'context_recall']:
            score_a_metric = eval_a['scores'].get(metric)
            score_b_metric = eval_b['scores'].get(metric)

            if score_a_metric is not None and score_b_metric is not None:
                if abs(score_a_metric - score_b_metric) > 0.1:
                    better = system_a_name if score_a_metric > score_b_metric else system_b_name
                    reasoning_parts.append(
                        f"{metric.replace('_', ' ').title()}: {better} performed better "
                        f"({score_a_metric:.2f} vs {score_b_metric:.2f})"
                    )

        comparison['reasoning'] = " | ".join(reasoning_parts) if reasoning_parts else "Scores are very close"

        logger.info(f"RAGAS Comparison: {winner} wins (confidence: {confidence})")
        logger.info(f"Scores: {system_a_name}={score_a:.2f}, {system_b_name}={score_b:.2f}")

        return comparison


# Global instances (one per provider)
_ragas_evaluators = {}


def get_ragas_evaluator(provider: str = "grok") -> RAGASEvaluator:
    """
    Get or create RAGAS evaluator instance for specified provider.

    Args:
        provider: "ollama" (local, DSGVO-compliant) or "grok" (cloud API)

    Returns:
        RAGASEvaluator instance
    """
    global _ragas_evaluators

    # Map frontend provider names to evaluator names
    provider_mapping = {
        "local": "ollama",
        "ollama": "ollama",
        "grok": "grok",
        "anthropic": "grok"  # Use Grok for Anthropic (cheaper for evaluation)
    }
    evaluator_provider = provider_mapping.get(provider.lower(), "grok")

    if evaluator_provider not in _ragas_evaluators:
        _ragas_evaluators[evaluator_provider] = RAGASEvaluator(provider=evaluator_provider)

    return _ragas_evaluators[evaluator_provider]
