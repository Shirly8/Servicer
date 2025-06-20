import React from 'react';
import SentimentBar from './SentimentBar';
import './Components.css';

const ModelAnalysis = ({ metrics, reviewaspect, onClose }) => {
  // Convert the reviewaspect object to an array of [key, value] pairs
  const aspectEntries = Object.entries(reviewaspect);

  return (
    <div className="model-analysis-popup">
      <div className="model-analysis-content">
        <h2 style = {{"backgroundColor": "#436176"}}>Model Analysis</h2>

        {/* Model Metrics */}
        <div className="evaluateTable">
          <div className="metric">
            <h3>Accuracy</h3>
            <p>{(metrics.accuracy * 100).toFixed(2)}%</p>
          </div>
          <div className="metric">
            <h3>F1 Score</h3>
            <p>{(metrics.f1 * 100).toFixed(2)}%</p>
          </div>
          <div className="metric">
            <h3>Precision</h3>
            <p>{(metrics.precision * 100).toFixed(2)}%</p>
          </div>
          <div className="metric">
            <h3>Recall</h3>
            <p>{(metrics.recall * 100).toFixed(2)}%</p>
          </div>
        </div>


        <h2 style = {{"backgroundColor": "#436176"}}>Restaurant Overall Sentiment</h2>

          {/* Render Sentiment Bars for each aspect */}
          <div className="sentimentBars">
          {aspectEntries.map(([aspect, score], index) => (
            <SentimentBar key={index} aspect={aspect} score={score} sentiment={score >= 0.5 ? 'Positive' : 'Negative'} />
          ))}
        </div>

        <button className="close-button" onClick={onClose}>Close</button>
      </div>
    </div>
  );
};

export default ModelAnalysis;
