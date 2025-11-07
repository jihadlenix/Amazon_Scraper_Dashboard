
import { useState } from 'react'

export type ScrapeParams = {
  keyword?: string | null
  search_url?: string | null
  domain?: string
  max_pages?: number
}

export default function Controls({ onScrape, onFilter }:{
  onScrape: (p:ScrapeParams)=>void,
  onFilter: (f:{q?:string, min_rating?:number, max_price?:number})=>void
}){
  const [keyword, setKeyword] = useState('wireless headphones')
  const [domain, setDomain] = useState('amazon.com')
  const [pages, setPages] = useState(1)
  const [searchUrl, setSearchUrl] = useState('')

  const [q, setQ] = useState('')
  const [minRating, setMinRating] = useState<string>('')
  const [maxPrice, setMaxPrice] = useState<string>('')

  return (
    <div className="controls">
      <div className="card">
        <h3>Scrape</h3>
        <div className="row">
          <input value={keyword} onChange={e=>setKeyword(e.target.value)} placeholder="Keyword"/>
          <select value={domain} onChange={e=>setDomain(e.target.value)}>
            <option>amazon.com</option>
            <option>amazon.ae</option>
            <option>amazon.co.uk</option>
          </select>
          <input type="number" min={1} max={10} value={pages} onChange={e=>setPages(parseInt(e.target.value||'1'))} />
          <button onClick={()=>onScrape({ keyword, domain, max_pages: pages })}>Scrape Keyword</button>
        </div>
        <div className="row">
          <input value={searchUrl} onChange={e=>setSearchUrl(e.target.value)} placeholder="or paste full search URL"/>
          <button onClick={()=>onScrape({ search_url: searchUrl || null, max_pages: pages })}>Scrape URL</button>
        </div>
      </div>

      <div className="card">
        <h3>Filters</h3>
        <div className="row">
          <input value={q} onChange={e=>setQ(e.target.value)} placeholder="Name contains..."/>
          <input value={minRating} onChange={e=>setMinRating(e.target.value)} placeholder="Min rating e.g. 4.3"/>
          <input value={maxPrice} onChange={e=>setMaxPrice(e.target.value)} placeholder="Max price e.g. 100"/>
          <button onClick={()=>onFilter({
            q: q || undefined,
            min_rating: minRating ? parseFloat(minRating) : undefined,
            max_price: maxPrice ? parseFloat(maxPrice) : undefined
          })}>Apply</button>
        </div>
      </div>
    </div>
  )
}
