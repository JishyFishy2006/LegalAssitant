#!/usr/bin/env python3
"""Test script for all node components."""
import sys
import os
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_reranker():
    """Test the reranker node."""
    print("Testing RerankerNode...")
    from src.core.nodes.reranker_bge import RerankerNode
    
    reranker = RerankerNode()
    
    # Mock candidates from retrieval
    candidates = [
        {
            'id': 'doc1',
            'text': 'Credit reports contain information about late payments and defaults',
            'rrf_score': 0.8,
            'title': 'Credit Report Info'
        },
        {
            'id': 'doc2', 
            'text': 'Consumer rights under federal law include dispute procedures',
            'rrf_score': 0.6,
            'title': 'Consumer Rights'
        }
    ]
    
    results = reranker.process("late payments credit report", candidates, top_k=2)
    print(f"✅ Reranker processed {len(results)} candidates")
    for r in results:
        print(f"  - {r['id']}: rerank_score={r.get('rerank_score', 0):.3f}")
    return True

def test_structure_validator():
    """Test the structure validator node."""
    print("\nTesting StructureNode...")
    from src.core.nodes.structure_validator import StructureNode
    
    validator = StructureNode()
    
    # Test valid JSON
    valid_json = '{"answer": "This is a test answer", "citations": []}'
    result = validator.process(valid_json)
    print(f"✅ Valid JSON: {result['valid']}")
    
    # Test invalid JSON
    invalid_json = '{"answer": "Missing quote}'
    result = validator.process(invalid_json)
    print(f"✅ Invalid JSON handled: {not result['valid']}")
    
    return True

def test_reason_node():
    """Test the reasoning node."""
    print("\nTesting ReasonNode...")
    try:
        from src.core.nodes.reason_ollama import ReasonNode
        
        reasoner = ReasonNode()
        
        # Mock passages
        passages = [
            {
                'id': 'test1',
                'title': 'Test Document',
                'text': 'Late payments stay on credit reports for 7 years.',
                'source_url': 'https://example.com'
            }
        ]
        
        result = reasoner.process("How long do late payments stay?", passages)
        print(f"✅ Reasoning generated response with {len(result.get('citations', []))} citations")
        print(f"  Answer preview: {result.get('answer', '')[:100]}...")
        return True
    except Exception as e:
        print(f"⚠️  Reasoning node test failed (expected - needs Ollama): {e}")
        return False

def test_stt_node():
    """Test the STT node."""
    print("\nTesting STTNode...")
    from src.core.nodes.stt_faster_whisper import STTNode
    
    stt = STTNode()
    
    # Create minimal WAV bytes for testing
    wav_header = b'RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
    
    result = stt.process(wav_header)
    print(f"✅ STT processed audio: {result.get('transcript', 'No transcript')[:50]}...")
    return True

def test_tts_node():
    """Test the TTS node."""
    print("\nTesting TTSNode...")
    from src.core.nodes.tts_piper import TTSNode
    
    tts = TTSNode()
    
    result = tts.process("This is a test of text to speech conversion.")
    print(f"✅ TTS generated {len(result.get('audio_bytes', b''))} bytes of audio")
    print(f"  Duration: {result.get('duration', 0):.2f} seconds")
    return True

def main():
    """Run all node tests."""
    print("=" * 50)
    print("Testing All Node Components")
    print("=" * 50)
    
    tests = [
        test_reranker,
        test_structure_validator, 
        test_stt_node,
        test_tts_node,
        test_reason_node  # Last since it might fail without Ollama
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    print(f"\n{'=' * 50}")
    print(f"Test Results: {passed}/{total} passed")
    print(f"{'=' * 50}")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
