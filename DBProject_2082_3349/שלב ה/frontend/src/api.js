// Centralised API client – all calls go through /api (proxied to :8000)
const BASE = '/api'

async function req(method, path, body) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
  }
  if (body !== undefined) opts.body = JSON.stringify(body)
  const res = await fetch(BASE + path, opts)
  if (!res.ok) {
    let detail = `HTTP ${res.status}`
    try { const j = await res.json(); detail = j.detail || detail } catch {}
    throw new Error(detail)
  }
  return res.json()
}

export const api = {
  // Stats
  stats: () => req('GET', '/stats'),

  // Tables meta
  tablesList:  () => req('GET', '/tables'),
  tableMeta:   (key) => req('GET', `/tables/${key}/meta`),
  tableRows:   (key) => req('GET', `/tables/${key}/rows`),
  tableRow:    (key, pk) => req('GET', `/tables/${key}/row/${pk}`),
  fkOptions:   (key, col) => req('GET', `/tables/${key}/fk/${col}`),
  insertRow:   (key, data) => req('POST', `/tables/${key}`, { data }),
  updateRow:   (key, pk, data) => req('PUT', `/tables/${key}/${pk}`, { data }),
  deleteRow:   (key, pk) => req('DELETE', `/tables/${key}/${pk}`),

  // Queries
  queriesList: () => req('GET', '/queries'),
  runQuery:    (key) => req('POST', `/queries/${key}`),

  // Routines
  habitats:    () => req('GET', '/routines/habitats'),
  vets:        () => req('GET', '/routines/vets'),
  species:     () => req('GET', '/routines/species'),
  habitatCost: (habitatId) => req('POST', '/routines/habitat-cost', { habitatId }),
  animalsByVet: (vetId) => req('POST', '/routines/animals-by-vet', { vetId }),
  checkups:    () => req('POST', '/routines/checkups'),
  adjustDiet:  (speciesId, percent) => req('POST', '/routines/adjust-diet', { speciesId, percent }),
  triggerDemo: (habitatId, newCapacity) => req('POST', '/routines/trigger-demo', { habitatId, newCapacity }),
}
