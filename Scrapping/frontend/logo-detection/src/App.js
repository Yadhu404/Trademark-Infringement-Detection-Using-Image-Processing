import logo from './logo.svg';
import './App.css';
import { useState } from 'react';

function App() {
  const[url, setUrl] = useState("");
  const[file, setFile] = useState(null);
  const[results, setResults] = useState([]);

  const handleScrape = async () => {
    await fetch("http://localhost:5000/scrape", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
    alert("Scraping complete!");
  };

  const handleCompare = async () => {
    const formData = new FormData();
    formData.append("image", file);

    const res = await fetch("http://localhost:5000/compare", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    setResults(data.results);
  };
  const something = function(){
    console.log(url);
  }

  return (
    <div className="App">
      <div className='platform-select'>
        <select onChange={(e) => setUrl(e.target.value)}>
          <option value={""}>Select Platform</option>
          <option value={"https://play.google.com/"}>playstore</option>
          <option value={"https://www.graphicdesigneire.ie/graphic-design-blog/top-101-most-famous-logos-of-all-time-ranked"}>graphicdesigneire</option>
        </select>
        <input type='button' value="SCRAP" onClick={handleScrape}/>
      </div>
      <div className='test-image'>
        <input type='file' onChange={(e) => setFile(e.target.files[0])}/>
        <input type='button' value='COMPARE' onClick={handleCompare}/>
      </div>

      <div className='result'>
        <h3>Top Matches</h3>
      <ul>
        {results.map((r, i) => (
          <li key={i}>
            <img src={"scraped_images/"+r.filename}/> — Similarity: {r.similarity} {r.is_similar ? "Possible Match" : ""}
          </li>
        ))}
      </ul>
      </div>
    </div>
  );
}

export default App;
