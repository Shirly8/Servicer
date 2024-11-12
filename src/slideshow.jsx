import React from 'react'
import { useState, useEffect, useRef} from 'react'
import './App.css';
import {useSwipeable } from 'react-swipeable';

const SlideComponent = () => {
  const handlers = useSwipeable({
    onSwipedLeft: () => console.log("swipedleft"),
    onSwipedRight: () => console.log("SwipedRight")
  });

  const [currentSlide, setCurrentSlide] = useState(0)
  const slideCount = 3

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentSlide((prevSlide) => (prevSlide + 1) % slideCount);
    }, 10000);

    return () => clearInterval(interval);
  }, [slideCount]);


  return (

    <div {...handlers} className = "slide">
    {currentSlide === 0 && (
    <div>
    <div className= 'thumbnails'></div>
    <div className = "thirds">
    <h6>OUR SECRET INGREDIENT...</h6>
    <p className = "p2"> Our chef’s passion for cooking. That’s it. 
      Our extensive menu, featuring 85 dishes and 25 drinks, 
      was curated by our initial team of six chefs, including our owner, 
      the renowned Chef Shirley Huang. Our commitment to perfection 
      and our customers is what makes Aretti truly special.</p>
    </div>
    </div>
    )}


    {currentSlide === 1 && (
   <div>
   <div className= 'thumbnails2'></div>
   <div className = "thirds">
    <h6>OUR ONE MISSION...</h6>
   <p className = "p2"> 
    For you to have an unparalleled experience. That's it.
    Whether it's a celebration, a get-together, a special occasion, or 
    just an ordinary day, we are dedicated to turning every moment into a cherished memory.
    We focus on bringing our restaurants interior to life with lavish decorations, exceptional services, 
    and our admirable French-Italian dishes.
   </p>
   </div>
   </div>
    )}


  {currentSlide === 2 && (
    <div>
    <div className= 'thumbnails3'></div>
    <div className = "thirds">
      <h6>AT THE END OF THE DAY...</h6>
    <p className = "p2"> 
      We don't want our meals to be something that just fills your stomach. 
      We want to make a lasting impression, to etch our name in your memory.
      We want you to leave with a piece of us - even as simple as a memory of our restaurant, our food and our services.
    </p>
    </div>
    </div>
    )}

    </div>


  );
};

export default SlideComponent;