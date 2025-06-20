import React from 'react';

const SentimentBar = ({ aspect, score, sentiment }) => {


  // Round the score to 2 decimal places
  let roundedScore = 0

  if (sentiment == 'Positive') {
    roundedScore = (score * 100).toFixed(2);
  }else{
    roundedScore = (100 - (score * 100)).toFixed(2);
  }

  // Bar color based on score percentage
  const barFilledPercentage = `${roundedScore}%`;

  return (
    <div style={{ marginBottom: '15px', borderRadius: '8px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '-30px', marginTop:'15px' }}>
        <span style={{ color: 'white', marginLeft: '15px' }}>{aspect}</span>
        <span style={{ color: 'black' }}>{roundedScore} %</span>
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
            width: barFilledPercentage,
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
