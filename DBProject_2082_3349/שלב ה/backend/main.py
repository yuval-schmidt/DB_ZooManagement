"""FastAPI backend – Zoo Management REST API."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import psycopg2
from config import DB_CONFIG
from database import (
    DatabaseError, call_function, call_procedure_refcursor,
    execute, fetch_all, fetch_one, get_existing_tables, next_id,
)
from queries_data import PHASE_B_QUERIES
from table_metadata import (
    TABLE_GROUPS, TABLES, all_editable_columns, build_select_sql, pk_labels,
)

app = FastAPI(title="Zoo Management API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Helper ────────────────────────────────────────────────────────────────────
def _db_err(exc: DatabaseError):
    raise HTTPException(status_code=500, detail=str(exc))


# ═══════════════════════════════════════════════════════════════════════════════
# STATS
# ═══════════════════════════════════════════════════════════════════════════════
@app.get("/api/stats")
def get_stats():
    existing = get_existing_tables()
    counts = {}
    tables_to_count = [
        ("animal", "animals"),
        ("veterinarian", "vets"),
        ("employee", "employees"),
        ("medicalvisit", "visits"),
        ("habitat", "habitats"),
        ("species", "species"),
        ("treatment", "treatments"),
        ("medication", "medications"),
    ]
    for tbl, key in tables_to_count:
        if tbl in existing:
            try:
                row = fetch_one(f"SELECT COUNT(*) FROM {tbl}")
                counts[key] = int(row[0]) if row else 0
            except DatabaseError:
                counts[key] = 0
        else:
            counts[key] = 0

    # Animals per habitat (for chart)
    animals_per_habitat = []
    if "habitat" in existing and "animal" in existing:
        try:
            rows = fetch_all("""
                SELECT h.habitatname, COUNT(a.animalid) as count
                FROM habitat h
                LEFT JOIN animal a ON h.habitatid = a.habitatid
                GROUP BY h.habitatname ORDER BY count DESC LIMIT 8
            """)
            animals_per_habitat = [{"name": r[0], "count": int(r[1])} for r in rows]
        except DatabaseError:
            pass

    # Recent health records
    recent_health = []
    if "healthrecord" in existing and "animal" in existing:
        try:
            rows = fetch_all("""
                SELECT a.name, hr.healthstatus, hr.checkupdate, hr.weight
                FROM healthrecord hr
                JOIN animal a ON hr.animalid = a.animalid
                ORDER BY hr.checkupdate DESC LIMIT 6
            """)
            recent_health = [
                {"animal": r[0], "status": r[1],
                 "date": str(r[2]), "weight": float(r[3]) if r[3] else None}
                for r in rows
            ]
        except DatabaseError:
            pass

    return {"counts": counts, "animalsPerHabitat": animals_per_habitat, "recentHealth": recent_health}


# ═══════════════════════════════════════════════════════════════════════════════
# TABLES META
# ═══════════════════════════════════════════════════════════════════════════════
@app.get("/api/tables")
def get_tables_list():
    existing = get_existing_tables()
    result = {}
    for group, keys in TABLE_GROUPS.items():
        group_tables = []
        for k in keys:
            tdef = TABLES[k]
            if tdef.table.lower() in existing:
                group_tables.append({
                    "key": k,
                    "table": tdef.table,
                    "displayName": tdef.display_name,
                    "readOnly": tdef.read_only,
                    "pk": tdef.pk,
                })
        if group_tables:
            result[group] = group_tables
    return result


@app.get("/api/tables/{table_key}/meta")
def get_table_meta(table_key: str):
    tdef = TABLES.get(table_key)
    if not tdef:
        raise HTTPException(404, f"Table '{table_key}' not found")
    cols = []
    for col in tdef.columns:
        cols.append({
            "name": col.name, "label": col.label,
            "type": col.field_type, "choices": col.choices,
        })
    fks = []
    for fk in tdef.foreign_keys:
        fks.append({
            "column": fk.column, "refTable": fk.ref_table,
            "refPk": fk.ref_pk, "label": fk.grid_label,
        })
    pklabels = pk_labels(tdef)
    return {
        "key": table_key, "table": tdef.table,
        "displayName": tdef.display_name,
        "pk": tdef.pk, "pkLabels": pklabels,
        "columns": cols, "foreignKeys": fks,
        "readOnly": tdef.read_only,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# ROWS (READ)
# ═══════════════════════════════════════════════════════════════════════════════
@app.get("/api/tables/{table_key}/rows")
def get_rows(table_key: str):
    tdef = TABLES.get(table_key)
    if not tdef:
        raise HTTPException(404, f"Table '{table_key}' not found")
    try:
        sql, headers = build_select_sql(tdef)
        rows = fetch_all(sql)
    except DatabaseError as exc:
        _db_err(exc)

    pk_count = len(tdef.pk)
    result = []
    for row in rows:
        pk_vals = row[:pk_count]
        display_vals = row[pk_count:]
        record: dict[str, Any] = {}
        for i, pk in enumerate(tdef.pk):
            record[f"__pk_{pk}"] = pk_vals[i]
        for header, val in zip(headers, display_vals):
            record[header] = None if val is None else str(val)
        result.append(record)
    return {"headers": headers, "rows": result, "pkColumns": tdef.pk}


# ═══════════════════════════════════════════════════════════════════════════════
# FK OPTIONS
# ═══════════════════════════════════════════════════════════════════════════════
@app.get("/api/tables/{table_key}/fk/{column}")
def get_fk_options(table_key: str, column: str):
    tdef = TABLES.get(table_key)
    if not tdef:
        raise HTTPException(404)
    fk = next((f for f in tdef.foreign_keys if f.column == column), None)
    if not fk:
        raise HTTPException(404, f"FK column '{column}' not found")

    ref = fk.ref_table.lower()
    sql_map = {
        "activity": "SELECT activityid, activityid::text || ' – ' || activitydate::text FROM activity ORDER BY activityid",
        "medicalvisit": "SELECT visitid, visitid::text || ' – ' || reason FROM medicalvisit ORDER BY visitid",
        "veterinarian": "SELECT vetid, firstname || ' ' || lastname FROM veterinarian ORDER BY 2",
        "employee": "SELECT employeeid, firstname || ' ' || lastname FROM employee ORDER BY 2",
    }
    sql = sql_map.get(ref, f"SELECT {fk.ref_pk}, {fk.display_sql} AS lbl FROM {ref} ORDER BY 2")
    try:
        rows = fetch_all(sql)
        return [{"id": int(r[0]), "label": str(r[1])} for r in rows]
    except DatabaseError as exc:
        _db_err(exc)


# ═══════════════════════════════════════════════════════════════════════════════
# INSERT
# ═══════════════════════════════════════════════════════════════════════════════
class RowPayload(BaseModel):
    data: dict[str, Any]


@app.post("/api/tables/{table_key}", status_code=201)
def insert_row(table_key: str, payload: RowPayload):
    tdef = TABLES.get(table_key)
    if not tdef:
        raise HTTPException(404)
    data = payload.data.copy()

    # Auto-generate PK if single int PK
    if len(tdef.pk) == 1:
        pk = tdef.pk[0]
        if pk not in data and pk != "logid":
            try:
                data[pk] = next_id(tdef.table, pk)
            except DatabaseError as exc:
                _db_err(exc)

    cols = list(data.keys())
    vals = list(data.values())
    sql = (f"INSERT INTO {tdef.table} ({', '.join(cols)}) "
           f"VALUES ({', '.join(['%s'] * len(vals))})")
    try:
        execute(sql, tuple(vals))
        return {"ok": True, "message": "הרשומה נוספה בהצלחה"}
    except DatabaseError as exc:
        raise HTTPException(400, detail=str(exc))


# ═══════════════════════════════════════════════════════════════════════════════
# UPDATE
# ═══════════════════════════════════════════════════════════════════════════════
@app.put("/api/tables/{table_key}/{pk_value}")
def update_row(table_key: str, pk_value: str, payload: RowPayload):
    tdef = TABLES.get(table_key)
    if not tdef:
        raise HTTPException(404)
    data = payload.data.copy()
    # Support composite PK via comma-separated values
    pk_vals = pk_value.split(",")
    if len(pk_vals) != len(tdef.pk):
        raise HTTPException(400, "PK count mismatch")

    conditions = [f"{pk} = %s" for pk in tdef.pk]
    pk_params = [int(v) if v.isdigit() else v for v in pk_vals]
    set_parts = [f"{k} = %s" for k in data]
    vals = list(data.values()) + pk_params
    sql = (f"UPDATE {tdef.table} SET {', '.join(set_parts)} "
           f"WHERE {' AND '.join(conditions)}")
    try:
        n = execute(sql, tuple(vals))
        if n == 0:
            raise HTTPException(404, "רשומה לא נמצאה")
        return {"ok": True, "message": "הרשומה עודכנה"}
    except DatabaseError as exc:
        raise HTTPException(400, detail=str(exc))


# ═══════════════════════════════════════════════════════════════════════════════
# LOAD ONE ROW (for update form)
# ═══════════════════════════════════════════════════════════════════════════════
@app.get("/api/tables/{table_key}/row/{pk_value}")
def get_one_row(table_key: str, pk_value: str):
    tdef = TABLES.get(table_key)
    if not tdef:
        raise HTTPException(404)
    pk_vals = pk_value.split(",")
    conditions = [f"{pk} = %s" for pk in tdef.pk]
    params = [int(v) if v.isdigit() else v for v in pk_vals]
    sel = ", ".join([c.name for c in tdef.columns] + [f.column for f in tdef.foreign_keys])
    try:
        row = fetch_one(
            f"SELECT {sel} FROM {tdef.table} WHERE {' AND '.join(conditions)}",
            tuple(params),
        )
    except DatabaseError as exc:
        _db_err(exc)
    if not row:
        raise HTTPException(404, "רשומה לא נמצאה")

    result: dict[str, Any] = {}
    idx = 0
    for col in tdef.columns:
        result[col.name] = None if row[idx] is None else str(row[idx])
        idx += 1
    for fk in tdef.foreign_keys:
        result[fk.column] = None if row[idx] is None else str(row[idx])
        idx += 1
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# DELETE
# ═══════════════════════════════════════════════════════════════════════════════
@app.delete("/api/tables/{table_key}/{pk_value}")
def delete_row(table_key: str, pk_value: str):
    tdef = TABLES.get(table_key)
    if not tdef:
        raise HTTPException(404)
    pk_vals = pk_value.split(",")
    conditions = [f"{pk} = %s" for pk in tdef.pk]
    params = [int(v) if v.isdigit() else v for v in pk_vals]
    sql = f"DELETE FROM {tdef.table} WHERE {' AND '.join(conditions)}"
    try:
        n = execute(sql, tuple(params))
        if n == 0:
            raise HTTPException(404, "רשומה לא נמצאה")
        return {"ok": True, "message": "הרשומה נמחקה"}
    except DatabaseError as exc:
        raise HTTPException(400, detail=str(exc))


# ═══════════════════════════════════════════════════════════════════════════════
# QUERIES (Phase B)
# ═══════════════════════════════════════════════════════════════════════════════
@app.get("/api/queries")
def list_queries():
    return [
        {"key": k, "title": v["title"], "description": v["description"]}
        for k, v in PHASE_B_QUERIES.items()
    ]


_QUERY_HEADERS = {
    "food_by_species":          ["שם נפוץ", "שם מדעי", "סך מזון שנצרך"],
    "habitat_missing_checkups": ["שם בית גידול", "סוג אקלים", "מספר חיות"],
    "diet_cost_april":          ["שם נפוץ", "שם מדעי", "סך עלות תזונה"],
    "weight_december":          ["שם בית גידול", "סוג אקלים", "סך משקל"],
}


@app.post("/api/queries/{key}")
def run_query(key: str):
    q = PHASE_B_QUERIES.get(key)
    if not q:
        raise HTTPException(404)
    try:
        rows = fetch_all(q["sql"])
        headers = _QUERY_HEADERS.get(key, [f"עמודה {i+1}" for i in range(len(rows[0]) if rows else 0)])
        return {
            "headers": headers,
            "rows": [[str(v) if v is not None else "" for v in row] for row in rows],
            "count": len(rows),
        }
    except DatabaseError as exc:
        raise HTTPException(500, detail=str(exc))


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTINES (Phase D)
# ═══════════════════════════════════════════════════════════════════════════════

# -- Dropdowns ----------------------------------------------------------------
@app.get("/api/routines/habitats")
def get_habitats():
    try:
        rows = fetch_all("SELECT habitatid, habitatname FROM habitat ORDER BY habitatname")
        return [{"id": int(r[0]), "name": str(r[1])} for r in rows]
    except DatabaseError as exc:
        _db_err(exc)


@app.get("/api/routines/vets")
def get_vets():
    try:
        rows = fetch_all("SELECT vetid, firstname || ' ' || lastname FROM veterinarian ORDER BY 2")
        return [{"id": int(r[0]), "name": str(r[1])} for r in rows]
    except DatabaseError as exc:
        _db_err(exc)


@app.get("/api/routines/species")
def get_species():
    try:
        rows = fetch_all("SELECT speciesid, commonname FROM species ORDER BY commonname")
        return [{"id": int(r[0]), "name": str(r[1])} for r in rows]
    except DatabaseError as exc:
        _db_err(exc)


# -- Function: habitat cost ---------------------------------------------------
class HabitatCostReq(BaseModel):
    habitatId: int


@app.post("/api/routines/habitat-cost")
def routine_habitat_cost(req: HabitatCostReq):
    try:
        result = call_function("SELECT get_habitat_diet_cost(%s)", (req.habitatId,))
        cost = float(result) if result else 0.0
        return {"cost": cost, "formatted": f"₪ {cost:.2f}"}
    except DatabaseError as exc:
        raise HTTPException(500, detail=str(exc))


# -- Function: animals by vet --------------------------------------------------
class VetReq(BaseModel):
    vetId: int


@app.post("/api/routines/animals-by-vet")
def routine_animals_by_vet(req: VetReq):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False
        with conn.cursor() as cur:
            cur.execute("SELECT get_animals_by_vet_refcursor(%s)", (req.vetId,))
            cursor_name = cur.fetchone()[0]
            cur.execute(f'FETCH ALL IN "{cursor_name}"')
            rows = cur.fetchall()
        conn.commit()
        conn.close()
        display = [
            {"animal": r[1], "birthdate": str(r[2]),
             "visitdate": str(r[3]), "reason": str(r[4])}
            for r in rows
        ]
        return {"rows": display, "count": len(display)}
    except (psycopg2.Error, DatabaseError) as exc:
        raise HTTPException(500, detail=str(exc))


# -- Procedure: routine checkups -----------------------------------------------
@app.post("/api/routines/checkups")
def routine_checkups():
    try:
        raw = call_procedure_refcursor("process_routine_checkups", ())
        # Fetch animal names
        animal_ids = [int(r[4]) for r in raw if r[4] is not None]
        name_map: dict[int, str] = {}
        if animal_ids:
            name_rows = fetch_all(
                "SELECT animalid, name FROM animal WHERE animalid = ANY(%s)",
                (list(set(animal_ids)),),
            )
            name_map = {int(r[0]): str(r[1]) for r in name_rows}
        display = [
            {"date": str(r[1]), "weight": str(r[2]),
             "status": str(r[3]), "animal": name_map.get(int(r[4]), str(r[4]))}
            for r in raw
        ]
        return {"rows": display, "created": len(display)}
    except DatabaseError as exc:
        raise HTTPException(500, detail=str(exc))


# -- Procedure: adjust diet cost -----------------------------------------------
class AdjustDietReq(BaseModel):
    speciesId: int
    percent: float


@app.post("/api/routines/adjust-diet")
def routine_adjust_diet(req: AdjustDietReq):
    try:
        raw = call_procedure_refcursor("adjust_diet_cost_by_species", (req.speciesId, req.percent))
        display = [
            {"plan": str(r[2]), "cost": f"₪ {float(r[1]):.2f}"}
            for r in raw
        ]
        return {"rows": display, "updated": len(display)}
    except DatabaseError as exc:
        raise HTTPException(500, detail=str(exc))


# -- Trigger demo: update capacity --------------------------------------------
class TriggerDemoReq(BaseModel):
    habitatId: int
    newCapacity: int


@app.post("/api/routines/trigger-demo")
def routine_trigger_demo(req: TriggerDemoReq):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            cur.execute("UPDATE habitat SET maxcapacity = %s WHERE habitatid = %s",
                        (req.newCapacity, req.habitatId))
            cur.execute("""
                SELECT h.habitatname, l.oldcapacity, l.newcapacity, l.changedate
                FROM habitat_capacity_log l
                JOIN habitat h ON l.habitatid = h.habitatid
                WHERE l.habitatid = %s ORDER BY l.changedate DESC LIMIT 5
            """, (req.habitatId,))
            rows = cur.fetchall()
        conn.commit()
        conn.close()
        log = [
            {"habitat": r[0], "old": r[1], "new": r[2], "date": str(r[3])}
            for r in rows
        ]
        return {"log": log}
    except psycopg2.Error as exc:
        raise HTTPException(500, detail=str(exc))
