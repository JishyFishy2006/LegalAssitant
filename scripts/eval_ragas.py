#!/usr/bin/env python3
"""
RAGAS evaluation script for T5.1 - evaluates RAG system quality.
Usage: python scripts/eval_ragas.py
"""
import sys
import os
import json
from typing import List, Dict, Any

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from core.nodes.retriever_faiss import Retriever
from core.nodes.reason_ollama import ReasonNode
from core.nodes.reranker_bge import RerankerNode

def create_test_dataset() -> List[Dict[str, Any]]:
    """Create an expanded test dataset for RAGAS evaluation."""
    return [
        # Credit Reporting
        {
            "question": "How long do late payments stay on my credit report?",
            "expected_answer": "Late payments typically stay on credit reports for 7 years from the original delinquency date.",
            "topic": "credit_reporting"
        },
        {
            "question": "What are my rights under the Fair Credit Reporting Act?",
            "expected_answer": "The FCRA gives you rights to access your credit report, dispute errors, and be notified of adverse actions.",
            "topic": "credit_reporting"
        },
        {
            "question": "How do I dispute an error on my credit report?",
            "expected_answer": "You can dispute errors by contacting the credit bureau in writing with supporting documentation.",
            "topic": "credit_reporting"
        },
        {
            "question": "What information appears on credit reports?",
            "expected_answer": "Credit reports contain payment history, account information, credit inquiries, and public records.",
            "topic": "credit_reporting"
        },
        
        # Debt Collection
        {
            "question": "Can debt collectors call me at work?",
            "expected_answer": "Debt collectors cannot call you at work if you tell them your employer prohibits such calls.",
            "topic": "debt_collection"
        },
        {
            "question": "What are illegal debt collection practices?",
            "expected_answer": "Illegal practices include harassment, false statements, unfair practices, and calling at inappropriate times.",
            "topic": "debt_collection"
        },
        {
            "question": "What information must debt collectors provide?",
            "expected_answer": "Debt collectors must provide validation notices with debt amount, creditor name, and dispute rights.",
            "topic": "debt_collection"
        },
        {
            "question": "Can I stop debt collectors from contacting me?",
            "expected_answer": "You can request in writing that debt collectors stop contacting you, with some exceptions.",
            "topic": "debt_collection"
        },
        
        # Consumer Rights
        {
            "question": "What is identity theft protection?",
            "expected_answer": "Identity theft protection includes fraud alerts, credit freezes, and monitoring services.",
            "topic": "consumer_rights"
        },
        {
            "question": "How do I place a fraud alert?",
            "expected_answer": "Contact one credit bureau to place a fraud alert, which will be shared with the other bureaus.",
            "topic": "consumer_rights"
        },
        {
            "question": "What is a credit freeze?",
            "expected_answer": "A credit freeze restricts access to your credit file to prevent new accounts from being opened.",
            "topic": "consumer_rights"
        },
        {
            "question": "What are my rights when applying for credit?",
            "expected_answer": "You have rights to fair treatment, disclosure of terms, and notification of adverse actions.",
            "topic": "consumer_rights"
        },
        
        # Employment and Credit
        {
            "question": "Can employers check my credit report?",
            "expected_answer": "Employers can check credit reports with written permission for certain positions.",
            "topic": "employment"
        },
        {
            "question": "What must employers tell me about credit checks?",
            "expected_answer": "Employers must get written consent and provide disclosure before running credit checks.",
            "topic": "employment"
        }
    ]

def evaluate_rag_system():
    """Evaluate the RAG system using improved RAGAS metrics."""
    try:
        print("Starting Enhanced RAGAS evaluation...")
        
        # Initialize components with reranker integration
        retriever = Retriever()
        reranker = RerankerNode()
        reasoner = ReasonNode()
        
        # Create expanded test dataset
        test_data = create_test_dataset()
        
        results = []
        total_faithfulness = 0
        total_relevance = 0
        total_context_recall = 0
        topic_scores = {}
        
        for i, test_case in enumerate(test_data):
            question = test_case["question"]
            topic = test_case.get("topic", "general")
            print(f"\nEvaluating question {i+1}/{len(test_data)}: {question}")
            print(f"  Topic: {topic}")
            
            # Step 1: Retrieve relevant documents
            retrieved_docs = retriever.search(question, k=8)  # Get more candidates
            
            # Step 2: Rerank for better relevance
            reranked_docs = reranker.process(question, retrieved_docs, top_k=5)
            
            # Step 3: Generate answer with reranked context
            response = reasoner.process(question, reranked_docs)
            answer = response.get("answer", "")
            
            # Extract contexts for evaluation
            contexts = [doc.get("text", "") for doc in reranked_docs]
            
            # Calculate multiple metrics
            faithfulness_score = calculate_faithfulness(answer, contexts)
            relevance_score = calculate_relevance(question, contexts)
            context_recall_score = calculate_context_recall(test_case["expected_answer"], contexts)
            
            # Track by topic
            if topic not in topic_scores:
                topic_scores[topic] = {"faithfulness": [], "relevance": [], "context_recall": []}
            topic_scores[topic]["faithfulness"].append(faithfulness_score)
            topic_scores[topic]["relevance"].append(relevance_score)
            topic_scores[topic]["context_recall"].append(context_recall_score)
            
            total_faithfulness += faithfulness_score
            total_relevance += relevance_score
            total_context_recall += context_recall_score
            
            result = {
                "question": question,
                "topic": topic,
                "answer": answer,
                "contexts": contexts,
                "faithfulness": faithfulness_score,
                "relevance": relevance_score,
                "context_recall": context_recall_score,
                "retrieved_docs": len(retrieved_docs),
                "reranked_docs": len(reranked_docs),
                "citations": len(response.get("citations", []))
            }
            results.append(result)
            
            print(f"  Faithfulness: {faithfulness_score:.3f}")
            print(f"  Relevance: {relevance_score:.3f}")
            print(f"  Context Recall: {context_recall_score:.3f}")
            print(f"  Citations: {result['citations']}")
        
        # Calculate average scores
        num_tests = len(test_data)
        avg_faithfulness = total_faithfulness / num_tests
        avg_relevance = total_relevance / num_tests
        avg_context_recall = total_context_recall / num_tests
        
        # Print detailed results
        print(f"\n{'='*60}")
        print(f"Enhanced RAGAS Evaluation Results")
        print(f"{'='*60}")
        print(f"Overall Scores:")
        print(f"  Average Faithfulness: {avg_faithfulness:.3f}")
        print(f"  Average Relevance: {avg_relevance:.3f}")
        print(f"  Average Context Recall: {avg_context_recall:.3f}")
        print(f"  Total Questions: {num_tests}")
        
        # Topic breakdown
        print(f"\nTopic Breakdown:")
        for topic, scores in topic_scores.items():
            avg_faith = sum(scores["faithfulness"]) / len(scores["faithfulness"])
            avg_rel = sum(scores["relevance"]) / len(scores["relevance"])
            avg_recall = sum(scores["context_recall"]) / len(scores["context_recall"])
            print(f"  {topic.replace('_', ' ').title()}:")
            print(f"    Faithfulness: {avg_faith:.3f}")
            print(f"    Relevance: {avg_rel:.3f}")
            print(f"    Context Recall: {avg_recall:.3f}")
        
        print(f"\nPass Thresholds:")
        print(f"  Faithfulness: 0.750")
        print(f"  Relevance: 0.700")
        print(f"  Context Recall: 0.600")
        
        # Determine pass/fail
        passes_faithfulness = avg_faithfulness >= 0.75
        passes_relevance = avg_relevance >= 0.70
        passes_context_recall = avg_context_recall >= 0.60
        
        overall_pass = passes_faithfulness and passes_relevance and passes_context_recall
        
        if overall_pass:
            print(f"\n✅ OVERALL PASS: All metrics meet thresholds")
        else:
            print(f"\n❌ OVERALL FAIL: Some metrics below threshold")
            if not passes_faithfulness:
                print(f"  ❌ Faithfulness: {avg_faithfulness:.3f} < 0.750")
            if not passes_relevance:
                print(f"  ❌ Relevance: {avg_relevance:.3f} < 0.700")
            if not passes_context_recall:
                print(f"  ❌ Context Recall: {avg_context_recall:.3f} < 0.600")
        
        return overall_pass
            
    except Exception as e:
        print(f"❌ ERROR during evaluation: {e}")
        return False
    finally:
        if 'retriever' in locals():
            retriever.close()

def calculate_faithfulness(answer: str, contexts: List[str]) -> float:
    """
    Calculate faithfulness score - how well the answer is grounded in retrieved contexts.
    """
    if not answer or not contexts:
        return 0.0
    
    answer_lower = answer.lower()
    context_text = " ".join(contexts).lower()
    
    # Check for required legal disclaimers
    has_disclaimer = any(phrase in answer_lower for phrase in [
        "not legal advice", "not a lawyer", "consult with a qualified attorney"
    ])
    
    # Check for explicit citations
    has_citations = any(phrase in answer_lower for phrase in [
        "according to", "source:", "document", "based on"
    ])
    
    # Check content overlap with contexts
    answer_words = set(answer_lower.split())
    context_words = set(context_text.split())
    
    if not answer_words:
        return 0.0
    
    overlap = len(answer_words.intersection(context_words))
    content_faithfulness = min(overlap / len(answer_words), 1.0)
    
    # Penalize if answer seems to add external knowledge
    external_knowledge_penalty = 0.0
    if "typically" in answer_lower or "generally" in answer_lower:
        if content_faithfulness < 0.5:  # Low overlap suggests external knowledge
            external_knowledge_penalty = 0.2
    
    # Calculate final score
    faithfulness = content_faithfulness
    if has_disclaimer:
        faithfulness = min(faithfulness + 0.15, 1.0)
    if has_citations:
        faithfulness = min(faithfulness + 0.1, 1.0)
    
    faithfulness = max(0.0, faithfulness - external_knowledge_penalty)
    
    return faithfulness

def calculate_relevance(question: str, contexts: List[str]) -> float:
    """
    Calculate relevance score - how relevant the retrieved contexts are to the question.
    """
    if not question or not contexts:
        return 0.0
    
    question_lower = question.lower()
    question_words = set(question_lower.split())
    
    # Remove common stop words
    stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "be", "been", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "may", "might", "can", "what", "how", "when", "where", "why", "who"}
    question_words = question_words - stop_words
    
    if not question_words:
        return 0.0
    
    relevance_scores = []
    
    for context in contexts:
        context_lower = context.lower()
        context_words = set(context_lower.split()) - stop_words
        
        if not context_words:
            relevance_scores.append(0.0)
            continue
        
        # Calculate word overlap
        overlap = len(question_words.intersection(context_words))
        word_relevance = overlap / len(question_words)
        
        # Boost for topic-specific terms
        topic_boosts = {
            "credit report": 0.1,
            "debt collector": 0.1,
            "fair credit reporting act": 0.15,
            "fcra": 0.15,
            "fdcpa": 0.15,
            "consumer rights": 0.1,
            "identity theft": 0.1,
            "fraud alert": 0.1,
            "credit freeze": 0.1
        }
        
        topic_boost = 0.0
        for term, boost in topic_boosts.items():
            if term in question_lower and term in context_lower:
                topic_boost += boost
        
        relevance_scores.append(min(word_relevance + topic_boost, 1.0))
    
    # Return average relevance across all contexts
    return sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0

def calculate_context_recall(expected_answer: str, contexts: List[str]) -> float:
    """
    Calculate context recall - how much of the expected information is present in contexts.
    """
    if not expected_answer or not contexts:
        return 0.0
    
    expected_lower = expected_answer.lower()
    context_text = " ".join(contexts).lower()
    
    # Extract key concepts from expected answer
    expected_words = set(expected_lower.split())
    
    # Remove stop words
    stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "be", "been", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "may", "might", "can"}
    expected_words = expected_words - stop_words
    
    if not expected_words:
        return 0.0
    
    context_words = set(context_text.split())
    
    # Calculate how many expected concepts are covered
    covered_concepts = len(expected_words.intersection(context_words))
    recall = covered_concepts / len(expected_words)
    
    # Boost for specific legal terms being present
    legal_terms = ["years", "days", "written", "notice", "dispute", "error", "report", "bureau", "collector", "rights", "law", "act", "federal", "state"]
    legal_term_boost = 0.0
    
    for term in legal_terms:
        if term in expected_lower and term in context_text:
            legal_term_boost += 0.05
    
    return min(recall + legal_term_boost, 1.0)

if __name__ == "__main__":
    success = evaluate_rag_system()
    sys.exit(0 if success else 1)
