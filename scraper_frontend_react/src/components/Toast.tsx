
import { useEffect } from 'react'

export default function Toast({ text, type='info', onClose }:{ text:string, type?:'info'|'error'|'success', onClose:()=>void }){
  useEffect(() => {
    const t = setTimeout(onClose, 3500)
    return () => clearTimeout(t)
  }, [onClose])

  return (
    <div className={`toast ${type}`} onClick={onClose}>
      {text}
    </div>
  )
}
