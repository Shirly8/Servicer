import React from 'react';
import './Components.css'
import { useState, useEffect } from 'react'
import star from '../images/star.png'
import buffer from '../images/Buffer.png'
import SentimentBar from '../Components/SentimentBar'
import ModelAnalysis from './ModelAnalysis';


function SentimentIQ() {
  const [reviews, setReviews] = useState([]);
  const [ratings, setRatings] = useState("");
  const [reviewGenerated, setReviewsGenerated] = useState(false);
  const [sentimentScore, setSentimentScore] = useState(null);
  const [reviewText,setReviewText] = useState("");
  const [metrics, setMetrics] = useState({ accuracy: 0, f1: 0, precision: 0, recall: 0 });
  const [loading, setLoading] = useState(false);
  const [aspectAnalysis, setAspectAnalysis] = useState([]);
  const [showModelAnalysis, setShowModelAnalysis] = useState(false);
  const [reviewaspect, setReviewAspect] = useState([]);


  

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

      if (response.ok) {
        const data = await response.json(); 
        setReviews(data); 
        fetchMetrics();
      }else {
        console.log("Error fetching data")
      }

    } catch (error) {
      console.error('Error generating reviews:', error);
    } finally{
      
      setLoading(false);
    }
  };


  //Analyze the Sentiment
  const analyzeSentiment = async () => {
    try {
      const response = await fetch('/analyzeSentiment', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: reviewText }),
      });
  
      const data = await response.json();
      console.log(data)
      console.log(data.score)
      
      setAspectAnalysis(data.aspect_analysis);


      setSentimentScore(data.score);
    } catch (error) {
      console.log('Error getting sentiment score: ', error);
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
        setMetrics(data.results);
        setReviewsGenerated(true);
        setReviewAspect(data.abasresults)
        console.log(data.abasresults)

    } catch (error) {
        console.log("Error fetching metrics: ", error);
    }
};


    useEffect(()=> {
      generateReviews();
    }, []);

    const handleModelAnalysisPopup = () => {
      setShowModelAnalysis(true); 
    };
  
    const closeModelAnalysisPopup = () => {
      setShowModelAnalysis(false);
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
          placeholder='Click on any of the past reviews and see its sentiment analysis on the XL-NET Model'
          ></textarea>
          <div className="send-icon" style = {{width: "1em", position: "relative", top: "-67px", left: "53%"}} onClick = {analyzeSentiment}/>

          {sentimentScore != null && (
          <div style = {{marginTop: '-40px'}}>
            <h3 style = {{textAlign: "center", fontFamily: "Arial"}}>Sentiment Score: </h3>
            <div className = "ratingtext2">
              <h1> {(sentimentScore * 100).toFixed(2)} %</h1>
            </div>

            {/* Render Sentiment Bars for each aspect */}
        <div className = "sentimentBar">
          {aspectAnalysis.map((aspect, index) => (
            <SentimentBar key={index} aspect={aspect.Aspect} score={aspect.Score} sentiment = {aspect.Sentiment} />
          ))}
        </div>
            
          </div>
          )}
        
        </div>

        <div className = "half1">
        <h1 className = "miniheading">Sample Reviews</h1>

        {loading ? (
          <div className = "loadingspace">
          <div className = "loading">
            <img src = {buffer} className = "spinner"></img>
            <p style = {{color: "#436176"}}> <strong> LLMs (Meta Llama 3)</strong> help create realistic customer reviews, enabling our <strong>XLNET model</strong> to evaluate sentiment analysis effectiveness.
            <br></br> <br></br>
            <strong>Iterative Learning </strong> allows the model to get repeatedly trained on new data. This iterative process allows the model to learn from its errors, adjust its weights, and improve its ability to predict sentiment more accurately
            </p>
          </div>
          </div>
        ): (
          <div className = "reviews">
          {reviews.map((review,index) => (
           
          <div key = {index} className = "review" onClick={() => setReviewText(review.text.replace(/['"]+/g, ''))}>
            <div className = "ratingtext">
            <h2>{review.rating}</h2> 
            <img src = {star} style = {{height: "2em"}}></img>
            </div>
          
            <p style = {{fontSize: "11px"}}>{review.text}</p>
          </div>
                    
          ))}
          <button className = "generateReview" onClick = {generateReviews}>ReGenerate</button>

        </div>
        )}
            {reviewGenerated && (
            <button onClick={handleModelAnalysisPopup}> See Model Analysis</button>
          )}

        </div>
        {/* Display ModelAnalysis popup */}
        {showModelAnalysis && (
            <ModelAnalysis
              metrics={metrics}
              reviewaspect={reviewaspect}
              onClose={closeModelAnalysisPopup}
            />
          )}
        
    </div>
    </div>
    </>
  )
}

export default SentimentIQ
