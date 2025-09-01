import logo from './logo.svg';
import './App.css';
import { useRef, useState } from 'react';

function App() {
  let noImageState = "No Image Found";
  let noLogoSelectedState = "Upload Logo";
  let logoSelectedState = "✔";

  const[url, setUrl] = useState("");
  const[file, setFile] = useState(null);
  const[results, setResults] = useState([]);

  const[noImage, setImageMessage] = useState(noImageState);
  const[uploadLogo, setUploadState] = useState(noLogoSelectedState);

  const setClearDiv = useRef(null);

  const RemoveResultDiv = () => {
    if(setClearDiv.current && setClearDiv.current.firstChild)
      {
        setClearDiv.current.removeChild(setClearDiv.current.firstChild);
      }
  }
  const handleScrape = async () => {
    if(url == ""){ setImageMessage("Insert Logo!"); return;}
    
    // RemoveResultDiv();

    setImageMessage("Searching...");
    await fetch("http://localhost:5000/scrape", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      console.log("DONE SCRAPPING...");
    handleCompare();
  };

  const handleCompare = async () => {
    setImageMessage("Analyzing...");
    console.log("START COMAPRING...");
    const formData = new FormData();
    formData.append("image", file);

    try
    {
      const res = await fetch("http://localhost:5000/compare", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      if(data.results)
      {
        setResults(data.results);
      }
      else
      {
        console.log("|...RESULTS IF EMPTY...|");
      }
      setImageMessage("");
    }
    catch(e)
    {
      setImageMessage("Cannot fetch logo. Please check your network connection");
    }

  };



  return (
    <div className="App">
      <div className='container'>
        <div className='main'>
          <h2><b>Trademark Infringement System</b></h2>
          <p>Choose any logo to detect *</p>

          <div className='test-image'>
            <label htmlFor="fileChoose">{uploadLogo}</label>
            <input type='file' id="fileChoose" onChange={(e) => {setFile(e.target.files[0]); setUploadState(logoSelectedState); console.log(e.target.files[0].name);}}/>
          </div>
          <div className='line'></div>
          <p>You can select any platforms for<br/><b>Platform Specific Search.</b><br/>Verify your custom logo doesn't exist.</p>
          
          <div className='platform-select'>
            <select onChange={(e) => setUrl(e.target.value)}>
              <option value={""}>Select Platform</option>
              <option value={"play.google"}>playstore</option>
              {/* <option value={"https://www.graphicdesigneire.ie/graphic-design-blog/top-101-most-famous-logos-of-all-time-ranked"}>graphicdesigneire</option> */}
              <option value={"amazon"}>Amazon</option>
              <option value={"flipkart"}>FlipKart</option>
              <option value={"walmart"}>Walmart</option>
              <option value={"alibaba"}>Alibaba</option>
              <option value={"ebay"}>eBay</option>
            </select>
          </div>
        </div>

        <div className='result'>
          <div className='find-button'>
            <input type='button' value='FIND' onClick={handleScrape}/>
          </div>

          <div className='img-compare'>
            <div className='ip-image'>
              {file &&
                <img src={URL.createObjectURL(file)}/>
              }
              {!file &&
                <p>No Image Selected</p>
              }
            </div>

            <div className='target' ref={setClearDiv}>
              <p>{noImage}</p>
              {results.map((r, i) => (
                <div className='target-logo'>
                  <div className='logo'>
                    <img src={`http://localhost:5000/scraped_images/${r.filename}`}  alt='logo'/>
                  </div>

                  <div className='detail'>
                    <p>{r.similarity * 100 + "%"} {r.is_similar ? " ⚠️Possibly Exist" : "Matching"}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
