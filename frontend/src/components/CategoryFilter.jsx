export default function CategoryFilter({ categories, value, onChange }) {
  return (
    <select className="ss-select" style={{ width: 'auto' }} value={value || ''} onChange={(e) => onChange(e.target.value)}>
      <option value="">All Categories</option>
      {categories.map((c) => (
        <option key={c.id} value={c.id}>
          {c.name}
        </option>
      ))}
    </select>
  )
}
