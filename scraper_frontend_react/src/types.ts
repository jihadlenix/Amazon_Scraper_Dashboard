// src/types.ts
export type Product = {
  id: number
  asin: string
  title: string
  product_url: string
  image_url?: string
  price?: number
  price_raw?: string
  currency?: string
  rating?: number
  rating_count?: number
  created_at: string
  updated_at: string
}

export type ProductsResponse = {
  page: number
  page_size: number
  total: number
  items: Product[]
}

export type PricePoint = {
  price?: number
  price_raw?: string
  currency?: string
  seen_at: string
}

export type HistoryResponse = {
  asin: string
  count: number
  points: PricePoint[]
}
