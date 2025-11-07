
import { Product } from '../types'

export default function ProductTable({ items }:{ items: Product[] }){
  return (
    <div className="table-wrap">
      <table className="tbl">
        <thead>
          <tr>
            <th>Image</th>
            <th>ASIN</th>
            <th>Title</th>
            <th>Price</th>
            <th>Rating</th>
            <th>Link</th>
          </tr>
        </thead>
        <tbody>
          {items.map(p => (
            <tr key={p.id}>
              <td>{p.image_url ? <img src={p.image_url} alt={p.title} /> : ''}</td>
              <td>{p.asin}</td>
              <td title={p.title}>{p.title}</td>
              <td>{p.price ?? ''}</td>
              <td>{p.rating ?? ''}</td>
              <td><a href={p.product_url} target="_blank">Open</a></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
