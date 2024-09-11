import React from 'react'
import { useState, useEffect, useRef} from 'react'
import './App.css';
import Arettis from './images/Arettis.svg'
import Servicer from './images/Servicer.svg'
import fivestar from './images/5star.png'
import fourstar from './images/4.5star.png'

import SentimentIQ from './Components/SentimentIQ';
import QueryIQ from './Components/QueryIQ';
import RecommendIQ from './Components/RecommendIQ';

import PdfViewer from './PDFViewer'


function App() {

  const [clickedComponent, setClickedComponent] = useState(null);
  const tabsRef = useRef(null);


  //Scroll-To the Tab feature
  useEffect(() => {
    if (clickedComponent !=null && tabsRef.current) {
      tabsRef.current.scrollIntoView({behavior: 'smooth'})
    }
  }, [clickedComponent])


  //Different components of the tab
  const renderComponent = () => {
    if (clickedComponent === null) {
      return null;
    }

    switch (clickedComponent) {
      case 'SentimentIQ':
        return <SentimentIQ />;
      case 'QueryIQ':
        return <QueryIQ/>;
      case 'RecommendIQ':
        return <RecommendIQ/>
      default: 
        return null;
    }
  }

  //Handle Toggle Component Visibility:
  const handleTabClick = (component) => {
    setClickedComponent(prevComponent => prevComponent === component ? null : component);
  };

  return (
    <div className = 'main'>

      <header>
        <img src = {Arettis} className = "logo left"></img>
        <img src = {Servicer} style = {{height: "7em"}}></img>
       
       <div className = "navRight">
        <h2 className = "nav">Menu</h2>
        <h2 className = "nav">Our Location </h2>
        <h2 className = "nav">About Us</h2>
      </div> 
      </header>

    <div className = "thumbnail">  
       <h1 className = "thumbnailfont">Elevate your Service Experience with AI</h1>
       <button className = "buttonthumnail">Learn More</button>
    </div>


    <div className = "components">
      <nav className='tabs' ref = {tabsRef}>
        <button className = 'tabbutton' onClick = {()=> handleTabClick('SentimentIQ')}>SentimentIQ</button>
        <button className = 'tabbutton' onClick = {()=> handleTabClick('QueryIQ')}>QueryIQ</button>
        <button className = 'tabbutton' onClick = {()=> handleTabClick('RecommendIQ')}>RecommendIQ</button>
      </nav>
    </div>

    <div className = "rendered">
        {renderComponent()}
    </div>



    <div className = "centered">
    <h1> Toronto's First THREE Michelin Star</h1>

    <div className = "three">
      <div className = "image1">
        <h4>Menu</h4></div>
      
      <div className = "image2">
        <h4>FAQ</h4>
        </div>
      
      <div className = "image3">
        <h4>About Us</h4>
      </div>
    </div>


    <div className = "centered">
    <h1> What our CRITICS say...</h1>

    <div className = "three2">
      <div className = "critics">
        <h5>Gordan Ramsay</h5>
        <p1>Aretti is a culinary masterpiece with impeccable service and a menu that is a symphony of flavors. 
          The Polpo alla Griglia and Osso Buco were standout dishes, 
          and the Chocolate Fondant was the perfect ending to an unforgettable meal. 
          Every detail, from presentation to ambiance, is designed to create a memorable evening.
          <img className = "reviewstar" src = {fivestar}></img>
        </p1>
      </div>

      <div className = "critics">
        <h5>Anthony Bourdain</h5>
        <p1>Dining at Aretti is like stepping into a world of culinary artistry, 
          with luxurious ambiance and precision in every dish. 
          The Foie Gras Torchon and Tagliatelle al Tartufo were divine, 
          and the Pistachio Gelato was a delightful finish. 
          Aretti sets the standard for fine dining in Toronto.
          <img className = "reviewstar" src = {fivestar}></img>
        </p1>
      </div>

      <div className = "critics">
        <h5>Ruth Reichi</h5>
        <p1>Aretti offers a refined atmosphere and exceptional service, 
          with standout dishes like Carpaccio di Manzo and Seafood Risotto. 
          While the Lobster Roll Sliders could have been more innovative, 
          the overall experience was exceptional, making Aretti one of the finest top-tier dining destination in Toronto.
          <img className = "reviewstar" src = {fourstar}></img>
        </p1>
      </div>
    </div>    
    </div>

    </div>
    <div classname = "slideshow">
    <div className= 'thumbnails'></div>
    <div className = "thirds">
    <h6>One Secret Ingredients...</h6>
    <p2>Our chef’s passion for cooking. That’s it. 
      Our extensive menu, featuring 85 dishes and 25 drinks, 
      was curated by our initial team of six chefs, including our owner, 
      the renowned Chef Shirley Huang. Our commitment to perfection 
      and our customers is what makes Aretti truly special.</p2>
    </div>
    </div>

    <div className = "thirds2">
      <div className = "end"></div>
      <div className = "end2">
        <h1>WE'RE DYING TO HAVE YOU HERE!</h1>

      <div className = "info">
        <p>Address: 123 Random Road, A1B 3C4, Toronto, ON Canada</p>
        <p>Phone Number: +1 (123) - 456 - 7890</p>
        <p>Email: Reservations@Aretti.com</p>
        <p>Instagram: @ArettiDining</p>
        <p>Facebook: @ArettiDining</p>
        <p>Website: ArettiDining.com</p>
      </div>

      </div>



    </div>

    </div>
    
  )
}

export default App
