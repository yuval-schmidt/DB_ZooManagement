import { useState, useEffect, useRef } from 'react'

/* ═══════════════════════════════════════════════════════════
   TOAST SYSTEM
═══════════════════════════════════════════════════════════ */
let _addToast = null
export function useToastRegister(fn) { _addToast = fn }
export function toast(msg, type = 'success') {
  if (_addToast) _addToast(msg, type)
}

export function ToastContainer() {
  const [toasts, setToasts] = useState([])
  useToastRegister((msg, type) => {
    const id = Date.now()
    setToasts(t => [...t, { id, msg, type }])
    setTimeout(() => setToasts(t => t.filter(x => x.id !== id)), 3500)
  })
  const icons = { success: '✅', error: '❌', info: 'ℹ️', warn: '⚠️' }
  return (
    <div className="toast-container">
      {toasts.map(t => (
        <div key={t.id} className={`toast toast-${t.type}`}>
          <span>{icons[t.type] || '•'}</span>
          <span>{t.msg}</span>
        </div>
      ))}
    </div>
  )
}

/* ═══════════════════════════════════════════════════════════
   MODAL
═══════════════════════════════════════════════════════════ */
export function Modal({ title, onClose, children, footer }) {
  useEffect(() => {
    const esc = (e) => e.key === 'Escape' && onClose()
    window.addEventListener('keydown', esc)
    return () => window.removeEventListener('keydown', esc)
  }, [onClose])

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal fade-in">
        <div className="modal-header">
          <h2 className="modal-title">{title}</h2>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body">{children}</div>
        {footer && <div className="modal-footer">{footer}</div>}
      </div>
    </div>
  )
}

/* ═══════════════════════════════════════════════════════════
   SPINNER
═══════════════════════════════════════════════════════════ */
export function Spinner({ size = 20 }) {
  return <div className="spinner" style={{ width: size, height: size }} />
}

/* ═══════════════════════════════════════════════════════════
   DATA TABLE
═══════════════════════════════════════════════════════════ */
const PAGE_SIZE = 15

export function DataTable({ headers, rows, onEdit, onDelete, pkColumns = [], loading }) {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')

  const filtered = rows.filter(row =>
    Object.values(row).some(v => v && String(v).toLowerCase().includes(search.toLowerCase()))
  )
  const total = Math.ceil(filtered.length / PAGE_SIZE)
  const paged = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)

  // Health status badge
  const statusBadge = (val) => {
    if (!val) return val
    const v = val.toLowerCase()
    if (v === 'healthy') return <span className="badge badge-green">{val}</span>
    if (v === 'sick') return <span className="badge badge-yellow">{val}</span>
    if (v === 'critical') return <span className="badge badge-red">{val}</span>
    if (v === 'deceased') return <span className="badge badge-gray">{val}</span>
    if (v === 'recovering') return <span className="badge badge-blue">{val}</span>
    return val
  }

  if (loading) return (
    <div className="empty-state"><Spinner size={32} /><p style={{marginTop:16}}>טוען נתונים...</p></div>
  )

  return (
    <div>
      <div className="toolbar">
        <input
          className="search-input"
          placeholder="🔍  חיפוש..."
          value={search}
          onChange={e => { setSearch(e.target.value); setPage(1) }}
        />
        <span style={{ color: 'var(--text-muted)', fontSize: 13 }}>
          {filtered.length} רשומות{search ? ' (מסונן)' : ''}
        </span>
      </div>

      <div className="data-table-wrap">
        <table className="data-table">
          <thead>
            <tr>
              {headers.map(h => <th key={h}>{h}</th>)}
              {(onEdit || onDelete) && <th>פעולות</th>}
            </tr>
          </thead>
          <tbody>
            {paged.length === 0 ? (
              <tr><td colSpan={headers.length + 1} style={{ textAlign: 'center', padding: 40, color: 'var(--text-muted)' }}>
                אין רשומות
              </td></tr>
            ) : paged.map((row, i) => {
              const pkKey = pkColumns.map(pk => row[`__pk_${pk}`]).join(',')
              return (
                <tr key={i}>
                  {headers.map(h => (
                    <td key={h} title={row[h]}>
                      {h.includes('סטטוס') || h === 'healthstatus' ? statusBadge(row[h]) : (row[h] || '—')}
                    </td>
                  ))}
                  {(onEdit || onDelete) && (
                    <td>
                      <div style={{ display: 'flex', gap: 6 }}>
                        {onEdit && (
                          <button className="btn btn-ghost btn-sm" onClick={() => onEdit(pkKey, row)}>✏️</button>
                        )}
                        {onDelete && (
                          <button className="btn btn-sm" style={{ background: 'rgba(239,68,68,0.1)', color: '#f87171', border: '1px solid rgba(239,68,68,0.2)' }}
                            onClick={() => onDelete(pkKey)}>🗑️</button>
                        )}
                      </div>
                    </td>
                  )}
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {total > 1 && (
        <div className="pagination">
          <button className="page-btn" onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>‹</button>
          {Array.from({ length: Math.min(total, 7) }, (_, i) => {
            const p = i + 1
            return <button key={p} className={`page-btn ${page === p ? 'active' : ''}`} onClick={() => setPage(p)}>{p}</button>
          })}
          <button className="page-btn" onClick={() => setPage(p => Math.min(total, p + 1))} disabled={page === total}>›</button>
        </div>
      )}
    </div>
  )
}

/* ═══════════════════════════════════════════════════════════
   STAT CARD
═══════════════════════════════════════════════════════════ */
export function StatCard({ icon, label, value, color = 'var(--primary)', gradient }) {
  const [displayed, setDisplayed] = useState(0)
  const target = typeof value === 'number' ? value : 0

  useEffect(() => {
    if (!target) return
    let start = 0
    const step = Math.ceil(target / 40)
    const t = setInterval(() => {
      start = Math.min(start + step, target)
      setDisplayed(start)
      if (start >= target) clearInterval(t)
    }, 20)
    return () => clearInterval(t)
  }, [target])

  return (
    <div className="stat-card" style={{ borderColor: `${color}33` }}>
      <div style={{
        position: 'absolute', inset: 0, borderRadius: 'var(--radius)',
        background: `radial-gradient(ellipse at top right, ${color}0f, transparent 70%)`,
        pointerEvents: 'none',
      }} />
      <div className="stat-icon">{icon}</div>
      <div className="stat-value" style={{ color }}>{typeof value === 'number' ? displayed.toLocaleString() : value}</div>
      <div className="stat-label">{label}</div>
    </div>
  )
}

/* ═══════════════════════════════════════════════════════════
   BAR CHART
═══════════════════════════════════════════════════════════ */
export function BarChart({ data, color = 'var(--primary)' }) {
  const [ready, setReady] = useState(false)
  useEffect(() => { setTimeout(() => setReady(true), 100) }, [])
  if (!data || !data.length) return <div className="empty-state"><p>אין נתונים</p></div>
  const max = Math.max(...data.map(d => d.count))
  return (
    <div className="bar-chart">
      {data.map((d, i) => (
        <div key={i} className="bar-row">
          <div className="bar-label" title={d.name}>{d.name}</div>
          <div className="bar-track">
            <div className="bar-fill" style={{
              width: ready ? `${(d.count / max) * 100}%` : '0%',
              background: `linear-gradient(90deg, ${color}, ${color}88)`,
              transitionDelay: `${i * 60}ms`,
            }} />
          </div>
          <div className="bar-count">{d.count}</div>
        </div>
      ))}
    </div>
  )
}

/* ═══════════════════════════════════════════════════════════
   CONFIRM DIALOG
═══════════════════════════════════════════════════════════ */
export function ConfirmModal({ message, onConfirm, onCancel }) {
  return (
    <Modal title="אישור פעולה" onClose={onCancel}
      footer={<>
        <button className="btn btn-red" onClick={onConfirm}>מחק</button>
        <button className="btn btn-ghost" onClick={onCancel}>ביטול</button>
      </>}>
      <p style={{ fontSize: 15, lineHeight: 1.6 }}>{message}</p>
    </Modal>
  )
}
