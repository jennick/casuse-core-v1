import React, { useEffect, useState } from 'react'
import Tile from '../components/Tile'
import { apiGet } from '../auth/api'

type Props = { token: string, onLogout: ()=>void }
export default function Dashboard({ token, onLogout }: Props) {
  const [data, setData] = useState<any>(null)
  const [err, setErr] = useState<string | null>(null)

  useEffect(() => {
    apiGet<any>('/api/tiles', token).then(setData).catch(e => setErr(String(e)))
  }, [token])

  return (
    <div style={{maxWidth:1000, margin:'5vh auto', padding:24}}>
      <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
        <h1>Casuse Core Dashboard</h1>
        <button onClick={onLogout}>Logout</button>
      </div>
      {err && <div style={{color:'#dc2626'}}>Kon tegels niet laden: {err}</div>}
      {data && (
        <div>
          <div style={{marginBottom:12, color:'#6b7280'}}>Welkom, {data.user}</div>
          <div style={{display:'grid', gridTemplateColumns:'repeat(3, 1fr)', gap:12}}>
            <Tile title="Modules up" value={data.kpis.modules_up} />
            <Tile title="Alerts" value={data.kpis.alerts} />
            <Tile title="Latency p95 (ms)" value={data.kpis.latency_ms_p95} />
          </div>
        </div>
      )}
    </div>
  )
}
