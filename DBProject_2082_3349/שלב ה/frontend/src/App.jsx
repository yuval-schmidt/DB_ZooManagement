import { useState, useEffect } from 'react'
import { api } from './api'
import { ToastContainer } from './components'
import Dashboard from './pages/Dashboard'
import TablePage from './pages/TablePage'
import QueriesPage from './pages/QueriesPage'
import RoutinesPage from './pages/RoutinesPage'
import './index.css'

const GROUP_ICONS = {
  'ניהול גן החיות':  '🌿',
  'צוות ופעילויות':  '👥',
  'מחלקה וטרינרית':  '🩺',
  'מערכת (יומנים)':  '📋',
}

const TABLE_ICONS = {
  HABITAT: '🏕️', SPECIES: '🐾', DIETPLAN: '🥗', ANIMAL: '🦒',
  HEALTHRECORD: '🩺', DAILYFEEDING: '🍖', EMPLOYEE: '👷',
  ACTIVITY_TYPE: '📌', ACTIVITY: '🎯', ACTIVITY_EMPLOYEE: '🔗',
  ACTIVITY_ANIMAL: '🔗', VETERINARIAN: '👨‍⚕️', MEDICALVISIT: '🏥',
  TREATMENT: '💊', MEDICATION: '💉', VACCINATION: '🛡️',
  MIRSHAM_VISIT_TREATMENT: '🔗', HERGEL_TREATMENT_MEDICATION: '🔗',
  TREATMENT_VACCINATION: '🔗', HABITAT_CAPACITY_LOG: '📊',
}

export default function App() {
  const [tables, setTables]     = useState({})
  const [page, setPage]         = useState('dashboard')  // 'dashboard' | 'queries' | 'routines' | table-key
  const [tableKey, setTableKey] = useState(null)

  useEffect(() => {
    api.tablesList()
      .then(setTables)
      .catch(() => {})
  }, [])

  const goTable = (key) => { setPage('table'); setTableKey(key) }

  const nav = (p) => { setPage(p); if (p !== 'table') setTableKey(null) }

  const currentTitle =
    page === 'dashboard' ? 'לוח בקרה' :
    page === 'queries'   ? 'שאילתות' :
    page === 'routines'  ? 'פרוצדורות' :
    tableKey ? tableKey : ''

  return (
    <div className="app-layout">
      {/* ── SIDEBAR ────────────────────────────────────────────── */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <h1>🦁 Zoo<br />Management</h1>
          <p>מערכת ניהול גן חיות</p>
        </div>

        <nav className="sidebar-nav">
          {/* Main nav */}
          <div className="sidebar-section-title">ניווט</div>
          <SidebarItem icon="🏠" label="לוח בקרה" active={page === 'dashboard'} onClick={() => nav('dashboard')} />
          <SidebarItem icon="📊" label="שאילתות – שלב ב'" active={page === 'queries'}   onClick={() => nav('queries')} />
          <SidebarItem icon="⚙️" label="פרוצדורות – שלב ד'" active={page === 'routines'} onClick={() => nav('routines')} />

          {/* Table groups */}
          <div className="sidebar-section-title" style={{ marginTop: 12 }}>טבלאות CRUD</div>
          {Object.entries(tables).map(([group, items]) => (
            <div className="sidebar-group" key={group}>
              <div className="sidebar-group-label">{GROUP_ICONS[group] || '📁'} {group}</div>
              {items.map(t => (
                <SidebarItem
                  key={t.key}
                  icon={TABLE_ICONS[t.key] || '•'}
                  label={t.displayName}
                  active={page === 'table' && tableKey === t.key}
                  onClick={() => goTable(t.key)}
                />
              ))}
            </div>
          ))}

          {Object.keys(tables).length === 0 && (
            <div style={{ padding: '20px 8px', color: 'var(--text-dim)', fontSize: 12, textAlign: 'center' }}>
              <div style={{ marginBottom: 8 }}>⚠️</div>
              לא נמצאו טבלאות.<br />ודאו שה-Backend פועל.
            </div>
          )}
        </nav>

        <div className="sidebar-footer">
          שלב ה׳ · PostgreSQL + FastAPI + React
        </div>
      </aside>

      {/* ── MAIN CONTENT ───────────────────────────────────────── */}
      <main className="main-content">
        {page === 'dashboard' && <Dashboard />}
        {page === 'table'     && <TablePage tableKey={tableKey} key={tableKey} />}
        {page === 'queries'   && <QueriesPage />}
        {page === 'routines'  && <RoutinesPage />}
      </main>

      <ToastContainer />
    </div>
  )
}

function SidebarItem({ icon, label, active, onClick }) {
  return (
    <button className={`sidebar-item ${active ? 'active' : ''}`} onClick={onClick}>
      <span className="item-icon">{icon}</span>
      <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{label}</span>
    </button>
  )
}
