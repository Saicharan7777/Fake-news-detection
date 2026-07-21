import React, { useState } from 'react';

const NewsForm = ({ onSubmit, isLoading }) => {
  const [text, setText] = useState('');

  const wordCount = text.trim() === '' ? 0 : text.trim().split(/\s+/).length;
  const charCount = text.length;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (text.trim().length < 10) return;
    onSubmit(text);
  };

  const handleClear = () => {
    setText('');
  };

  return (
    <div className="card news-form-card">
      <h2>Paste News Article</h2>
      
      <form onSubmit={handleSubmit}>
        <div className="textarea-container">
          <textarea
            placeholder="Paste news article text here (at least 10 characters)..."
            value={text}
            onChange={(e) => setText(e.target.value)}
            disabled={isLoading}
            rows={10}
          />
          {text.length > 0 && (
            <button 
              type="button" 
              className="btn-clear" 
              onClick={handleClear} 
              disabled={isLoading}
            >
              Clear
            </button>
          )}
        </div>

        <div className="form-meta">
          <div className="counters">
            <span>Words: {wordCount}</span>
            <span>Characters: {charCount}</span>
          </div>
          {text.trim().length > 0 && text.trim().length < 10 && (
            <span className="warning-text">Input is too short (min. 10 chars)</span>
          )}
        </div>

        <button
          type="submit"
          className="btn btn-primary"
          disabled={isLoading || text.trim().length < 10}
        >
          {isLoading ? 'Analyzing Article...' : 'Check News'}
        </button>
      </form>
    </div>
  );
};

export default NewsForm;
