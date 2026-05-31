import { useState, useEffect } from 'react'
import { api } from '../api'
import { DataTable, Modal, ConfirmModal, Spinner } from '../components'
import { toast } from '../components'

const FIELD_TYPE_INPUT = { text: 'text', int: 'number', float: 'number', date: 'date' }

export default function TablePage({ tableKey }) {
  const [meta, setMeta]         = useState(null)
  const [rows, setRows]         = useState([])
  const [headers, setHeaders]   = useState([])
  const [pkCols, setPkCols]     = useState([])
  const [loading, setLoading]   = useState(true)
  const [fkOptions, setFkOptions] = useState({})

  // Modals
  const [showInsert, setShowInsert]   = useState(false)
  const [showUpdate, setShowUpdate]   = useState(false)
  const [showConfirm, setShowConfirm] = useState(null)  // pk string

  const [formData, setFormData] = useState({})
  const [saving, setSaving]     = useState(false)

  // ── Load meta + rows ───────────────────────────────────────────────────────
  const loadRows = () => {
    return api.tableRows(tableKey).then(res => {
      setHeaders(res.headers)
      setRows(res.rows)
      setPkCols(res.pkColumns)
    })
  }

  useEffect(() => {
    if (!tableKey) return
    setLoading(true)
    Promise.all([api.tableMeta(tableKey), api.tableRows(tableKey)])
      .then(([m, r]) => {
        setMeta(m)
        setHeaders(r.headers)
        setRows(r.rows)
        setPkCols(r.pkColumns)
        // Load FK options
        const fkLoads = m.foreignKeys.map(fk =>
          api.fkOptions(tableKey, fk.column)
            .then(opts => [fk.column, opts])
            .catch(() => [fk.column, []])
        )
        return Promise.all(fkLoads)
      })
      .then(pairs => {
        const map = {}
        pairs.forEach(([col, opts]) => { map[col] = opts })
        setFkOptions(map)
      })
      .catch(e => toast(e.message, 'error'))
      .finally(() => setLoading(false))
  }, [tableKey])

  // ── Form helpers ───────────────────────────────────────────────────────────
  const openInsert = () => {
    setFormData({})
    setShowInsert(true)
  }

  const openUpdate = async (pkStr) => {
    try {
      const row = await api.tableRow(tableKey, pkStr)
      setFormData(row)
      setShowUpdate(pkStr)
    } catch (e) {
      toast(e.message, 'error')
    }
  }

  const handleSave = async (isUpdate) => {
    setSaving(true)
    try {
      if (isUpdate) {
        await api.updateRow(tableKey, showUpdate, formData)
        toast('✅ הרשומה עודכנה בהצלחה', 'success')
        setShowUpdate(false)
      } else {
        await api.insertRow(tableKey, formData)
        toast('✅ הרשומה נוספה בהצלחה', 'success')
        setShowInsert(false)
      }
      await loadRows()
    } catch (e) {
      toast(e.message, 'error')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (pkStr) => {
    try {
      await api.deleteRow(tableKey, pkStr)
      toast('🗑️ הרשומה נמחקה', 'success')
      setShowConfirm(null)
      await loadRows()
    } catch (e) {
      toast(e.message, 'error')
    }
  }

  // ── Form renderer ──────────────────────────────────────────────────────────
  const renderForm = () => {
    if (!meta) return null
    const fields = []

    meta.columns.forEach(col => {
      if (col.type === 'readonly') return
      if (col.choices) {
        fields.push(
          <div className="form-group" key={col.name}>
            <label className="form-label">{col.label}</label>
            <select className="form-select"
              value={formData[col.name] || ''}
              onChange={e => setFormData(p => ({ ...p, [col.name]: e.target.value }))}>
              <option value="">בחר...</option>
              {col.choices.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
        )
      } else {
        fields.push(
          <div className="form-group" key={col.name}>
            <label className="form-label">{col.label}</label>
            <input
              className="form-input"
              type={FIELD_TYPE_INPUT[col.type] || 'text'}
              value={formData[col.name] || ''}
              onChange={e => setFormData(p => ({ ...p, [col.name]: e.target.value }))}
              placeholder={col.label}
            />
          </div>
        )
      }
    })

    meta.foreignKeys.forEach(fk => {
      const opts = fkOptions[fk.column] || []
      fields.push(
        <div className="form-group" key={fk.column}>
          <label className="form-label">{fk.label}</label>
          <select className="form-select"
            value={formData[fk.column] || ''}
            onChange={e => setFormData(p => ({ ...p, [fk.column]: e.target.value }))}>
            <option value="">בחר...</option>
            {opts.map(o => <option key={o.id} value={o.id}>{o.label}</option>)}
          </select>
        </div>
      )
    })

    return fields
  }

  // ── Render ─────────────────────────────────────────────────────────────────
  if (!tableKey) return (
    <div className="empty-state">
      <div className="icon">👈</div>
      <h3>בחרו טבלה מהסרגל הצדדי</h3>
    </div>
  )

  return (
    <div className="fade-in">
      <div className="page-header">
        <h1><span className="gradient-text">{meta?.displayName || tableKey}</span></h1>
        <p>ניהול רשומות – שליפה, הוספה, עדכון ומחיקה</p>
      </div>

      <div className="toolbar" style={{ marginBottom: 20 }}>
        {!meta?.readOnly && (
          <button className="btn btn-primary" onClick={openInsert}>
            ➕ הוסף רשומה
          </button>
        )}
        {meta?.readOnly && (
          <span className="badge badge-purple">📋 טבלת יומן – רק קריאה</span>
        )}
        <button className="btn btn-ghost" onClick={() => { setLoading(true); loadRows().finally(() => setLoading(false)) }}>
          🔄 רענון
        </button>
        <span style={{ color: 'var(--text-muted)', fontSize: 13, marginRight: 'auto' }}>
          {rows.length} רשומות סה"כ
        </span>
      </div>

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <DataTable
          headers={headers}
          rows={rows}
          pkColumns={pkCols}
          loading={loading}
          onEdit={meta?.readOnly ? null : (pk, row) => openUpdate(pk)}
          onDelete={meta?.readOnly ? null : (pk) => setShowConfirm(pk)}
        />
      </div>

      {/* INSERT Modal */}
      {showInsert && (
        <Modal
          title={`➕ הוסף – ${meta?.displayName}`}
          onClose={() => setShowInsert(false)}
          footer={<>
            <button className="btn btn-primary" onClick={() => handleSave(false)} disabled={saving}>
              {saving ? <Spinner size={16} /> : '💾 שמור'}
            </button>
            <button className="btn btn-ghost" onClick={() => setShowInsert(false)}>ביטול</button>
          </>}
        >
          {renderForm()}
        </Modal>
      )}

      {/* UPDATE Modal */}
      {showUpdate && (
        <Modal
          title={`✏️ עדכן – ${meta?.displayName}`}
          onClose={() => setShowUpdate(false)}
          footer={<>
            <button className="btn btn-primary" onClick={() => handleSave(true)} disabled={saving}>
              {saving ? <Spinner size={16} /> : '💾 שמור שינויים'}
            </button>
            <button className="btn btn-ghost" onClick={() => setShowUpdate(false)}>ביטול</button>
          </>}
        >
          {renderForm()}
        </Modal>
      )}

      {/* DELETE Confirm */}
      {showConfirm && (
        <ConfirmModal
          message={`האם למחוק את הרשומה? פעולה זו אינה הפיכה.`}
          onConfirm={() => handleDelete(showConfirm)}
          onCancel={() => setShowConfirm(null)}
        />
      )}
    </div>
  )
}
