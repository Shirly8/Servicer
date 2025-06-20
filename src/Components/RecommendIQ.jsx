import React from 'react';
import { useState, useEffect } from 'react'
import './RecommendIQ.css'
import Papa from 'papaparse'

const categoryImages = {
  Appetizers: "option1",
  Salads: "option2",
  Entrees: "option3",
  Seafood: "option4",
  Desserts: "option5",
  Cocktails: "option6",
  Wine: "option7",
  Beer: "option8",
};



function RecommendIQ() {

  const [selectedOption, setSelectedOption] = useState(null);
  const [dropdownOptions, setDropdownOptions] = useState([]);
  const [data, setData] = useState([]);
  const [selectedDropDown, setSelectedDropDown] = useState(""); // initialize as empty string
  const [recommendations, setRecommendations] = useState([]);
  const [buffer, setBuffer] = useState(false);

  useEffect(() => {
    Papa.parse('/Files/Menu.csv', {
      download: true,
      header: true,
      complete: (results) => {
        setData(results.data)
      },
    })
  }, [])

    //Fetch the dropdown options given the selectedOption
    const fetchMenuOptions = (choice) => {
      setSelectedOption(choice)
      const optionNames = data.filter(row => row.Category === choice).map(row => row.Item_Name)
      console.log(optionNames)    //Log all the rows with the data
      setDropdownOptions(optionNames)    //Log all the rows with the data

    }


    //When users select item:
    const fetchRecommendations = async (itemName) => {
      setBuffer(true); // Activate buffer immediately
      try {
        const response = await fetch('/recommenditems', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ item_name: itemName }),
        });
        const recData = await response.json();
        if (recData.error) {
          console.log(recData.error);
          setRecommendations([]);
        } else {
          setRecommendations(recData);
        }
        // Keep the buffer active for 4 seconds
        setTimeout(() => {
          setBuffer(false);
        }, 4000);
      } catch (error) {
        console.log('Error fetching recommendations:', error);
        setBuffer(false);
      }
    };
    
    
    

    const handleDropdownChange = (e) => {
      const value = e.target.value;
      setSelectedDropDown(value);
      fetchRecommendations(value);
    };


    //Stars:
    const renderStars = (rating) => {
      const fullStars = Math.floor(rating);
      return '★'.repeat(fullStars) + '☆'.repeat(5 - fullStars);
    };




  return (
    <>
      <div className = "fulll">
        <h1 style = {{fontSize: "45px", textAlign: "center"}}> RecommendIQ</h1>
        <p style= {{paddingLeft: "5%", paddingRight:"5%", fontSize: "13px"}}>
        RecommendIQ - Recommendation Engine - Coming Soon - 
        </p>
        
        <div className = "recommendBox">
        <h2>Choose your type of recommendation: </h2>
        
        <div className = "recommendOptions">
          <div className = "option1" data-text = "Appetizers" onClick = {() => fetchMenuOptions("Appetizers")}></div>
          <div className = "option2" data-text = "Salads" onClick = {() => fetchMenuOptions("Salads")}></div>
          <div className = "option3" data-text = "Entrees" onClick = {() => fetchMenuOptions("Entrees")}></div>
          <div className = "option4" data-text = "Seafood" onClick = {() => fetchMenuOptions("Seafood")}></div>
          <div className = "option5" data-text = "Desserts" onClick = {() => fetchMenuOptions("Desserts")}></div>
          <div className = "option6" data-text = "Cocktails" onClick = {() => fetchMenuOptions("Cocktails")}></div>
          <div className = "option7" data-text = "Wine" onClick = {() => fetchMenuOptions("Wine")}></div>
          <div className = "option8" data-text = "Beer" onClick = {() => fetchMenuOptions("Beer")}></div>
        </div>

        {selectedOption && 
        <div>
          <h2> Choose your {selectedOption} </h2>

            <select className = "dropdown" value = {selectedDropDown} onChange = {handleDropdownChange}>
              {dropdownOptions.map((option, index) => (
                <option key={index} value={option}>{option}</option>
              ))}
            </select>
          </div>
        }

        {selectedDropDown &&
        <div>
      
          {buffer ? (
            <div>
    <h3 className="head3"> OUR RECOMMENDATIONS FOR YOU: </h3> 
    <div className="buffers-icon">
  </div>
  </div>
) : (
  <div>
    <h3 className="head3"> OUR RECOMMENDATIONS FOR YOU: </h3> 
    <h4 className="head4"> If you liked {selectedDropDown}, you might also like: </h4>
    <div className="recommendations-container">
      {Array.isArray(recommendations) && recommendations.map((item, index) => (

        <div key={index} className="recommendation-card">
        <h3 className = "recommendheaders">{item.Item_Name}</h3>
        <div className={`category-image ${categoryImages[item.Category] || 'default'}`}></div>
        <p className = "price">Price: ${item.Price}</p>
        {renderStars(item.Average_Rating)}
      </div>



      ))}
    </div>
  </div>
)}
      </div>
      }      
    </div>
  </div>
</>
)
}
export default RecommendIQ;
