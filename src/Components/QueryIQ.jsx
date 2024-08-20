import React from 'react';
import { useState } from 'react'
import './QueryChat.css'


function QueryIQ() {

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

     <input className = "inputText"></input>
     <div className = "send-icon"></div>


    </div> 

      </div>
  
    </>
  )
}

export default QueryIQ
