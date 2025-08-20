import React, { useState, useRef } from 'react'
import axios from 'axios'
import './App.css'

interface QueryResponse {
  query: string
  answer: string
  citations: Array<{
    id: string
    title: string
    source_url: string
    score: string
  }>
  sources_used: number
  processing_time: number
  fallback_mode?: boolean
  error?: string
}

function App() {
  const [query, setQuery] = useState('')
  const [response, setResponse] = useState<QueryResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])

  const handleTextQuery = async () => {
    if (!query.trim()) return

    setLoading(true)
    try {
      const result = await axios.post('/api/query', {
        query: query.trim(),
        k: 5
      })
      setResponse(result.data)
    } catch (error) {
      console.error('Query failed:', error)
      setResponse({
        query: query.trim(),
        answer: 'Sorry, there was an error processing your request.',
        citations: [],
        sources_used: 0,
        processing_time: 0,
        error: 'Network or server error'
      })
    } finally {
      setLoading(false)
    }
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data)
      }

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' })
        setAudioBlob(audioBlob)
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorder.start()
      setIsRecording(true)
    } catch (error) {
      console.error('Failed to start recording:', error)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  const handleAudioQuery = async () => {
    if (!audioBlob) return

    setLoading(true)
    try {
      const formData = new FormData()
      formData.append('audio', audioBlob, 'query.wav')

      const result = await axios.post('/api/query/audio', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      setResponse(result.data)
    } catch (error) {
      console.error('Audio query failed:', error)
      setResponse({
        query: 'Audio query',
        answer: 'Sorry, there was an error processing your audio request.',
        citations: [],
        sources_used: 0,
        processing_time: 0,
        error: 'Audio processing error'
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Legal Assistant</h1>
        <p>Ask legal questions and get answers with citations</p>
      </header>

      <main className="App-main">
        <div className="query-section">
          <h2>Text Query</h2>
          <div className="text-input">
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask a legal question..."
              rows={3}
              disabled={loading}
            />
            <button 
              onClick={handleTextQuery} 
              disabled={loading || !query.trim()}
            >
              {loading ? 'Processing...' : 'Ask Question'}
            </button>
          </div>
        </div>

        <div className="query-section">
          <h2>Voice Query</h2>
          <div className="audio-controls">
            {!isRecording ? (
              <button onClick={startRecording} disabled={loading}>
                🎤 Start Recording
              </button>
            ) : (
              <button onClick={stopRecording} className="recording">
                ⏹️ Stop Recording
              </button>
            )}
            
            {audioBlob && (
              <button 
                onClick={handleAudioQuery} 
                disabled={loading}
                className="submit-audio"
              >
                {loading ? 'Processing...' : '🔍 Submit Audio Query'}
              </button>
            )}
          </div>
        </div>

        {response && (
          <div className="response-section">
            <h2>Response</h2>
            {response.fallback_mode && (
              <div className="fallback-notice">
                ⚠️ Running in fallback mode (Ollama unavailable)
              </div>
            )}
            
            <div className="answer">
              <h3>Answer:</h3>
              <p>{response.answer}</p>
            </div>

            {response.citations.length > 0 && (
              <div className="citations">
                <h3>Sources ({response.sources_used}):</h3>
                <ul>
                  {response.citations.map((citation, index) => (
                    <li key={index}>
                      <strong>{citation.title}</strong>
                      {citation.source_url && (
                        <a href={citation.source_url} target="_blank" rel="noopener noreferrer">
                          🔗 View Source
                        </a>
                      )}
                      <span className="score">Score: {citation.score}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div className="metadata">
              <small>
                Processing time: {response.processing_time.toFixed(2)}s
                {response.error && ` | Error: ${response.error}`}
              </small>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
