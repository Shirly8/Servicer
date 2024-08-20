import React from 'react';
import { useState, useEffect } from 'react'
import './Components.css';
import star from '../images/star.png'
import buffer from '../images/Buffer.png'


function SentimentIQ() {
  const [reviews, setReviews] = useState([]);
  const [ratings, setRatings] = useState("");
  const [reviewGenerated, setReviewsGenerated] = useState(false);
  const [sentimentScore, setSentimentScore] = useState(null);
  const [reviewText,setReviewText] = useState("");
  const [metrics, setMetrics] = useState({ accuracy: 0, f1: 0, precision: 0, recall: 0 });
  const [loading, setLoading] = useState(false);
  

  //GENERATE SYNTHETIC REVIEW
  const generateReviews = async () => {
    setLoading(true)
    try {
      const response = await fetch('/generateReviews', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ratings})
      });


      //Sending review to LLM
      const data = await response.json();
      setReviews([]);
      setReviews(data);
      setReviewsGenerated(true);

      //Get the metrics after generating the reviews
      // fetchMetrics();

    }catch (error){
      console.log("Error generating reviews: ", error)
    }finally {
      setLoading(false)
    }
  }


  //Analyze the Sentiment
  const analyzeSentiment = async () => {
    try {
      const response = await fetch ('/analyzeSentiment', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({text: reviewText})
      });
      

      //Get the sentiment score
      const data = await response.json();
      setSentimentScore(data.score);
    }catch (error) {
      console.log("Error getting sentiment score: ", error);
    }
  };


  //FETCH THE METRICS:
    const fetchMetrics = async () => {
      try {
        const response = await fetch('/computeMetrics', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json'
          }
        });
  
        const data = await response.json();
        setMetrics(data);
      } catch (error) {
        console.log("Error fetching metrics: ", error);
      }
    };

    useEffect(()=> {
      generateReviews();
    }, []);

  return (
    <>

<div className = "full">
    <h1 style = {{fontSize: "45px", textAlign: "center"}}> SentimentIQ</h1>
    <p style= {{paddingLeft: "10%", paddingRight:"10%", fontSize: "13px"}}>
      SentimentIQ, a powerful tool that offers businesses a sophisicated way to understand customer sentiment,
      providing insights into how your customers feel about your products or services. 
      By integrating NLP techniques, real-time analysis and robust evaluation metrics, 
      SentimentIQ captures your customer reviews, continuously improving our model to provide you with the most accurate sentiment score possible.
      </p>
    
      <div className = "halves">
        <div className = "half1">
        <h1 className = "miniheading">Past Reviews</h1>

        {loading ? (
          <div className = "loading">
            <img src = {buffer} className = "spinner"></img>
          </div>

        ): (
          <div className = "reviews">
          {reviews.map((review,index) => (
           
          <div key = {index} className = "review">
            <div className = "ratingtext">
            <h2>{review.rating}</h2> 
            <img src = {star} style = {{height: "2em"}}></img>
            </div>
          
            <p style = {{fontSize: "11px"}}>{review.text}</p>
          </div>
                    
          ))}
          <button className = "generateReview" onClick = {generateReviews}>Re-generate</button>

        </div>
        )}


        </div>


        <div className = "half2">
          <h1 className = "miniheading">Enter Review</h1>

          <textarea className = "reviewinput" 
          value = {reviewText}
          onChange = {(e) => setReviewText(e.target.value)}
          ></textarea>
          <div className="send-icon" onClick = {analyzeSentiment}/>

          {sentimentScore !=null && (
          <div style = {{marginTop: '-15px'}}>
            <h3>Sentiment Score: </h3>
            <div className = "ratingtext2">
              <h1> {sentimentScore.toFixed(0)}</h1>
              <img src = {star} style = {{height: "4em"}}></img>
            </div>

          </div>
          )}

{/* 
          {reviewGenerated && (
            <div className = "evaluatetable">
              <h2 className = "evaluateTitle" > Model Analysis </h2>

              <div className="evaluatebox">
                <div className="metric">
                  <h3>Accuracy</h3>
                  <p className = "metricPara">{(metrics.accuracy * 100).toFixed(2)}%</p>
                </div>
                <div className="metric">
                  <h3>F1 Score</h3>
                  <p className = "metricPara">{(metrics.f1 * 100).toFixed(2)}%</p>
                </div>
                <div className="metric">
                  <h3>Precision</h3>
                  <p className = "metricPara">{(metrics.precision * 100).toFixed(2)}%</p>
                </div>
                <div className="metric">
                  <h3>Recall</h3>
                  <p className = "metricPara">{(metrics.recall * 100).toFixed(2)}%</p>
                </div>
              </div>

            </div>

          )}
         */}
        </div>


    </div>
    </div>
    </>
  )
}

export default SentimentIQ
