import React, { useEffect, useState } from 'react';
import './Components.css';
import star from '../images/star.png';

const AspectReviewList = ({ aspect }) => {
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!aspect) return;
    setLoading(true);
    fetch(`/getReviewsForAspect?aspect=${encodeURIComponent(aspect)}`)
      .then(res => res.json())
      .then(data => {
        setReviews(data);
        setLoading(false);
      })
      .catch(() => {
        setReviews([]);
        setLoading(false);
      });
  }, [aspect]);

  return (
    <div style={{ background: '#222', color: '#fff', padding: '10px', borderRadius: '8px', margin: '10px 0', overflowX: 'auto' }}>
      {loading ? (
        <p>Loading...</p>
      ) : reviews.length === 0 ? (
        <p>No reviews for this aspect.</p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'row', gap: '18px', overflowX: 'auto', paddingBottom: '10px' }}>
          {reviews.map((r, i) => (
            <div
              key={i}
              style={{
                minWidth: '220px',
                maxWidth: '260px',
                background: '#222',
                border: '2px solid white',
                borderRadius: '18px',
                padding: '18px 16px 12px 16px',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '8px' }}>
                {Array.from({ length: Math.max(0, Math.floor(Number(r.rating))) }).map((_, idx) => (
                  <img
                    key={idx}
                    src={star}
                    alt="star"
                    style={{ height: '28px', width: '28px', margin: '0 2px' }}
                  />
                ))}
              </div>
              <div style={{ textAlign: 'center', fontSize: '14px', marginTop: '6px', wordBreak: 'break-word' }}>
                {r.message}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AspectReviewList;
