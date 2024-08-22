import React from 'react'
import { useState, useEffect, useRef} from 'react'
import './App.css';
import Arettis from './images/Arettis.svg'
import Servicer from './images/Servicer.svg'
import SentimentIQ from './Components/SentimentIQ';
import QueryIQ from './Components/QueryIQ';
import RecommendIQ from './Components/RecommendIQ';


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
    <h1> Toronto's 3 Michelin Star</h1>

    </div>
    </div>
    
  )
}

export default App
