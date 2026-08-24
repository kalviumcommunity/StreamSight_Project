import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function SearchBar({ initialValue = '', compact = false }) {
  const [value, setValue] = useState(initialValue)
  const navigate = useNavigate()

  function handleSubmit(e) {
    e.preventDefault()
    const q = value.trim()
    if (q) navigate(`/search?q=${encodeURIComponent(q)}`)
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        className="ss-search-input"
        type="search"
        placeholder="Search titles..."
        value={value}
        onChange={(e) => setValue(e.target.value)}
        style={compact ? { minWidth: 160 } : undefined}
      />
    </form>
  )
}
