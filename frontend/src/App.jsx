import React, { useState } from 'react';
import axios from 'axios';
import NewsForm from './components/NewsForm';
import Result from './components/Result';
import './App.css';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://fake-news-backend-jxwo.onrender.com';

function App() {
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleCheckNews = async (newsText) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/predict`, { newsText });
      setResult(response.data);
    } catch (err) {
      console.error(err);
      const errMsg = err.response?.data?.error || err.response?.data?.details || 'Could not communicate with the server.';
      setError(errMsg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-wrapper">
      <nav className="navbar">
        <div className="navbar-container">
          <div className="navbar-brand">
            <span className="brand-name">Fake News Detector</span>
          </div>
        </div>
      </nav>

      <main className="container main-content">
        {error && (
          <div className="banner banner-warning">
            Error: {error}
          </div>
        )}

        <div className="dashboard-grid">
          <div className="column-left">
            <NewsForm onSubmit={handleCheckNews} isLoading={isLoading} />
          </div>

          <div className="column-right">
            <Result result={result} />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
