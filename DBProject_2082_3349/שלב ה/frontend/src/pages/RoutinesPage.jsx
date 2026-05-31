import { useState, useEffect } from 'react'
import { api } from '../api'
import { Spinner, DataTable } from '../components'
import { toast } from '../components'

/* ─── Section card component ──────────────────────────────────────────────── */
function RoutineCard({ color, icon, title, desc, badge, children }) {
  return (
    <div className="routine-card" style={{ borderColor: `${color}33` }}>
      <div className="routine-card-header" style={{
        background: `linear-gradient(135deg, ${color}22, transparent)`,
        borderBottom: `1px solid ${color}33`,
      }}>
        <div style={{
          width: 44, height: 44, borderRadius: 12,
          background: `${color}22`, border: `1px solid ${color}44`,
          display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 22,
        }}>{icon}</div>
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 700, fontSize: 15, color }}>{title}</div>
          <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 3 }}>{desc}</div>
        </div>
        {badge && <span className={`badge badge-${badge}`}>{badge === 'green' ? 'פונקציה' : badge === 'purple' ? 'פרוצדורה' : 'Trigger'}</span>}
      </div>
      <div className="routine-card-body">{children}</div>
    </div>
  )
}

/* ─── Result mini-table ───────────────────────────────────────────────────── */
function ResultTable({ headers, rows, color }) {
  if (!rows || rows.length === 0) return <div className="empty-state" style={{ padding: 30 }}><p>לא נמצאו תוצאות</p></div>
  return (
    <div className="data-table-wrap" style={{ marginTop: 16 }}>
      <table className="data-table">
        <thead>
          <tr>{headers.map(h => <th key={h} style={{ color }}>{h}</th>)}</tr>
        </thead>
        <tbody>
          {rows.slice(0, 20).map((row, i) => (
            <tr key={i}>
              {headers.map(h => <td key={h}>{row[h] ?? '—'}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

/* ─── Dropdown ────────────────────────────────────────────────────────────── */
function DropSelect({ items, value, onChange, placeholder }) {
  return (
    <select className="form-select" style={{ width: 'auto', minWidth: 220 }}
      value={value} onChange={e => onChange(Number(e.target.value))}>
      <option value="">{placeholder}</option>
      {items.map(it => <option key={it.id} value={it.id}>{it.name}</option>)}
    </select>
  )
}

/* ═══════════════════════════════════════════════════════════
   MAIN PAGE
═══════════════════════════════════════════════════════════ */
export default function RoutinesPage() {
  // Dropdowns data
  const [habitats, setHabitats]   = useState([])
  const [vets, setVets]           = useState([])
  const [speciesList, setSpecies] = useState([])

  // Selected values
  const [habitatId, setHabitatId]     = useState('')
  const [vetId, setVetId]             = useState('')
  const [speciesId, setSpeciesId]     = useState('')
  const [pct, setPct]                 = useState(10)
  const [capHabitatId, setCapHabitat] = useState('')
  const [newCap, setNewCap]           = useState(100)

  // Results
  const [habitatResult, setHabitatResult]   = useState(null)
  const [vetResult, setVetResult]           = useState(null)
  const [checkupsResult, setCheckupsResult] = useState(null)
  const [dietResult, setDietResult]         = useState(null)
  const [triggerResult, setTriggerResult]   = useState(null)

  // Loading flags
  const [loading, setLoading] = useState({})
  const setLoad = (key, val) => setLoading(p => ({ ...p, [key]: val }))

  useEffect(() => {
    api.habitats().then(setHabitats).catch(() => {})
    api.vets().then(setVets).catch(() => {})
    api.species().then(setSpecies).catch(() => {})
  }, [])

  // ── Runners ─────────────────────────────────────────────────────────────
  const runHabitatCost = async () => {
    if (!habitatId) return toast('בחרו בית גידול', 'warn')
    setLoad('habitat', true)
    try {
      const r = await api.habitatCost(habitatId)
      setHabitatResult(r)
      toast(`עלות: ${r.formatted}`, 'success')
    } catch (e) { toast(e.message, 'error') }
    finally { setLoad('habitat', false) }
  }

  const runVet = async () => {
    if (!vetId) return toast('בחרו וטרינר', 'warn')
    setLoad('vet', true)
    try {
      const r = await api.animalsByVet(vetId)
      setVetResult(r)
      toast(`נמצאו ${r.count} חיות`, 'success')
    } catch (e) { toast(e.message, 'error') }
    finally { setLoad('vet', false) }
  }

  const runCheckups = async () => {
    setLoad('checkups', true)
    try {
      const r = await api.checkups()
      setCheckupsResult(r)
      toast(`נוצרו ${r.created} רשומות בריאות`, 'success')
    } catch (e) { toast(e.message, 'error') }
    finally { setLoad('checkups', false) }
  }

  const runDiet = async () => {
    if (!speciesId) return toast('בחרו מין', 'warn')
    setLoad('diet', true)
    try {
      const r = await api.adjustDiet(speciesId, pct)
      setDietResult(r)
      toast(`עודכנו ${r.updated} תוכניות תזונה`, 'success')
    } catch (e) { toast(e.message, 'error') }
    finally { setLoad('diet', false) }
  }

  const runTrigger = async () => {
    if (!capHabitatId) return toast('בחרו בית גידול', 'warn')
    setLoad('trigger', true)
    try {
      const r = await api.triggerDemo(capHabitatId, newCap)
      setTriggerResult(r)
      toast('הטריגר הופעל – הרשומה נוצרה ביומן', 'success')
    } catch (e) { toast(e.message, 'error') }
    finally { setLoad('trigger', false) }
  }

  return (
    <div className="fade-in">
      <div className="page-header">
        <h1><span className="gradient-text">⚙️ פונקציות ופרוצדורות – שלב ד'</span></h1>
        <p>הפעלת תתי-תוכניות שנכתבו בשלב ד' של הפרויקט</p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

        {/* ── Function 1: Habitat Diet Cost ─────────────────────────────── */}
        <RoutineCard
          color="var(--primary)"
          icon="🌿"
          title="Get_Habitat_Diet_Cost"
          desc="מחשבת סך העלות היומית של תזונה לכל החיות בבית גידול"
          badge="green"
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
            <DropSelect items={habitats} value={habitatId} onChange={setHabitatId} placeholder="בחר בית גידול..." />
            <button className="btn btn-primary" onClick={runHabitatCost} disabled={loading.habitat}>
              {loading.habitat ? <Spinner size={16} /> : '▶ הפעל'}
            </button>
            {habitatResult && (
              <div style={{
                background: 'rgba(0,229,160,0.1)', border: '1px solid rgba(0,229,160,0.3)',
                borderRadius: 10, padding: '10px 20px', fontSize: 24, fontWeight: 800,
                color: 'var(--primary)',
              }}>
                {habitatResult.formatted}
                <div style={{ fontSize: 12, color: 'var(--text-muted)', fontWeight: 400, marginTop: 2 }}>סך עלות יומית</div>
              </div>
            )}
          </div>
        </RoutineCard>

        {/* ── Function 2: Animals by Vet ────────────────────────────────── */}
        <RoutineCard
          color="var(--teal)"
          icon="🩺"
          title="Get_Animals_By_Vet_RefCursor"
          desc="מחזירה רשימת חיות שטופלו על ידי וטרינר נבחר"
          badge="green"
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap', marginBottom: 12 }}>
            <DropSelect items={vets} value={vetId} onChange={setVetId} placeholder="בחר וטרינר..." />
            <button className="btn btn-ghost" style={{ borderColor: 'var(--teal)', color: 'var(--teal)' }} onClick={runVet} disabled={loading.vet}>
              {loading.vet ? <Spinner size={16} /> : '▶ הפעל'}
            </button>
            {vetResult && <span className="badge badge-blue">🐾 {vetResult.count} חיות</span>}
          </div>
          {vetResult && (
            <ResultTable
              color="var(--teal)"
              headers={['animal', 'birthdate', 'visitdate', 'reason']}
              rows={vetResult.rows}
            />
          )}
        </RoutineCard>

        {/* ── Procedure 1: Routine Checkups ─────────────────────────────── */}
        <RoutineCard
          color="var(--purple-lt)"
          icon="📋"
          title="Process_Routine_Checkups"
          desc="יוצרת רשומות בריאות אוטומטיות לחיות שלא עברו בדיקה בשנה האחרונה"
          badge="purple"
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
            <button className="btn btn-purple" onClick={runCheckups} disabled={loading.checkups}>
              {loading.checkups ? <Spinner size={16} /> : '▶ הפעל פרוצדורה'}
            </button>
            {checkupsResult && <span className="badge badge-purple">נוצרו {checkupsResult.created} רשומות</span>}
          </div>
          {checkupsResult && (
            <ResultTable
              color="var(--purple-lt)"
              headers={['animal', 'date', 'weight', 'status']}
              rows={checkupsResult.rows}
            />
          )}
        </RoutineCard>

        {/* ── Procedure 2: Adjust Diet Cost ─────────────────────────────── */}
        <RoutineCard
          color="var(--gold)"
          icon="🥗"
          title="Adjust_Diet_Cost_By_Species"
          desc="מעלה את עלות תוכניות התזונה לפי אחוז למין נבחר"
          badge="purple"
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap', marginBottom: 12 }}>
            <DropSelect items={speciesList} value={speciesId} onChange={setSpeciesId} placeholder="בחר מין..." />
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <label style={{ fontSize: 13, color: 'var(--text-muted)' }}>אחוז העלאה:</label>
              <input
                type="number" className="form-input"
                style={{ width: 80 }}
                value={pct}
                onChange={e => setPct(Number(e.target.value))}
                min={0} max={500}
              />
              <span style={{ color: 'var(--text-muted)' }}>%</span>
            </div>
            <button className="btn btn-gold" onClick={runDiet} disabled={loading.diet}>
              {loading.diet ? <Spinner size={16} /> : '▶ הפעל'}
            </button>
            {dietResult && <span className="badge badge-yellow">עודכנו {dietResult.updated} תוכניות</span>}
          </div>
          {dietResult && (
            <ResultTable color="var(--gold)" headers={['plan', 'cost']} rows={dietResult.rows} />
          )}
        </RoutineCard>

        {/* ── Trigger Demo ──────────────────────────────────────────────── */}
        <RoutineCard
          color="var(--gold-lt)"
          icon="⚡"
          title="Trg_Habitat_Capacity_Log"
          desc="עדכון MaxCapacity מפעיל טריגר שמתעד את השינוי ביומן"
          badge="trigger"
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap', marginBottom: 12 }}>
            <DropSelect items={habitats} value={capHabitatId} onChange={setCapHabitat} placeholder="בחר בית גידול..." />
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <label style={{ fontSize: 13, color: 'var(--text-muted)' }}>קיבולת חדשה:</label>
              <input
                type="number" className="form-input" style={{ width: 90 }}
                value={newCap} onChange={e => setNewCap(Number(e.target.value))} min={1}
              />
            </div>
            <button className="btn btn-gold" onClick={runTrigger} disabled={loading.trigger}>
              {loading.trigger ? <Spinner size={16} /> : '⚡ עדכן'}
            </button>
          </div>
          {triggerResult && (
            <ResultTable
              color="var(--gold-lt)"
              headers={['habitat', 'old', 'new', 'date']}
              rows={triggerResult.log}
            />
          )}
        </RoutineCard>

      </div>
    </div>
  )
}
