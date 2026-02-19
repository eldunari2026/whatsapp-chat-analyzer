import React, { useState, useEffect } from 'react';
import ChatInput from './components/ChatInput';
import Filters from './components/Filters';
import Results from './components/Results';
import { checkHealth, parseText, parseFile, analyzeText, analyzeFile } from './api/client';

export default function App() {
  const [filters, setFilters] = useState({ participant: '', startDate: '', endDate: '' });
  const [result, setResult] = useState(null);
  const [parseResult, setParseResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [health, setHealth] = useState(null);

  useEffect(() => {
    checkHealth()
      .then(setHealth)
      .catch(() => setHealth({ status: 'unreachable', ollama_available: false }));
  }, []);

  const handleSubmitText = async (text, mode) => {
    setLoading(true);
    setError(null);
    setResult(null);
    setParseResult(null);
    try {
      if (mode === 'parse') {
        setParseResult(await parseText(text));
      } else {
        setResult(await analyzeText(text, filters));
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitFile = async (file, mode) => {
    setLoading(true);
    setError(null);
    setResult(null);
    setParseResult(null);
    try {
      if (mode === 'parse') {
        setParseResult(await parseFile(file));
      } else {
        setResult(await analyzeFile(file, filters));
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header>
        <h1>WhatsApp Chat Analyzer</h1>
        <p className="subtitle">LLM-powered analysis using self-hosted Llama</p>
        {health && (
          <div className={`health ${health.ollama_available ? 'ok' : 'warn'}`}>
            {health.ollama_available
              ? `Connected - ${health.model}`
              : health.status === 'unreachable'
              ? 'Backend unreachable'
              : 'Ollama not available'}
          </div>
        )}
      </header>

      <div className="layout">
        <aside>
          <Filters filters={filters} setFilters={setFilters} />
        </aside>
        <main>
          <ChatInput
            onSubmitText={handleSubmitText}
            onSubmitFile={handleSubmitFile}
            loading={loading}
          />

          {loading && (
            <div className="loading">
              <div className="spinner" />
              <p>Analyzing with Llama... This may take 30-60 seconds on CPU.</p>
            </div>
          )}

          {error && <div className="error">{error}</div>}

          <Results result={result} parseResult={parseResult} />
        </main>
      </div>
    </div>
  );
}
