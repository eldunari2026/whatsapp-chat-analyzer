import React, { useState } from 'react';

export default function Results({ result, parseResult }) {
  const [openParticipant, setOpenParticipant] = useState(null);

  // Parse-only result
  if (parseResult) {
    return (
      <div className="results">
        <div className="stats-row">
          <div className="stat">
            <span className="stat-value">{parseResult.message_count}</span>
            <span className="stat-label">Messages</span>
          </div>
          <div className="stat">
            <span className="stat-value">{parseResult.participants.length}</span>
            <span className="stat-label">Participants</span>
          </div>
          <div className="stat">
            <span className="stat-value">
              {parseResult.start_date
                ? `${parseResult.start_date.slice(0, 10)} to ${parseResult.end_date.slice(0, 10)}`
                : 'N/A'}
            </span>
            <span className="stat-label">Date Range</span>
          </div>
        </div>
        <div className="section">
          <h3>Participants</h3>
          <p>{parseResult.participants.join(', ')}</p>
        </div>
        <div className="section">
          <h3>Messages</h3>
          <div className="messages-list">
            {parseResult.messages.slice(0, 100).map((m, i) => (
              <div key={i} className={`message ${m.is_system ? 'system' : ''}`}>
                <span className="msg-time">{m.timestamp.slice(0, 16).replace('T', ' ')}</span>
                {!m.is_system && <span className="msg-sender">{m.sender}</span>}
                <span className="msg-content">{m.content}</span>
              </div>
            ))}
            {parseResult.messages.length > 100 && (
              <p className="muted">Showing first 100 of {parseResult.messages.length} messages</p>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Full analysis result
  if (!result) return null;

  return (
    <div className="results">
      <div className="stats-row">
        <div className="stat">
          <span className="stat-value">{result.message_count}</span>
          <span className="stat-label">Messages</span>
        </div>
        <div className="stat">
          <span className="stat-value">{result.participant_count}</span>
          <span className="stat-label">Participants</span>
        </div>
        <div className="stat">
          <span className="stat-value">{result.date_range || 'N/A'}</span>
          <span className="stat-label">Date Range</span>
        </div>
      </div>

      {result.summary && (
        <div className="section">
          <h3>Summary</h3>
          <p>{result.summary}</p>
        </div>
      )}

      <div className="two-col">
        {result.topics.length > 0 && (
          <div className="section">
            <h3>Key Topics</h3>
            <ul>
              {result.topics.map((t, i) => (
                <li key={i}>{t}</li>
              ))}
            </ul>
          </div>
        )}

        {result.action_items.length > 0 && (
          <div className="section">
            <h3>Action Items</h3>
            <ul>
              {result.action_items.map((a, i) => (
                <li key={i}>{a}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {Object.keys(result.participant_summaries).length > 0 && (
        <div className="section">
          <h3>Participant Analysis</h3>
          <div className="participant-list">
            {Object.entries(result.participant_summaries).map(([name, summary]) => (
              <div key={name} className="participant-card">
                <button
                  className="participant-toggle"
                  onClick={() =>
                    setOpenParticipant(openParticipant === name ? null : name)
                  }
                >
                  <span>{name}</span>
                  <span>{openParticipant === name ? '−' : '+'}</span>
                </button>
                {openParticipant === name && (
                  <div className="participant-summary">{summary}</div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
