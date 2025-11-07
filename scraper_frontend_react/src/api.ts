// Unified base URL env
const BASE = import.meta.env.VITE_API_BASE

// Trigger a scrape
export async function triggerScrape(body: {
  keyword?: string | null
  search_url?: string | null
  domain?: string
  max_pages?: number
  delay_lo?: number
  delay_hi?: number
}) {
  const r = await fetch(`${BASE}/scrape`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  })
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}

// Fetch products with pagination/sorting
export async function fetchProducts(params?: {
  q?: string
  min_rating?: number
  max_price?: number
  page?: number
  page_size?: number
  order_by?: "price" | "rating" | "created_at" | "updated_at" | "title"
  order?: "asc" | "desc"
}) {
  const qs = new URLSearchParams((params ?? {}) as any).toString()
  const r = await fetch(`${BASE}/products?${qs}`)
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}

// Price history
export async function getHistory(asin: string) {
  const r = await fetch(`${BASE}/history/${encodeURIComponent(asin)}`)
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}

// CSV export URL
export function csvUrl(q?: {
  q?: string
  min_rating?: number
  max_price?: number
  order_by?: "price" | "rating" | "created_at" | "updated_at" | "title"
  order?: "asc" | "desc"
}) {
  const qs = new URLSearchParams((q ?? {}) as any).toString()
  return `${BASE}/products.csv?${qs}`
}
