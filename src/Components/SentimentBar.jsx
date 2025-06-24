import React from 'react';

const SentimentBar = ({ aspect, score, isStarRating = true }) => {
  let barFill = 0;
  let label = "";

  if (isStarRating) {
    // Clamp score between 1 and 5
    const safeScore = Math.max(1, Math.min(5, score));
    barFill = (safeScore / 5) * 100;
    label = `${safeScore}/5`;
  } else {
    // Clamp score between 0 and 1
    const safeScore = Math.max(0, Math.min(1, score));
    barFill = safeScore * 100;
    label = `${(safeScore * 100).toFixed(2)}%`;
  }

  return (
    <div style={{ marginBottom: '15px', borderRadius: '8px', width: '100%' }}>
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '-30px', marginTop:'15px' }}>
        <span style={{ color: 'black', marginLeft: '15px', marginRight: '10px' }}>{label}</span>
        <span style={{ color: 'white' }}>{aspect}</span>
      </div>
      <div
        style={{
          width: '100%',
          height: '40px',
          backgroundColor: '#99bccd', // unfilled color
          borderRadius: '12px',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            width: `${barFill}%`,
            height: '35px',
            backgroundColor: '#436176', // filled color
            borderRadius: '12px',
            border: '2px solid white',
          }}
        ></div>
      </div>
    </div>
  );
};

export default SentimentBar;
