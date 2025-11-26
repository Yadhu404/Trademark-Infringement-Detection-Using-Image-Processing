import { useState, useRef } from 'react'
import './App.css'
import BrandSearch from './Component/BrandSearch.jsx'
import ActionButton from './Component/ActionButton.jsx'
import LoadingState from './Component/LoadingState.jsx'
import Recentcheck from './Component/Recentcheck.jsx'
import DropZone from './Component/DropZone.jsx'
import Theoutput from './Component/Theoutput.jsx'
import Erroroccur from './Component/Erroroccur.jsx'
import axios from 'axios'

function App() {
  const [Uploadfile, setUploadedFile] = useState(null)
  const [Inputstate, setInputstate] = useState('')
  const [upsuccess, upsetsuccess] = useState(false)
  const [dropsuccess, dropsetsuccess] = useState(false)
  const [brandname, setbrandname] = useState(null)
  const [verdict, setverdict] = useState(null)
  const [similarity, setsimilarity] = useState(null)
  const [loading, setloading] = useState(false)
  const [error, setError] = useState(null)
  const fileref = useRef(null)
  const tryagain=()=>{
      setError(null);
      sendtobackend();
  }
  const handleupload = () => {
    fileref.current.click()
  }

  const sendtobackend = async () => {
    if (!Uploadfile) return
    setloading(true)
    setError(null) // Clear any previous errors
    
    try {
      const formdata = new FormData()
      formdata.append('file', Uploadfile)
      formdata.append('searchinput', Inputstate)
      
      const res = await axios.post('http://127.0.0.1:8080/upload', formdata)
      
      if (res.data && !res.data.error) {
        
            const data = res.data; 

            if ('check' in data) {
               
                console.log("Text check FAILED (check property is present).");
                
                if (data.check == false) {
                     alert("send data to admin")
                }
            }else{
                  setbrandname(res.data.brand)
                   setverdict(res.data.VERDICT)
                  setsimilarity(res.data.Similarity)
            }
          
      } else if (res.data && res.data.error) {
        // Backend returned an error message
        setError(res.data.error)
        setbrandname(null)
        setverdict(null)
        setsimilarity(null)
      } else {
        setError('Unexpected response from server')
        console.log(res)
      }
    } catch (err) {
      console.log('Error uploading file:', err)
      
      // Check if it's a response error (5xx, 4xx)
      if (err.response) {
        // Server responded with an error
        const errorMsg = err.response.data?.error || 'Server error occurred'
        setError(errorMsg)
      } else if (err.request) {
        // Request was made but no response received
        setError('No response from server. Please check your connection.')
      } else {
        // Something else went wrong
        setError('An unexpected error occurred')
      }
      
      // Reset states
      setbrandname(null)
      setverdict(null)
      setsimilarity(null)
    } finally {
      setloading(false)
    }
  }

  const handleChange = (e) => {
    const file = e.target.files[0]
    if (file && file.type.startsWith('image/')) {
      upsetsuccess(true)
      setUploadedFile(file)
      setError(null) // Clear error when new file is selected
    } else if (file) {
      alert('Please select an image file.')
    }
  }

  const handleRemove = () => {
    setUploadedFile(null)
    if (fileref.current) fileref.current.value = ''
    upsetsuccess(false)
    setbrandname(null)
    setverdict(null)
    setsimilarity(null)
    setError(null)
  }

  return (
    <div className="w-full h-full bg-white flex flex-col rounded-2xl shadow-2xl overflow-hidden">
      <div className="bg-gradient-to-br from-[#667eea] to-[#764ba2] text-white text-center p-3 sticky top-0 z-10">
        <h1 className="text-2xl font-semibold">🛡️ Trademark Detector</h1>
        <p className="text-sm opacity-90">Verify logos and brand authenticity</p>
      </div>

      <div className="flex-1 p-3 overflow-hidden">
        <BrandSearch Inputstate={Inputstate} setInputstate={setInputstate} />
        <ActionButton 
          handleupload={handleupload} 
          Uploadfile={Uploadfile} 
          dropsuccess={dropsuccess} 
          handleRemove={handleRemove} 
        />
        <DropZone 
          dropsetsuccess={dropsetsuccess} 
          setUploadedFile={setUploadedFile} 
          setbrandname={setbrandname} 
          setverdict={setverdict} 
          setsimilarity={setsimilarity} 
        />
        
        {(upsuccess || dropsuccess) && (
          <button
            className="block w-full mx-auto py-3 text-xl font-bold text-white bg-blue-500 rounded-lg shadow-lg hover:bg-blue-600 transition-all duration-200 cursor-pointer"
            onClick={sendtobackend}
          >
            Verify
          </button>
        )}

        {loading ? (
          <LoadingState />
        ) : error ? (
            <Erroroccur tryagain={tryagain} error={error}/>
        ) : brandname && verdict && similarity ? (
          <Theoutput brandname={brandname} verdict={verdict} similarity={similarity} />
        ) : (
          <Recentcheck />
        )}
      </div>

      <input
        type="file"
        onChange={handleChange}
        ref={fileref}
        accept="image/*"
        className="hidden"
      />
    </div>
  )
}

export default App