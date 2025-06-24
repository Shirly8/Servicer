import React, { useState, useEffect, useRef } from 'react';
import './Components.css'
import star from '../images/star.png'
import buffer from '../images/Buffer.png'
import SentimentBar from '../Components/SentimentBar'
import ModelAnalysis from '../Components/ModelAnalysis'


function SentimentIQ() {
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [reviewText,setReviewText] = useState("");
  const [aspectAnalysis, setAspectAnalysis] = useState([]);
  const [modelMetrics, setModelMetrics] = useState(null);
  const [showModelAnalysis, setShowModelAnalysis] = useState(false);

  // Fetch initial reviews from the CSV on component mount
  useEffect(() => {
    const fetchInitialReviews = async () => {
      try {
        const response = await fetch('/getInitialReviews');
        if (response.ok) {
          const data = await response.json();
          setReviews(data.reverse()); 
          // Fetch model metrics after reviews are loaded
          fetchModelMetrics();
        } else {
          console.error("Error fetching initial reviews:", response.statusText);
          setReviews([]);
        }
      } catch (error) {
        console.error('Error fetching initial reviews:', error);
        setReviews([]);
      } finally {
        setLoading(false);
      }
    };

    fetchInitialReviews();
  }, []); 

  // Fetch model evaluation metrics
  const fetchModelMetrics = async () => {
    setModelMetrics(null); // Show loading state
    try {
      const response = await fetch('/computeMetrics');
      if (response.ok) {
        const data = await response.json();
        setModelMetrics(data);
      }
    } catch (error) {
      console.error('Error fetching model metrics:', error);
    }
  };

  //GENERATE a single NEW SYNTHETIC REVIEW
  const generateNewReviews = async () => {
    setLoading(true);
    setAspectAnalysis([]);
    setReviewText('');
    try {
      // 1. Trigger backend to regenerate reviews
      await fetch('/generateReviews', { method: 'POST' });
      // 2. Fetch the new reviews
      const response = await fetch('/getInitialReviews');
      if (response.ok) {
        const data = await response.json();
        setReviews(data.reverse());
        // Fetch model metrics after new reviews are loaded
        fetchModelMetrics();
      }
    } catch (error) {
      console.error('Error generating new reviews:', error);
    } finally {
      setLoading(false);
    }
  };


  //Analyze the Sentiment
  const analyzeSentiment = async () => {
    if (!reviewText) return;
    try {
      const response = await fetch('/analyzeSentiment', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: reviewText }),
      });
  
      const data = await response.json();
      
      // The backend returns an object like { "Service": 1, "Food": 5 }.
      // We need to convert it to an array of objects for mapping.
      const analysisArray = Object.entries(data.aspect_analysis || {}).map(([aspect, stars]) => ({
        Aspect: aspect,
        Stars: stars,
      }));
      setAspectAnalysis(analysisArray);

    } catch (error) {
      console.log('Error getting sentiment score: ', error);
    }
  };

  // Compute average star rating for each aspect from reviews
  const computeAspectAverages = () => {
    const aspectSums = {};
    const aspectCounts = {};
    reviews.forEach(r => {
      if (r.message && r.rating && r.aspect) {
        const aspect = r.aspect;
        const rating = parseFloat(r.rating);
        if (!isNaN(rating)) {
          aspectSums[aspect] = (aspectSums[aspect] || 0) + rating;
          aspectCounts[aspect] = (aspectCounts[aspect] || 0) + 1;
        }
      }
    });
    const averages = {};
    Object.keys(aspectSums).forEach(aspect => {
      averages[aspect] = aspectSums[aspect] / aspectCounts[aspect];
    });
    return averages;
  };

  return (
    <>
    <div style = {{height: "100vh"}}>
    <h1 style = {{fontSize: "45px", textAlign: "center"}}> SentimentIQ</h1>
    <p style= {{paddingLeft: "10%", paddingRight:"10%", fontSize: "13px"}}>
      SentimentIQ, a powerful tool that offers businesses a sophisicated way to understand customer sentiment,
      providing insights into how your customers feel about your products or services. 
      By integrating NLP techniques, real-time analysis and robust evaluation metrics, 
      SentimentIQ captures your customer reviews, continuously improving our model to provide you with the most accurate sentiment score possible.
    </p>
    
      <div className = "halves">
        
        <div className = "half2">
          <h1 className = "miniheading">Enter Review</h1>

          <textarea className = "reviewinput" style = {{height: "100px"}}
          value = {reviewText}
          onChange = {(e) => setReviewText(e.target.value)}
          placeholder='Click on any of the past reviews and see its sentiment analysis on the ABSA Model'
          ></textarea>
          <div className="send-icon" style = {{width: "1em", position: "relative", top: "-67px", left: "53%"}} onClick = {analyzeSentiment}/>

<div className = "aspectbar">
          {aspectAnalysis.length > 0 && (
            <div style = {{marginTop: '-40px'}}>
              <h3 style = {{textAlign: "center", fontFamily: "Arial"}}>Aspect Analysis:</h3>
              <div className = "sentimentBar">
                {aspectAnalysis.map((aspect, index) => (
                  <SentimentBar key={index} aspect={aspect.Aspect} score={aspect.Stars} />
                ))}
              </div>
            </div>
          )}
        </div>

  </div>
        <div className = "half1">
          <h1 className = "miniheading">Sample Reviews</h1>

          {loading && reviews.length === 0 ? (
            <div className = "loadingspace">
              <div className = "loading">
                <img src = {buffer} className = "spinner" alt="Loading..."></img>
                <p style = {{color: "#436176"}}>Loading initial reviews...</p>
              </div>
            </div>
          ) : reviews.length === 0 ? (
            <div className = "loadingspace">
              <div className = "loading" style={{justifyContent: 'center', alignItems: 'center', textAlign: 'center'}}>
                <button className = "generateReview" onClick = {generateNewReviews}>Generate New Reviews</button>
                <p style={{color: "#436176", marginTop: '30px'}}>
                  Could not load initial reviews. <br/>
                </p>
              </div>
            </div>
          ) : (
            <div className="reviewbox">
              <div style={{ display: 'flex', flexDirection: 'row', gap: '10px', width: '100%', justifyContent: 'center', marginBottom: '10px' }}>
                <button
                  className="generateReview"
                  onClick={generateNewReviews}
                  disabled={loading}
                >
                  {loading ? 'Generating...' : 'Generate New Reviews'}
                </button>
                <button
                  className="generateReview"
                  onClick={() => setShowModelAnalysis(true)}
                  disabled={!modelMetrics}
                >
                  Model Analysis
                </button>
              </div>
              <div className="reviews">
                {loading && reviews.length === 0 &&
                  <div className="loading-bar-placeholder">Waiting for first review...</div>
                }
                {reviews.map((review, index) => (
                  <div key={index} className="review" onClick={() => setReviewText(review.message.replace(/['"]+/g, ''))}>
                    <div className="ratingtext">
                      <h2>{review.rating}</h2>
                      <img src={star} style={{ height: "2em" }} alt="star" />
                    </div>
                    <p style={{fontSize: "11px"}}>{review.message}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
    {/* Render ModelAnalysis popup at the root level so it overlays the UI */}
    {modelMetrics && showModelAnalysis && (
      <ModelAnalysis
        metrics={modelMetrics}
        aspectAverages={modelMetrics.aspect_averages}
        reviewaspect={modelMetrics.full_report ? modelMetrics.full_report : {}}
        onClose={() => setShowModelAnalysis(false)}
      />
    )}
    </>
  )
}

export default SentimentIQ
