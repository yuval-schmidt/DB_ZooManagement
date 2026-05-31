import { useState, useEffect } from 'react'
import { api } from '../api'
import { StatCard, BarChart, Spinner } from '../components'


const STATUS_COLOR = {
  Healthy:    'var(--primary)',
  Sick:       'var(--gold)',
  Critical:   'var(--red)',
  Deceased:   'var(--text-dim)',
  Recovering: 'var(--blue)',
}

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    api.stats()
      .then(setStats)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div style={{ display: 'flex', justifyContent: 'center', paddingTop: 80 }}>
      <Spinner size={48} />
    </div>
  )

  if (error) return (
    <div className="conn-banner err">
      <span>⚠️</span>
      <span>שגיאת חיבור: {error}. ודאו שה-Backend פועל: <code>uvicorn main:app --reload</code></span>
    </div>
  )

  const { counts, animalsPerHabitat, recentHealth } = stats

  return (
    <div className="fade-in">
      <div className="page-header">
        <h1><span className="gradient-text">🦁 מערכת ניהול גן החיות</span></h1>
        <p>ברוכים הבאים — סקירת מצב כללית של מסד הנתונים</p>
      </div>

      {/* ── KPI Stats ── */}
      <div className="grid-4" style={{ marginBottom: 28 }}>
        <StatCard icon="🦒" label="חיות"       value={counts.animals}    color="var(--primary)" />
        <StatCard icon="👨‍⚕️" label="וטרינרים"  value={counts.vets}       color="var(--purple-lt)" />
        <StatCard icon="👷" label="עובדים"     value={counts.employees}  color="var(--gold)" />
        <StatCard icon="🏥" label="ביקורים רפואיים" value={counts.visits} color="var(--teal)" />
      </div>

      <div className="grid-2" style={{ marginBottom: 28 }}>
        <StatCard icon="🏕️" label="בתי גידול"  value={counts.habitats}   color="var(--gold-lt)" />
        <StatCard icon="🐾" label="מינים"      value={counts.species}    color="var(--blue)" />
      </div>

      {/* ── Charts + Activity ── */}
      <div className="grid-2">
        {/* Bar chart */}
        <div className="card slide-up">
          <div className="section-title">📊 חיות לפי בית גידול</div>
          {animalsPerHabitat?.length > 0
            ? <BarChart data={animalsPerHabitat} color="var(--primary)" />
            : <div className="empty-state"><p>אין נתונים</p></div>
          }
        </div>

        {/* Activity feed */}
        <div className="card slide-up" style={{ animationDelay: '0.1s' }}>
          <div className="section-title">🩺 בדיקות בריאות אחרונות</div>
          {recentHealth?.length > 0 ? recentHealth.map((item, i) => (
            <div className="activity-item" key={i}>
              <div className="activity-dot" style={{ background: STATUS_COLOR[item.status] || 'var(--text-muted)' }} />
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600, fontSize: 14 }}>{item.animal}</div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{item.date}</div>
              </div>
              <span className={`badge badge-${
                item.status === 'Healthy' ? 'green'
                : item.status === 'Sick' ? 'yellow'
                : item.status === 'Critical' ? 'red'
                : item.status === 'Deceased' ? 'gray'
                : 'blue'
              }`}>{item.status}</span>
              {item.weight && <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>{item.weight} ק"ג</span>}
            </div>
          )) : <div className="empty-state"><p>אין בדיקות בריאות</p></div>}
        </div>
      </div>
    </div>
  )
}
