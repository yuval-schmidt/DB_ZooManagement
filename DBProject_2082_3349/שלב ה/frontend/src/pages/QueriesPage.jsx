import { useState, useEffect } from 'react'
import { api } from '../api'
import { Spinner, DataTable } from '../components'
import { toast } from '../components'

const QUERY_META = {
  food_by_species:          { icon: '🥦', color: 'var(--primary)',    title: 'סך מזון לפי מין' },
  habitat_missing_checkups: { icon: '🏕️', color: 'var(--gold)',       title: 'בתי גידול ללא בדיקות' },
  diet_cost_april:          { icon: '📊', color: 'var(--purple-lt)',  title: 'עלות תזונה – אפריל' },
  weight_december:          { icon: '⚖️', color: 'var(--teal)',       title: 'משקל בדיקות – דצמבר' },
}

export default function QueriesPage() {
  const [queries, setQueries]     = useState([])
  const [selected, setSelected]   = useState(null)
  const [result, setResult]       = useState(null)
  const [loading, setLoading]     = useState(false)
  const [running, setRunning]     = useState(false)

  useEffect(() => {
    setLoading(true)
    api.queriesList()
      .then(q => { setQueries(q); if (q.length) setSelected(q[0].key) })
      .catch(e => toast(e.message, 'error'))
      .finally(() => setLoading(false))
  }, [])

  const run = async () => {
    if (!selected) return
    setRunning(true)
    setResult(null)
    try {
      const res = await api.runQuery(selected)
      setResult(res)
    } catch (e) {
      toast(e.message, 'error')
    } finally {
      setRunning(false)
    }
  }

  const selectedQ = queries.find(q => q.key === selected)

  if (loading) return <div style={{ display: 'flex', justifyContent: 'center', paddingTop: 80 }}><Spinner size={40} /></div>

  return (
    <div className="fade-in">
      <div className="page-header">
        <h1><span className="gradient-text">📊 שאילתות ניתוח – שלב ב'</span></h1>
        <p>הרצת שאילתות SQL מנותחות על בסיס הנתונים</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: 24, alignItems: 'start' }}>
        {/* ── Query selector ── */}
        <div>
          <div className="section-title">📋 בחר שאילתה</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {queries.map(q => {
              const meta = QUERY_META[q.key] || { icon: '🔍', color: 'var(--text-muted)', title: q.title }
              const isSel = selected === q.key
              return (
                <div
                  key={q.key}
                  className={`query-card ${isSel ? 'selected' : ''}`}
                  onClick={() => { setSelected(q.key); setResult(null) }}
                  style={{ borderRightColor: isSel ? meta.color : '' }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
                    <span style={{ fontSize: 20 }}>{meta.icon}</span>
                    <span style={{ fontWeight: 700, fontSize: 14, color: isSel ? meta.color : 'var(--text)' }}>
                      {q.title}
                    </span>
                  </div>
                  <p style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.5 }}>{q.description}</p>
                </div>
              )
            })}
          </div>

          <button
            className="btn btn-primary"
            style={{ width: '100%', marginTop: 16, justifyContent: 'center' }}
            onClick={run}
            disabled={running || !selected}
          >
            {running ? <><Spinner size={16} /> מריץ...</> : '▶  הרץ שאילתה'}
          </button>
        </div>

        {/* ── Results ── */}
        <div>
          {/* Selected query info */}
          {selectedQ && (
            <div className="card" style={{ marginBottom: 20, background: 'var(--bg3)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <span style={{ fontSize: 28 }}>{QUERY_META[selectedQ.key]?.icon || '🔍'}</span>
                <div>
                  <div style={{ fontWeight: 700, fontSize: 16 }}>{selectedQ.title}</div>
                  <div style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 4 }}>{selectedQ.description}</div>
                </div>
              </div>
            </div>
          )}

          {/* Result table */}
          {running && (
            <div style={{ display: 'flex', justifyContent: 'center', padding: 60 }}>
              <Spinner size={40} />
            </div>
          )}

          {result && !running && (
            <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
              <div style={{ padding: '14px 20px', background: 'var(--bg3)', display: 'flex', alignItems: 'center', gap: 12, borderBottom: '1px solid var(--border)' }}>
                <span className="badge badge-green">✅ {result.count} תוצאות</span>
                <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>השאילתה הושלמה בהצלחה</span>
              </div>
              <DataTable
                headers={result.headers}
                rows={result.rows.map(r => Object.fromEntries(result.headers.map((h, i) => [h, r[i]])))}
                loading={false}
              />
            </div>
          )}

          {!result && !running && (
            <div className="empty-state">
              <div className="icon">▶️</div>
              <h3>בחרו שאילתה והריצו</h3>
              <p>התוצאות יוצגו כאן</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
