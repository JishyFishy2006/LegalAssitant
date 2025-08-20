"""Reasoning node using Ollama for generating legal responses."""
import json
from typing import List, Dict, Any
from ..llm.ollama_client import OllamaClient

class ReasonNode:
    """Reasoning node for generating legal responses with citations."""
    
    def __init__(self, model: str = "llama3.2"):
        """Initialize reasoning node with Ollama client."""
        self.client = OllamaClient(model)
        self.system_prompt = self._load_system_prompt()
    
    def _load_system_prompt(self) -> str:
        """Load the system prompt for legal reasoning with emphasis on analysis."""
        return """You are a legal research assistant. Your goal is to analyze legal documents and provide clear, reasoned answers to legal questions.

1. Always begin with: "I am not a lawyer. This is not legal advice."
2. Analyze the question and relevant documents to provide a direct, concise answer in your own words.
3. Focus on explaining the legal principles and reasoning behind the answer rather than quoting text.
4. When referencing documents:
   - Explain the relevance of each document to the question
   - Synthesize information across documents when possible
   - Use citations in this format: (Source: [Document Title], [URL])
5. If the documents don't directly answer the question:
   - Explain what information is available
   - Note any gaps in the available information
6. End with: "Please consult with a qualified attorney for advice specific to your situation."

### Example:
Q: What is a credit report?
A: I am not a lawyer. This is not legal advice.
A credit report is a record of your borrowing history, including accounts, loans, and payment behavior. It is used by lenders and sometimes employers to evaluate your financial reliability (Source: CFPB, consumerfinance.gov; Source: FTC, ftc.gov).
Please consult with a qualified attorney for advice specific to your situation."""
    
    def process(self, query: str, passages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a legal response based on query and retrieved passages."""
        try:
            context = self._format_passages(passages)
            
            user_message = f"""User Question:
{query}

Background Context (do not copy directly):
{context}

Task:
You are given a user question and some background context from legal documents.
- Use the background context only as supporting evidence.
- Do not regurgitate raw text.
- Always reason from the context to construct a direct answer.
- If the context does not contain an answer, state this clearly.
- Always structure your answer as:
  1. Disclaimer
  2. Direct Answer (reasoned in your own words)
  3. Supporting Evidence (cite context documents)
  4. Closing Disclaimer"""
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            response = self.client.chat(messages)
            answer_text = response.get('message', {}).get('content', '')
            
            citations = self._extract_citations(passages)
            
            return {
                "answer": answer_text,
                "citations": citations,
                "query": query,
                "sources_used": len(passages)
            }
            
        except Exception as e:
            citations = self._extract_citations(passages)
            fallback_answer = self._generate_fallback_response(query, passages)
            
            return {
                "answer": fallback_answer,
                "citations": citations,
                "query": query,
                "sources_used": len(passages),
                "fallback_mode": True,
                "error": f"Ollama unavailable: {str(e)}"
            }
    
    def _format_passages(self, passages: List[Dict[str, Any]]) -> str:
        """Format passages for inclusion in the prompt."""
        formatted = []
        for i, passage in enumerate(passages, 1):
            title = passage.get('title', 'Unknown Document')
            text = passage.get('text', '')
            source_url = passage.get('source_url', '')
            
            formatted.append(f"""Document {i}: {title}
Source: {source_url}
Content: {text}
---""")
        
        return "\n\n".join(formatted)
    
    def _extract_citations(self, passages: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Extract citation information from passages."""
        citations = []
        for passage in passages:
            citations.append({
                "id": passage.get('id', ''),
                "title": passage.get('title', 'Unknown Document'),
                "source_url": passage.get('source_url', ''),
                "score": str(passage.get('rerank_score', passage.get('rrf_score', 0)))
            })
        return citations
    
    def _generate_fallback_response(self, query: str, passages: List[Dict[str, Any]]) -> str:
        """Generate a fallback response focused on analysis when Ollama is unavailable."""
        parts = ["I am not a lawyer. This is not legal advice.\n"]
        
        if not passages:
            parts.append("I couldn't find any relevant legal documents to address your question.\n")
        else:
            # Group passages by topic
            topics = {}
            for passage in passages:
                topic = passage.get('title', 'General Legal Information')
                if topic not in topics:
                    topics[topic] = []
                topics[topic].append(passage)
            
            # Provide an analytical response
            parts.append(f"Regarding your question about '{query}', here's my analysis based on the available documents:\n")
            
            for topic, topic_passages in list(topics.items())[:3]:
                parts.append(f"**{topic}**")
                # Take the most relevant passage from each topic
                best_passage = max(topic_passages, 
                                 key=lambda p: len(set(query.lower().split()) & 
                                                set(p.get('text', '').lower().split())))
                
                # Generate an analytical summary
                summary = self._summarize_passage(best_passage.get('text', ''), query)
                source = f" (Source: {best_passage.get('source_url', '')})" if best_passage.get('source_url') else ""
                
                # Add analysis of how this relates to the query
                parts.append(f"- {summary}{source}")
        
        parts.append("\nFor specific legal advice tailored to your situation, please consult with a qualified attorney.")
        return "\n".join(parts)
    
    def _summarize_passage(self, text: str, query: str, max_length: int = 200) -> str:
        """Generate an analytical summary of a passage in relation to the query."""
        # Simple extraction of key sentences
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 10]
        query_terms = set(term.lower() for term in query.split() if len(term) > 2)
        
        if not sentences:
            return "This document contains information that may be relevant to your question."
            
        # Score sentences based on relevance to query and position
        scored_sentences = []
        for i, sent in enumerate(sentences):
            sent_terms = set(term.lower() for term in sent.split() if len(term) > 2)
            # Higher score for sentences that contain query terms
            term_score = len(query_terms.intersection(sent_terms))
            # Slight preference for sentences earlier in the document
            position_score = 1.0 / (i + 1)
            score = (term_score * 2) + position_score
            if score > 0:
                scored_sentences.append((score, sent))
        
        # Sort by score and take top 1-2 sentences
        scored_sentences.sort(reverse=True, key=lambda x: x[0])
        summary = '. '.join(s for _, s in scored_sentences[:2])
        
        # Ensure the summary is concise and ends properly
        if len(summary) > max_length:
            summary = summary[:max_length].rsplit(' ', 1)[0] + '...'
        if not summary.endswith(('.', '...')):
            summary += '...'
            
        return summary
