import React from 'react';
import './Components.css'
import Papa from 'papaparse';
import { useState, useEffect } from 'react'
import star from '../images/star.png'
import buffer from '../images/Buffer.png'

function SentimentIQ() {
  const [reviews, setReviews] = useState([]);
  const [reviewGenerated, setReviewsGenerated] = useState(false);
  const [sentimentScore, setSentimentScore] = useState(null);
  const [reviewText,setReviewText] = useState("");
  const [metrics, setMetrics] = useState({ accuracy: 0, f1: 0, precision: 0, recall: 0 });
  const [loading, setLoading] = useState(true);
  const [score, setScore] = useState(null);
  const [sentiment, setSentiment] = useState(null);
  const [sentimentText, setSentimentText] = useState(null);
  

  //GENERATE SYNTHETIC REVIEW
  const generateReviews = async () => {
      // Fetch from CSV if status is 403
      return fetch('/Files/reviews.csv')
      
          .then(response => response.text())
          .then(data => {
            const parsedData = Papa.parse(data, { header: true });
            
            const first4Reviews = parsedData.data.map(item => ({
              text: item.Review,
              rating: item.Rating
            }));

            setReviews(first4Reviews);

            // Simulate loading for 5 seconds
              setTimeout(() => {
              setLoading(false);
              fetchMetrics()
          }, 5000);

          });
        }


  //Analyze the Sentiment
  const analyzeSentiment = async () => {
    fetch('/Files/SentimentScores.csv')
    .then(response => response.text())
    .then(data => {
      const parsedData = Papa.parse(data, { header: true });
      const matchedReview = parsedData.data.find(review => review.Review === reviewText);
      setSentimentScore(matchedReview.Rating);
      setScore(matchedReview.Score);

      if (matchedReview.Score > 0.90) {
        setSentiment('lightgreen')
        setSentimentText('Positive')
      }else if (matchedReview.Score > 0.5) {
        setSentiment('yellow')
        setSentimentText('Neutral')
      }else {
        setSentiment("lightcoral")
        setSentimentText('Negative')
      }
    });
  };

  // const analyzeSentiment = async () => {

  //FETCH THE METRICS:
    const fetchMetrics = async () => {
      fetch('/Files/modelEval.json')
      .then(response => response.json())

      .then(data => {
          setMetrics({
            accuracy: data.accuracy,
            precision: data.precision,
            recall: data.recall,
            f1: data.f1
        })
        setReviewsGenerated(true)
    });
  }

    useEffect(()=> {
      generateReviews();
    }, []);

  return (
    <>
    <div style = {{height: "100vh"}}>
    <h1 style = {{fontSize: "45px", textAlign: "center"}}> SentimentIQ</h1>
    <p style= {{paddingLeft: "10%", paddingRight:"10%", fontSize: "13px"}}>
      SentimentIQ, a powerful tool that offers businesses a sophisicated way to understand customer sentiment,
      providing insights into how your customers feel about your products or services. 
      By integrating NLP techniques, real-time analysis and robust evaluation metrics, 
      SentimentIQ captures your customer reviews, continuously improving our model to provide you with the most accurate sentiment score possible.
      <br></br><br></br>
      <em>Note: The back-end server has been disabled for this deployment, so some features may not be available.</em>
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
           
          <div key = {index} className = "review" onClick = {() => setReviewText(review.text)} >
            <div className = "ratingtext">
            <h2 className = "heading2">{review.rating}</h2> 
            <img src = {star} style = {{height: "2em"}}></img>
            </div>
          
            <p style = {{fontSize: "11px"}}>{review.text}</p>
          </div>
                    
          ))}
        </div>
        )}


        </div>


        <div className = "half2">
          <h1 className = "miniheading">Try our NLP Model</h1>

          <textarea className = "reviewinput" style = {{height: "125px"}}
          value = {reviewText}
          onChange = {(e) => setReviewText(e.target.value)}
          placeholder = {`Click on any of the past reviews and see its sentiment analysis on the XLNET Model`}
          disabled
          ></textarea>
          <div className="send-icon" style = {{width: "1em", position: "relative", top: "-70px", left: "53%"}}onClick = {analyzeSentiment}/>

          {sentimentScore !=null && (
          <div className = "modelscore">

            <div className = "scoretext">
              <h3>Sentiment Score: </h3>
              <div className = "ratingtext3">
              <h1 style = {{color: sentiment}}> {(score * 100).toFixed(2)}%</h1>
              <p className = "sentimenttext" style = {{color: sentiment}}>{sentimentText}</p>
            </div>
            </div>
            
            <div className = "scoretext">
            <h3>Sentiment Rating: </h3>
            <div className = "ratingtext2">
              <h1> {sentimentScore}</h1>
              <img src = {star} style = {{height: "4em"}}></img>
            </div>
            </div>
            
  
          </div>
          )}


          {reviewGenerated && (
            <div className = "evaluatetable">
              <h2 className = "evaluateTitle" >Current Model Analysis </h2>

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
        
        </div>


    </div>
    </div>
    </>
  )
}

export default SentimentIQ
