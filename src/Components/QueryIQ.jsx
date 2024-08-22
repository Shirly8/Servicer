import React from 'react';
import { useState } from 'react'
import './QueryChat.css'
import user from '../images/user.png'
import Aretti from '../images/Arettis.svg'

function QueryIQ() {
  const [prompt, setPrompt] = useState('')
  const [responses, setResponses] = useState([])
  const [buffer, setBuffer] = useState(false);


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
        sendPrompt(event);
      }
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
     <input 
     className = "inputText"
     value = {prompt}
     onChange = {e => setPrompt(e.target.value)}
     onKeyDown={handleKeyPress}
     >
     </input>

     {buffer ? (
      <div className = "buffer-icon">
        {/* <img src = {buffericon}></img> */}
      </div>
     ) : (
      <div className = "send-icon" onClick = {sendPrompt}></div>
     )}


    </div> 

      </div>
  
    </>
  )
}

export default QueryIQ
