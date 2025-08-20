"""I/O utilities for file operations."""
import json
import os
from typing import Any, Dict, List, Optional

def read_jsonl(file_path: str) -> List[Dict[str, Any]]:
    """Read a JSONL file and return a list of dictionaries."""
    records = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            records.append(json.loads(line.strip()))
    return records

def write_jsonl(records: List[Dict[str, Any]], file_path: str) -> None:
    """Write a list of dictionaries to a JSONL file."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')

def read_text_file(file_path: str) -> str:
    """Read a text file and return its contents."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def write_text_file(content: str, file_path: str) -> None:
    """Write content to a text file."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
