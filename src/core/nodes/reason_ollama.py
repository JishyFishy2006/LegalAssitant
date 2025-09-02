"""Reasoning node using Ollama for generating legal responses."""
import json
from typing import List, Dict, Any
from ..llm.ollama_client import OllamaClient

class ReasonNode:
    """Reasoning node for generating legal responses with citations."""
    
    def __init__(self):
        """Initialize reasoning node with Ollama client."""
        try:
            # Use default model from OllamaClient
            self.client = OllamaClient()
            self.model = self.client.model  # Get the actual model name being used
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize Ollama. "
                "Please ensure Ollama is running. Error: {str(e)}"
            )
            
        self.system_prompt = self._load_system_prompt()
    
    def _load_system_prompt(self) -> str:
        """Load the system prompt for legal reasoning with enforced synthesis."""
        return """You are a legal research assistant. Your job is to analyze legal documents and provide clear, 
        well-reasoned answers to legal questions by SYNTHESIZING information across multiple sources.
        
        # CORE INSTRUCTIONS
        1. You MUST synthesize information across all documents. DO NOT list documents separately.
        2. Identify and group related legal concepts, rights, and obligations.
        3. Explain how different provisions work together in practice.
        4. Highlight any exceptions, limitations, or special cases.
        
        # RESPONSE FORMAT
        Follow this structure:
        
        1. [DISCLAIMER] "I am not a lawyer. This is not legal advice."
        
        2. [DIRECT ANSWER] 
           - Start with a concise 1-2 sentence answer to the question.
           - Use plain language, not legal jargon.
           
        3. [DETAILED EXPLANATION]
           - Group related points under clear section headers (e.g., "Access to Reports", "Disputing Errors")
           - For each point, explain the legal principle and its practical implications
           - Use bullet points for clarity
           - Include specific timeframes, limits, or conditions
           
        4. [IMPORTANT CONSIDERATIONS]
           - Note any exceptions or special cases
           - Mention any required procedures or documentation
           - Highlight potential consequences
           
        5. [CITATIONS]
           - Include (Source: [Agency/Document]) for key facts
           - Keep citations brief and relevant
           
        6. [DISCLAIMER] "Please consult with a qualified attorney for advice specific to your situation."
        
        # SYNTHESIS TECHNIQUES
        - Look for connections between different documents
        - Combine similar points from multiple sources
        - Explain how different provisions work together
        - Note any contradictions or variations in the law
        - Focus on practical implications for the user

### EXAMPLE 1: FCRA RIGHTS
Q: What are my rights under the Fair Credit Reporting Act?

A: [DISCLAIMER] I am not a lawyer. This is not legal advice.

[DIRECT ANSWER]
The Fair Credit Reporting Act (FCRA) gives you important rights to access, correct, and control your credit information, with specific protections for accuracy and privacy.

[DETAILED EXPLANATION]

**1. Access to Your Credit Information**
- Get one free credit report every 12 months from each of the three major credit bureaus
- Additional free reports in certain situations (e.g., denied credit, unemployment, suspected fraud)
- Receive notice if information in your file is used against you

**2. Accuracy and Dispute Rights**
- Dispute incomplete or inaccurate information (bureaus must investigate within 30 days)
- Have incorrect information corrected or deleted
- Add a statement to your file explaining any disputes

**3. Privacy and Access Controls**
- Limit "prescreened" credit offers (opt-out available)
- Restrict who can access your credit report (requires "permissible purpose")
- Place a security freeze to prevent new accounts being opened in your name

[IMPORTANT CONSIDERATIONS]
- Time limits: Most negative information drops off after 7 years (10 years for bankruptcies)
- Special rules apply to medical debt and certain other types of information
- Some rights require specific written notice or dispute procedures

[CITATIONS]
(Source: Federal Trade Commission, consumer.ftc.gov)
(Source: Consumer Financial Protection Bureau, consumerfinance.gov)

[DISCLAIMER] Please consult with a qualified attorney for advice specific to your situation.

### EXAMPLE 2: TENANT REPAIRS
Q: What can I do if my landlord won't make repairs?

A: [DISCLAIMER] I am not a lawyer. This is not legal advice.

[DIRECT ANSWER]
If your landlord fails to make necessary repairs, you may have several legal remedies depending on your state, including repair-and-deduct, rent withholding, or breaking your lease in severe cases.

[DETAILED EXPLANATION]

**1. Initial Steps**
- Document all issues with photos/videos and written notices
- Send a formal repair request in writing (keep copies)
- Check local housing codes for specific requirements

**2. Available Remedies**
- Repair and deduct: Pay for repairs yourself and deduct from rent (some states)
- Rent withholding: Stop paying rent until repairs are made (with court approval in some states)
- Code enforcement: Report violations to local housing authorities
- Lawsuit: Seek court-ordered repairs or monetary damages

[IMPORTANT CONSIDERATIONS]
- State laws vary significantly on what remedies are available
- Some states require specific procedures before taking action
- Wrongful actions could lead to eviction

[CITATIONS]
(Source: U.S. Department of Housing and Urban Development, hud.gov)
(Source: National Consumer Law Center, nclc.org)

[DISCLAIMER] Please consult with a qualified attorney for advice specific to your situation."""
    
    def _summarize_passages(self, passages: List[Dict[str, Any]], query: str) -> str:
        """Summarize passages to extract key legal concepts and their relationships.
        
        Args:
            passages: List of passage dictionaries with 'text', 'title', and 'source_url' keys
            query: The user's query to determine relevance
            
        Returns:
            str: A synthesized summary focusing on legal concepts and their relationships
        """
        if not passages:
            return "No relevant documents found."
            
        # Identify key legal concepts from the query
        legal_terms = {
            'rights', 'act', 'section', 'law', 'require', 'must', 'prohibit',
            'access', 'dispute', 'report', 'credit', 'information', 'consumer'
        }
        
        # Extract key concepts from the query
        query_concepts = set(term.lower() for term in query.split() 
                           if term.lower() not in {'what', 'are', 'my', 'the', 'under', 'for', 'and', 'with'})
        
        # Track concepts and their relationships
        concept_map = {}
        
        for passage in passages[:5]:  # Limit to top 5 passages
            text = passage.get('text', '').strip()
            if not text:
                continue
                
            title = passage.get('title', 'Document')
            source = passage.get('source_url', '')
            
            # Extract key sentences with legal concepts
            sentences = [s.strip() for s in text.split('.') if any(term in s.lower() for term in legal_terms)]
            
            for sent in sentences:
                # Extract legal provisions (e.g., "Section 605", "15 U.S. Code § 1681")
                import re
                provisions = re.findall(r'(?:Section\s+\d+[A-Z]*|\d+\s+U\.?S\.?C\.?\s+§?\s*\d+)', sent, re.IGNORECASE)
                
                # Extract key rights or requirements
                rights = []
                if 'right' in sent.lower():
                    rights.extend(re.findall(r'right to [\w\s]+(?=\s*(?:\.|,|;|$))', sent.lower()))
                if 'must' in sent.lower() or 'require' in sent.lower():
                    rights.extend(re.findall(r'(?:must|require[sd]?)[\s\w]+(?=\s*(?:\.|,|;|$))', sent.lower()))
                
                # Extract timeframes
                timeframes = re.findall(r'\b(?:within|after|for|up to|maximum of)?\s*\d+\s*(?:days?|months?|years?)\b', sent.lower())
                
                # Add to concept map
                for concept in provisions + rights + timeframes:
                    if concept not in concept_map:
                        concept_map[concept] = []
                    concept_map[concept].append({
                        'sentence': sent,
                        'source': source,
                        'title': title
                    })
        
        # Generate a synthesized summary
        summary_parts = []
        
        # Group by document/source
        source_map = {}
        for concept, entries in concept_map.items():
            for entry in entries:
                if entry['title'] not in source_map:
                    source_map[entry['title']] = {
                        'source': entry['source'],
                        'concepts': set(),
                        'sentences': []
                    }
                source_map[entry['title']]['concepts'].add(concept)
                if entry['sentence'] not in source_map[entry['title']]['sentences']:
                    source_map[entry['title']]['sentences'].append(entry['sentence'])
        
        # Build the summary
        for title, data in source_map.items():
            source_note = f" (Source: {data['source']})" if data['source'] else ""
            summary_parts.append(f"{title}{source_note}:")
            summary_parts.extend(f"- {s}" for s in data['sentences'][:3])  # Limit to top 3 sentences per source
            summary_parts.append("")  # Add blank line between sources
        
        return '\n'.join(summary_parts).strip() if summary_parts else "No relevant legal concepts found in the provided documents."
    
    def process(self, query: str, passages: List[Dict[str, Any]], synthesis_instructions: str = None) -> Dict[str, Any]:
        """Generate a legal response by synthesizing information across multiple documents.
        
        Args:
            query: The user's legal question
            passages: List of relevant passages from the retriever
            synthesis_instructions: Optional instructions for how to synthesize the information
            
        Returns:
            Dict with 'answer' (str) and 'citations' (list of dicts)
        """
        if not passages:
            return {
                'answer': "I couldn't find any relevant legal information to answer your question.",
                'citations': []
            }
        
        # Summarize the most relevant parts of the passages
        context = self._summarize_passages(passages, query)
        
        # Prepare the user message with explicit instructions
        special_instructions = f"[SPECIAL INSTRUCTIONS]\n{synthesis_instructions}" if synthesis_instructions else ""
        
        # Format the context with document sections
        formatted_context = ""
        for i, passage in enumerate(passages[:5], 1):  # Limit to top 5 most relevant passages
            title = passage.get('title', f'Document {i}')
            text = passage.get('text', '').strip()
            source = passage.get('source_url', '')
            
            formatted_context += f"""
            --- DOCUMENT {i}: {title} ---
            {text}
            
            Source: {source if source else 'Not specified'}
            
            """
        
        user_message = f"""[QUESTION]
        {query}
        
        [RELEVANT DOCUMENT SECTIONS]
        {formatted_context}
        
        [TASK]
        Based on the provided document sections, please provide a comprehensive answer to the question following these guidelines:
        
        1. Start with a concise, direct answer to the question
        2. Include relevant details and context from the documents
        3. Cite specific sections or passages when making claims
        4. If the documents don't fully answer the question, clearly state what information is missing
        5. Format your response with clear section headers
        
        {special_instructions}
        
        [RESPONSE FORMAT]
        [DISCLAIMER] I am not a lawyer. This is not legal advice.
        
        [DIRECT ANSWER]
        [Your concise answer here]
        
        [DETAILED EXPLANATION]
        [Your detailed analysis here with citations]
        
        [IMPORTANT CONSIDERATIONS]
        [Any exceptions, limitations, or special cases]
        
        [CITATIONS]
        [List of sources with specific sections referenced]
        
        [DISCLAIMER] Please consult with a qualified attorney for advice specific to your situation.
        """.strip()
        
        # Prepare the messages for the LLM
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message.strip()}
        ]
        
        try:
            # Get the response from the LLM
            response = self.client.chat(
                messages,
                temperature=0.2,  # Lower temperature for more focused, consistent responses
                max_tokens=2000,  # Allow for more detailed analysis
                top_p=0.9,
                frequency_penalty=0.25,  # Reduce repetition
                presence_penalty=0.15,   # Encourage covering all key points
            )
            
            # Extract the answer text
            answer_text = response['message']['content']
            
            # Ensure the response includes the required disclaimers
            if not answer_text.startswith("I am not a lawyer. This is not legal advice."):
                answer_text = "I am not a lawyer. This is not legal advice.\n\n" + answer_text
                
            if "Please consult with a qualified attorney" not in answer_text:
                answer_text += "\n\nPlease consult with a qualified attorney for advice specific to your situation."
            
            # Extract citations from the passages
            citations = [
                {
                    'title': p.get('title', 'Untitled Document'),
                    'source_url': p.get('source_url', ''),
                    'id': p.get('id', '')
                }
                for p in passages
                if p.get('text', '').strip()
            ]
            
            return {
                'answer': answer_text,
                'citations': citations[:10]  # Limit to top 10 citations
            }
            
        except Exception as e:
            # Try to extract citations from passages
            citations = []
            try:
                citations = [
                    {
                        'title': p.get('title', 'Untitled Document'),
                        'source_url': p.get('source_url', ''),
                        'id': p.get('id', '')
                    }
                    for p in passages[:10]  # Limit to top 10 citations
                    if p.get('text', '').strip()
                ]
            except:
                pass
                
            return {
                'answer': (
                    "I'm sorry, I encountered an error while processing your request. "
                    f"Error: {str(e)}\n\n"
                    "Please try rephrasing your question or ask about a different legal topic."
                ),
                'citations': citations,
                'error': str(e)
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
