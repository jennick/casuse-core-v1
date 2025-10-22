import React, { useEffect, useState } from 'react'
import { pkcePair } from '../auth/pkce'
import { authorize, exchangeCode } from '../auth/oidc'

type Props = { onAuthenticated: (token: string) => void }

export default function Login({ onAuthenticated }: Props) {
  const [email, setEmail] = useState('admin.one@casuse.local')
  const [password, setPassword] = useState('Casuse!2025')

  useEffect(() => {
    const url = new URL(window.location.href)
    const code = url.searchParams.get('code')
    const v = sessionStorage.getItem('code_verifier')
    if (code && v) {
      exchangeCode('core-fe', code, v, '/').then(tok => {
        onAuthenticated(tok.access_token)
      }).catch(() => alert('Tokenruil mislukt'))
    }
  }, [])

  async function doLogin(e: React.FormEvent) {
    e.preventDefault()
    const form = new URLSearchParams({ email, password })
    const ok = await fetch('/auth/login', { method: 'POST', body: form })
    if (!ok.ok) { alert('Login mislukt'); return }
    const { verifier, challenge } = await pkcePair();
    sessionStorage.setItem('code_verifier', verifier)
    const state = crypto.randomUUID()
    await authorize('core-fe', '/', challenge, state)
  }

  return (
    <div style={{maxWidth: 380, margin: '10vh auto', padding: 24, border: '1px solid #cbd5e1', borderRadius: 8}}>
      <h1>Casuse Core Login</h1>
      <form onSubmit={doLogin}>
        <label>Email<br/><input value={email} onChange={e=>setEmail(e.target.value)} required/></label><br/>
        <label>Wachtwoord<br/><input type="password" value={password} onChange={e=>setPassword(e.target.value)} required/></label><br/>
        <button type="submit" style={{marginTop:12}}>Inloggen</button>
      </form>
    </div>
  )
}
