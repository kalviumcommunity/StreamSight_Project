import { useEffect, useRef, useState } from 'react'
import * as videoService from '../services/videoService'
import * as analyticsService from '../services/analyticsService'
import DataTable from '../components/DataTable'
import Modal from '../components/Modal'
import { PageLoading } from '../components/Loading'
import { formatDuration, formatDate } from '../utils/format'
import { useToast } from '../context/ToastContext'
import { apiErrorMessage } from '../services/api'

const EMPTY_FORM = {
  title: '', description: '', category_id: '', duration: '', thumbnail_url: '', video_url: '', release_date: '',
}

export default function ContentManagement() {
  const [videos, setVideos] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState(null) // null = closed, {} = new, {...video} = edit
  const [form, setForm] = useState(EMPTY_FORM)
  const [saving, setSaving] = useState(false)
  const [newCategoryName, setNewCategoryName] = useState('')
  const [importReport, setImportReport] = useState(null)
  const [importing, setImporting] = useState(false)
  const fileInputRef = useRef(null)
  const { notify } = useToast()

  function loadVideos() {
    setLoading(true)
    videoService.listVideos({ per_page: 100, sort: 'newest' }).then((data) => setVideos(data.items)).finally(() => setLoading(false))
  }

  useEffect(() => {
    loadVideos()
    videoService.listCategories().then(setCategories)
  }, [])

  function openCreate() {
    setForm(EMPTY_FORM)
    setEditing({})
  }

  function openEdit(video) {
    setForm({
      title: video.title,
      description: video.description || '',
      category_id: video.category_id,
      duration: video.duration,
      thumbnail_url: video.thumbnail_url || '',
      video_url: video.video_url || '',
      release_date: video.release_date || '',
    })
    setEditing(video)
  }

  async function handleSave(e) {
    e.preventDefault()
    setSaving(true)
    try {
      const payload = {
        ...form,
        category_id: Number(form.category_id),
        duration: Number(form.duration),
        release_date: form.release_date || undefined,
      }
      if (editing?.id) {
        await videoService.updateVideo(editing.id, payload)
        notify('Video updated')
      } else {
        await videoService.createVideo(payload)
        notify('Video created')
      }
      setEditing(null)
      loadVideos()
    } catch (err) {
      notify(apiErrorMessage(err), 'error')
    } finally {
      setSaving(false)
    }
  }

  async function handleDeactivate(video) {
    if (!window.confirm(`Deactivate "${video.title}"? It will no longer be visible to viewers.`)) return
    try {
      await videoService.deactivateVideo(video.id)
      notify('Video deactivated')
      loadVideos()
    } catch (err) {
      notify(apiErrorMessage(err), 'error')
    }
  }

  async function handleAddCategory(e) {
    e.preventDefault()
    if (!newCategoryName.trim()) return
    try {
      await videoService.createCategory({ name: newCategoryName.trim() })
      setNewCategoryName('')
      videoService.listCategories().then(setCategories)
      notify('Category added')
    } catch (err) {
      notify(apiErrorMessage(err), 'error')
    }
  }

  async function handleImport(e) {
    const file = e.target.files?.[0]
    if (!file) return
    setImporting(true)
    setImportReport(null)
    try {
      const report = await analyticsService.importEngagementFile(file)
      setImportReport(report)
      notify(`Imported ${report.valid_records} of ${report.total_records} records`)
    } catch (err) {
      notify(apiErrorMessage(err), 'error')
    } finally {
      setImporting(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  return (
    <div>
      <div className="ss-section-title">
        Content Management
        <button className="ss-btn ss-btn-primary" onClick={openCreate}>+ Add Video</button>
      </div>

      {loading ? (
        <PageLoading />
      ) : (
        <div className="ss-card" style={{ marginBottom: '1.5rem' }}>
          <DataTable
            columns={[
              { key: 'title', label: 'Title' },
              { key: 'category', label: 'Category', render: (r) => r.category?.name },
              { key: 'duration', label: 'Duration', render: (r) => formatDuration(r.duration) },
              { key: 'views', label: 'Views' },
              { key: 'release_date', label: 'Released', render: (r) => formatDate(r.release_date) },
              { key: 'is_active', label: 'Status', render: (r) => (
                <span className={`ss-badge ${r.is_active ? 'ss-badge-positive' : 'ss-badge-neutral'}`}>
                  {r.is_active ? 'Active' : 'Inactive'}
                </span>
              ) },
              { key: 'actions', label: '', sortable: false, render: (r) => (
                <div style={{ display: 'flex', gap: 6 }}>
                  <button className="ss-btn ss-btn-outline ss-btn-sm" onClick={() => openEdit(r)}>Edit</button>
                  {r.is_active && (
                    <button className="ss-btn ss-btn-danger ss-btn-sm" onClick={() => handleDeactivate(r)}>Deactivate</button>
                  )}
                </div>
              ) },
            ]}
            rows={videos}
            pageSize={10}
          />
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }}>
        <div className="ss-card">
          <div className="ss-section-title">Categories</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: '1rem' }}>
            {categories.map((c) => (
              <span key={c.id} className="ss-badge ss-badge-neutral">{c.name}</span>
            ))}
          </div>
          <form onSubmit={handleAddCategory} style={{ display: 'flex', gap: 8 }}>
            <input
              className="ss-input"
              placeholder="New category name"
              value={newCategoryName}
              onChange={(e) => setNewCategoryName(e.target.value)}
            />
            <button className="ss-btn ss-btn-primary ss-btn-sm" type="submit">Add</button>
          </form>
        </div>

        <div className="ss-card">
          <div className="ss-section-title">Import Engagement Dataset</div>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>
            Upload a CSV, JSON, or Excel file with columns: user_id, video_id, watch_duration, completion_rate
            (optional: pause_count, replay_count, seek_count).
          </p>
          <input ref={fileInputRef} type="file" accept=".csv,.json,.xlsx,.xls" onChange={handleImport} disabled={importing} />
          {importing && <p style={{ fontSize: '0.82rem', marginTop: 8 }}>Importing...</p>}
          {importReport && (
            <div style={{ marginTop: '1rem', fontSize: '0.82rem' }}>
              <div>Total: {importReport.total_records} · Valid: {importReport.valid_records} · Invalid: {importReport.invalid_records} · Duplicates: {importReport.duplicates}</div>
              {importReport.validation_failures?.length > 0 && (
                <details style={{ marginTop: 8 }}>
                  <summary style={{ cursor: 'pointer', color: 'var(--accent)' }}>
                    View {importReport.validation_failures.length} validation failures
                  </summary>
                  <ul style={{ maxHeight: 150, overflowY: 'auto', marginTop: 6 }}>
                    {importReport.validation_failures.map((f, i) => (
                      <li key={i}>Row {f.row}: {f.errors.join(', ')}</li>
                    ))}
                  </ul>
                </details>
              )}
            </div>
          )}
        </div>
      </div>

      {editing !== null && (
        <Modal title={editing.id ? 'Edit Video' : 'Add Video'} onClose={() => setEditing(null)}>
          <form onSubmit={handleSave}>
            <div className="ss-form-group">
              <label className="ss-label">Title</label>
              <input className="ss-input" required value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
            </div>
            <div className="ss-form-group">
              <label className="ss-label">Description</label>
              <textarea className="ss-input" rows={3} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
            </div>
            <div className="ss-form-group">
              <label className="ss-label">Category</label>
              <select className="ss-select" required value={form.category_id} onChange={(e) => setForm({ ...form, category_id: e.target.value })}>
                <option value="">Select category</option>
                {categories.map((c) => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
            </div>
            <div className="ss-form-group">
              <label className="ss-label">Duration (seconds)</label>
              <input className="ss-input" type="number" min="1" required value={form.duration} onChange={(e) => setForm({ ...form, duration: e.target.value })} />
            </div>
            <div className="ss-form-group">
              <label className="ss-label">Thumbnail URL</label>
              <input className="ss-input" value={form.thumbnail_url} onChange={(e) => setForm({ ...form, thumbnail_url: e.target.value })} />
            </div>
            <div className="ss-form-group">
              <label className="ss-label">Video URL</label>
              <input className="ss-input" value={form.video_url} onChange={(e) => setForm({ ...form, video_url: e.target.value })} />
            </div>
            <div className="ss-form-group">
              <label className="ss-label">Release Date</label>
              <input className="ss-input" type="date" value={form.release_date} onChange={(e) => setForm({ ...form, release_date: e.target.value })} />
            </div>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
              <button type="button" className="ss-btn ss-btn-outline" onClick={() => setEditing(null)}>Cancel</button>
              <button type="submit" className="ss-btn ss-btn-primary" disabled={saving}>
                {saving ? 'Saving...' : 'Save'}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  )
}
