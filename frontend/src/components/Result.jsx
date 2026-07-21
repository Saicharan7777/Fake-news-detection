import React from 'react';

const Result = ({ result }) => {
  if (!result) {
    return (
      <div className="card result-card empty-state">
        <h3>No Analysis Performed Yet</h3>
        <p>Enter text on the left and click 'Check News' to check validity.</p>
      </div>
    );
  }

  const { predictionResult, confidenceScore, savedToDb } = result;
  const isReal = predictionResult === 'Real';
  
  // Calculate the probability of the news being Fake
  const fakePercentage = isReal ? (100 - confidenceScore) : confidenceScore;
  const roundedFakePercentage = Math.round(fakePercentage * 100) / 100;

  return (
    <div className="card result-card outcome-card">
      <div className="outcome-body">
        <div className="simple-percentage">
          Likelihood of Fake News: <span className="percentage-value-highlight">{roundedFakePercentage}%</span>
        </div>
        
        <div className="result-meta">
          <span className="model-accuracy">Model Accuracy: 99.98%</span>
          {savedToDb && (
            <span className="db-badge db-success">
              Atlas Save Status: Successful
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

export default Result;
