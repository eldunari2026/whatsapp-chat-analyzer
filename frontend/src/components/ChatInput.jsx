import React, { useState } from 'react';

export default function ChatInput({ onSubmitText, onSubmitFile, loading }) {
  const [tab, setTab] = useState('paste');
  const [text, setText] = useState('');
  const [file, setFile] = useState(null);

  const handleTextSubmit = (mode) => {
    if (text.trim()) onSubmitText(text.trim(), mode);
  };

  const handleFileSubmit = (mode) => {
    if (file) onSubmitFile(file, mode);
  };

  return (
    <div className="chat-input">
      <div className="tabs">
        <button
          className={tab === 'paste' ? 'tab active' : 'tab'}
          onClick={() => setTab('paste')}
        >
          Paste Text
        </button>
        <button
          className={tab === 'upload' ? 'tab active' : 'tab'}
          onClick={() => setTab('upload')}
        >
          Upload File
        </button>
      </div>

      {tab === 'paste' && (
        <div className="tab-content">
          <textarea
            rows={12}
            placeholder="Paste WhatsApp chat text here..."
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
          <div className="actions">
            <button
              onClick={() => handleTextSubmit('parse')}
              disabled={loading || !text.trim()}
            >
              Parse Only
            </button>
            <button
              className="primary"
              onClick={() => handleTextSubmit('analyze')}
              disabled={loading || !text.trim()}
            >
              {loading ? 'Analyzing...' : 'Full Analysis'}
            </button>
          </div>
        </div>
      )}

      {tab === 'upload' && (
        <div className="tab-content">
          <div className="file-drop">
            <input
              type="file"
              accept=".txt,.pdf,.docx,.png,.jpg,.jpeg,.webp"
              onChange={(e) => setFile(e.target.files[0] || null)}
            />
            {file && <p className="file-name">Selected: {file.name}</p>}
          </div>
          <div className="actions">
            <button
              onClick={() => handleFileSubmit('parse')}
              disabled={loading || !file}
            >
              Parse Only
            </button>
            <button
              className="primary"
              onClick={() => handleFileSubmit('analyze')}
              disabled={loading || !file}
            >
              {loading ? 'Analyzing...' : 'Full Analysis'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
