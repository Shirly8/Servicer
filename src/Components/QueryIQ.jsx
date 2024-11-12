import React from 'react';
import { useState, useEffect } from 'react'
import Fuse from 'fuse.js'
import './QueryChat.css'
import user from '../images/user.png'
import Aretti from '../images/Arettis.svg'
import Papa from 'papaparse';

function QueryIQ() {
  const [prompt, setPrompt] = useState('')
  const [responses, setResponses] = useState([])
  const [buffer, setBuffer] = useState(false);
  const [data,setData] = useState([])
  const [suggestions, setSuggestions] = useState([])
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);


  useEffect(() => {
    // Load and parse the CSV file
    Papa.parse('../../Files/QA.csv', {
      download: true,
      header: true,
      complete: (results) => {
        setData(results.data)
      },
      
    });
  }, []);

  //GET THE DATA FROM CSV FLE
  const fuse = new Fuse(data, {
    keys: ['Question'],
    threshold: 0.5,
    includeScore: true
  });

  const sendPrompt = async (event) => {
    event.preventDefault();
    setBuffer(true);

    setTimeout(() => {
      setBuffer(false);
      const response = findAnswer(prompt);
      setResponses((prevResponse) => [...prevResponse, {prompt, response}])
      setPrompt('');
    }, 3000);
  };

  const findAnswer = (query) => {
    const result = fuse.search(query);
    return result.length > 0 ? result[0].item.Answer : "Sorry, QueryIQ doesn't know the answer to that question. Perhaps question is not in the database";
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      if (showSuggestions && selectedIndex >= 0) {
        setPrompt(suggestions[selectedIndex]);
        setShowSuggestions(false);
      } else {
        sendPrompt(event);
      }
    } else if (event.key === 'ArrowDown') {
      setSelectedIndex((prevIndex) => (prevIndex + 1) % suggestions.length);
    } else if (event.key === 'ArrowUp') {
      setSelectedIndex((prevIndex) => (prevIndex - 1 + suggestions.length) % suggestions.length);
    }
  };


  //SHOW SUGGESTIONS
  const displaySuggestions = (e) => {
    const input = e.target.value;
    setPrompt(input);

    if (input.length > 0) {
      const questionaire = ['who', 'what', 'when', 'where', 'why', 'do', 'can', 'you', 'I', "what's", "whats", "is", "are", "a", "the", 'of'];
      const keywords = input.toLowerCase().split(' ').filter(word => !questionaire.includes(word) && word);
  
      const allQuestions = data.map(item => item.Question).filter(question => keywords.some(keyword => question.toLowerCase().includes(keyword)));

      setSuggestions(allQuestions);
      setShowSuggestions(allQuestions.length > 0);
      setSelectedIndex(-1);
    }else{
      setShowSuggestions(false);
    }
  }

  const clickedSuggestions = (suggestion) => {
    setPrompt(suggestion);  
    setShowSuggestions(false);
  }


  return (
    <>
      <div className = "full">
      <h1 style = {{fontSize: "45px", textAlign: "center"}}> QueryIQ</h1>
      <p style= {{paddingLeft: "5%", paddingRight:"5%", fontSize: "13px"}}>
        QueryIQ, a state-of-the-art Retrieval-Augmented Generation (RAG) that provides businesses with an AI-powered chatbot that understands and responds to customer inquiries with remarkable accuracy.
        QueryIQ is built with a deep understanding of your business-specific knowledge base, such as your company's unique products, services, documents and industry-specific handbook. 
        This specialization delivers responses with not only with contextual precision, but highly relevant to your business needs.
        <br></br><br></br>
        <em>Note: The back-end server has been disabled for this deployment, so some features may not be available.</em>
      </p>

     <div className = "chat">

    <div className = "chat-box">
      {responses.map((res, index) => (
        <div key = {index} className = "chat-message">
          <div className = "rightChat">
          <img className = "chaticon" src = {user} style = {{width: '3em'}}></img>
          <p className = "botText"> {res.prompt}</p>
          </div>

          <div className = "leftChat">
            <img className = "chaticon" src = {Aretti} style = {{width: '6em'}}></img>
          <p className = "botText">{res.response}</p>
          </div>
        
         </div>

      ))}


    </div>
    <div className = "input-container">
      
      <div className = "suggestionBox">
      {showSuggestions && (
        <div className = "suggestions">
          {suggestions.map((item, index) => (
            <div
              key = {index}
              className={`each-suggestion ${index === selectedIndex ? 'selected' : ''}`}
              onClick={() => clickedSuggestions(item)}
            >
            {item}
            </div>
          ))}
        </div>
      )}
     <input 
     className = "inputText"
     value = {prompt}
     onChange = {displaySuggestions}
     onKeyDown={handleKeyPress}
     >
     </input>
     </div>

     {buffer ? (
      <div className = "buffer-icon"></div>
     ) : (
      <div className = "send-icon" onClick = {sendPrompt}></div>
     )}

    </div>
    </div> 

      </div>
  
    </>
  )
}

export default QueryIQ
