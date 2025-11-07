import { useEffect, useMemo, useState } from 'react'
import { fetchProducts, triggerScrape, csvUrl as buildCsvUrl } from './api'
import type { Product } from './types'
import Spinner from './components/Spinner'
import Toast from './components/Toast'
import ProductTable from './components/ProductTable'
import Controls, { ScrapeParams } from './components/Controls'

export default function App() {
  const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

  const [items, setItems] = useState<Product[]>([])
  const [loading, setLoading] = useState(false)
  const [toast, setToast] = useState<{ text: string; type: 'info' | 'error' | 'success' } | null>(null)
  const [filters, setFilters] = useState<{ q?: string; min_rating?: number; max_price?: number }>({})

  const exportHref = useMemo(
    () => buildCsvUrl({ ...filters }),
    [filters]
  )

  async function load() {
    setLoading(true)
    try {
      const res = await fetchProducts({
        ...filters,
        page: 1,
        page_size: 200,
        order_by: 'created_at',
        order: 'desc',
      })
      setItems(res.items)
    } catch (e: any) {
      setToast({ text: e?.message || 'Failed to load', type: 'error' })
    } finally {
      setLoading(false)
    }
  }

  async function doScrape(p: ScrapeParams) {
    setLoading(true)
    try {
      const body = {
        keyword: p.keyword ?? null,
        search_url: p.search_url ?? null,
        domain: p.domain ?? 'amazon.com',
        max_pages: p.max_pages ?? 1,
        delay_lo: 2.5,
        delay_hi: 5.0,
      }
      const res = await triggerScrape(body)
      setToast({ text: `Fetched ${res.fetched}. Updated ${res.inserted_or_updated}.`, type: 'success' })
      await load()
    } catch (e: any) {
      setToast({ text: e?.message || 'Scrape failed', type: 'error' })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <div className="container">
      <header className="header">
        <div>
          <h2>Product Scraper Dashboard</h2>
          <div className="sub">API: {API_BASE}</div>
        </div>
        <a href={exportHref} className="btn btn-secondary" target="_blank" rel="noreferrer">
          Export CSV
        </a>
      </header>

      <Controls
        onScrape={doScrape}
        onFilter={(f) => {
          setFilters(f)
          load()
        }}
      />

      {loading && (
        <div className="overlay">
          <Spinner />
          <div className="hint">Working… This may take 10–30s while the browser loads pages.</div>
        </div>
      )}

      <ProductTable items={items} />

      {toast && <Toast text={toast.text} type={toast.type} onClose={() => setToast(null)} />}

      <footer className="footer">Uses only public search pages</footer>
    </div>
  )
}
