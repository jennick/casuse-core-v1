import React, { useEffect, useState } from 'react'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'

export default function App() {
  const [token, setToken] = useState<string | null>(null)

  useEffect(() => {
    const t = sessionStorage.getItem('access_token')
    if (t) setToken(t)
  }, [])

  if (!token) return <Login onAuthenticated={(t) => { sessionStorage.setItem('access_token', t); setToken(t); }} />
  return <Dashboard token={token} onLogout={() => { sessionStorage.clear(); location.href = '/' }} />
}
