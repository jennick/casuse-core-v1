import React from 'react'
export default function Tile({ title, value }: { title: string, value: string | number }) {
  return (
    <div style={{padding:16, border:'1px solid #e5e7eb', borderRadius:10}}>
      <div style={{fontSize:12, color:'#6b7280'}}>{title}</div>
      <div style={{fontSize:28, fontWeight:700}}>{value}</div>
    </div>
  )
}
