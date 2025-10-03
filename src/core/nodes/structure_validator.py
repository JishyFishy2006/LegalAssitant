"""Structure validation node for ensuring JSON response format."""
import json
from typing import Dict, Any, Optional
import jsonschema

class StructureNode:
    """Structure validation node for validating and formatting JSON responses."""
    
    def __init__(self, schema_path: Optional[str] = None):
        """Initialize structure validator with optional JSON schema."""
        self.schema = self._load_schema(schema_path) if schema_path else None
    
    def _load_schema(self, schema_path: str) -> Dict[str, Any]:
        """Load JSON schema from file."""
        try:
            with open(schema_path, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def process(self, json_string: str, expected_schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Validate and structure JSON response.
        
        Args:
            json_string: Raw JSON string to validate
            expected_schema: Optional schema to validate against
            
        Returns:
            Dict containing validated JSON object and validation status
        """
        try:
            # Parse JSON string
            parsed_json = json.loads(json_string)
            
            # Use provided schema or instance schema
            schema = expected_schema or self.schema
            
            # Validate against schema if available
            validation_errors = []
            if schema:
                try:
                    jsonschema.validate(parsed_json, schema)
                except jsonschema.ValidationError as e:
                    validation_errors.append(str(e))
            
            # Ensure required legal disclaimers
            if isinstance(parsed_json, dict) and 'answer' in parsed_json:
                answer = parsed_json['answer']
                if not self._has_legal_disclaimer(answer):
                    parsed_json['answer'] = self._add_legal_disclaimer(answer)
            
            return {
                "valid": len(validation_errors) == 0,
                "data": parsed_json,
                "errors": validation_errors,
                "formatted": True
            }
            
        except json.JSONDecodeError as e:
            # Try to extract JSON from text if parsing fails
            cleaned_json = self._extract_json_from_text(json_string)
            if cleaned_json:
                return self.process(cleaned_json, expected_schema)
            
            return {
                "valid": False,
                "data": {"error": "Invalid JSON format", "raw_text": json_string},
                "errors": [f"JSON decode error: {str(e)}"],
                "formatted": False
            }
        except Exception as e:
            return {
                "valid": False,
                "data": {"error": str(e)},
                "errors": [str(e)],
                "formatted": False
            }
    
    def _has_legal_disclaimer(self, text: str) -> bool:
        """Check if text contains required legal disclaimer."""
        disclaimer_phrases = [
            "I am not a lawyer",
            "This is not legal advice",
            "not legal advice",
            "consult with a qualified attorney"
        ]
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in disclaimer_phrases)
    
    def _add_legal_disclaimer(self, text: str) -> str:
        """Add legal disclaimer to response if missing."""
        disclaimer = "I am not a lawyer. This is not legal advice. "
        return disclaimer + text
    
    def _extract_json_from_text(self, text: str) -> Optional[str]:
        """Attempt to extract JSON from mixed text content."""
        # Look for JSON-like structures in the text
        start_markers = ['{', '[']
        end_markers = ['}', ']']
        
        for start_char, end_char in zip(start_markers, end_markers):
            start_idx = text.find(start_char)
            if start_idx != -1:
                # Find matching closing bracket
                bracket_count = 0
                for i, char in enumerate(text[start_idx:], start_idx):
                    if char == start_char:
                        bracket_count += 1
                    elif char == end_char:
                        bracket_count -= 1
                        if bracket_count == 0:
                            return text[start_idx:i+1]
        
        return None
