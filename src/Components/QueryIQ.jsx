import React from 'react';
import { useState, useEffect } from 'react'
import './QueryChat.css'
import user from '../images/user.png'
import Aretti from '../images/Arettis.svg'
import Papa from 'papaparse';
import Fuse from 'fuse.js'


function QueryIQ() {
  const [prompt, setPrompt] = useState('')
  const [responses, setResponses] = useState([])
  const [buffer, setBuffer] = useState(false);


  //DISPLAY FAQs as suggestions
  const [suggestions, setSuggestions] = useState([])
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [data,setData] = useState([])


  useEffect(() => {
    // Load and parse the CSV file
    Papa.parse('/Files/QA.csv', {
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

    try {
      const response = await fetch ('/Querychat', {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify({ text: prompt})
});

    const data = await response.json()
    console.log('API Response:', data); // Debugging log
    setResponses((prevResponse) => [...prevResponse, {prompt, response: data.response}])
    setPrompt('');

  }catch (error){
    console.log(error)
  }finally {
    setBuffer(false)
  }
  }

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      event.preventDefault();
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
      const results = fuse.search(input).map(result => result.item.Question);
      setSuggestions(results);
      setShowSuggestions(results.length > 0);
      setSelectedIndex(-1);
    } else {
      setShowSuggestions(false);
    }
  };
  

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
      <div className = "buffer-icon">
        {/* <img src = {buffericon}></img> */}
      </div>
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
