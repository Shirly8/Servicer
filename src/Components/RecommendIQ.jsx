import React from 'react';
import { useState, useEffect } from 'react'
import './RecommendIQ.css'
import Papa from 'papaparse'


function RecommendIQ() {

  const [selectedOption, setSelectedOption] = useState(null);
  const [dropdownOptions, setDropdownOptions] = useState([])
  const [data,setData] = useState([])
  const [selectedDropDown, setSelectedDropDown] = useState(null)
  const [buffer, setBuffer] = useState(false)

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


    const handleDropdownChange = (e) => {
      setSelectedDropDown(e.target.value)
      

      setTimeout(() => {
        setBuffer(true)
      }, 2500)

      setBuffer(false)
    }


  return (
    <>
      <div className = "full">
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
          <h3 className = "head3"> OUR RECOMMENDATIONS FOR YOU: </h3> 
          <h4 className = "head4"> If you liked {selectedDropDown}, you might also like: </h4>

          {buffer ? (
          <div>
              {/* THIS IS WHERE WE APPLY THE MAPPING FOR THE RECOMMENDATIONS */}
              <h5 className = "head5">HERE WILL BE THE RECOMMENDATIONS</h5>
          </div>
        ) : (
          <div className = "buffers-icon">

          
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
