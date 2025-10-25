import React from 'react'
import { createRoot } from 'react-dom/client'

const API = import.meta.env.VITE_API_BASE

function App(){
  const [resp, setResp] = React.useState(null)
  const [secure, setSecure] = React.useState(null)
  const token = localStorage.getItem('token')||''
  return (
    <div style={{fontFamily:'system-ui', padding:'2rem'}}>
      <h1>Website Module API UI</h1>
      <p>API base: {API}</p>
      <p>
        <button onClick={async()=>{
          const r = await fetch(`${API}/api/ping`); setResp(await r.json());
        }}>Ping</button>
        {' '}
        <button onClick={async()=>{
          const r = await fetch(`${API}/api/secure`,{headers:{Authorization:`Bearer ${token}`}}); setSecure(await r.json());
        }}>Secure Ping (JWT)</button>
      </p>
      <pre>{JSON.stringify(resp,null,2)}</pre>
      <pre>{JSON.stringify(secure,null,2)}</pre>
      <p><a href="http://localhost:10300/home">Terug naar Home</a></p>
    </div>
  )
}
createRoot(document.getElementById('root')).render(<App/>)
