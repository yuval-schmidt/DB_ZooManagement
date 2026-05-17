#!/usr/bin/env python3
"""
טעינת נתונים ואובייקטי שלב ד' ל-zoo_db.
הרצה: python seed_database.py
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import psycopg2
from psycopg2 import extras

from config import DB_CONFIG

ROOT = Path(__file__).resolve().parents[2]
STAGE_A = ROOT / "שלב א"
STAGE_C = ROOT / "שלב ג"
STAGE_D = ROOT / "שלב ד"
INTEGRATE_SQL = STAGE_C / "Integrate.sql"

SPECIES_CSV = STAGE_A / "mockarooFiles" / "SPEICES_MOCK_DATA.csv"
DIET_CSV = STAGE_A / "mockarooFiles" / "DIETPLAN_MOCK_DATA.csv"
ANIMAL_CSV = STAGE_A / "DataImportFiles" / "ANIMAL.csv"
HEALTH_CSV = STAGE_A / "DataImportFiles" / "HEALTHRECORD.csv"
FEEDING_CSV = STAGE_A / "mockarooFiles" / "DAILYFEEDING_MOCK_DATA.csv"

PHASE_D_FILES = [
    STAGE_D / "AlterTable.sql",
    STAGE_D / "Function_GetHabitatDietCost.sql",
    STAGE_D / "Function_GetAnimalsByVet.sql",
    STAGE_D / "Procedure_ProcessRoutineCheckups.sql",
    STAGE_D / "Procedure_AdjustDietCost.sql",
    STAGE_D / "Trigger_HabitatCapacityLog.sql",
]

ANIMAL_LIMIT = 2000
HEALTH_LIMIT = 3000
VALID_HEALTH = frozenset({"Healthy", "Sick", "Recovering", "Critical", "Deceased"})


def _read_sql(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _copy_csv(
    cur,
    table: str,
    columns: list[str],
    csv_path: Path,
    csv_columns: list[str] | None = None,
    limit: int | None = None,
):
    if not csv_path.is_file():
        print(f"  דילוג – קובץ לא נמצא: {csv_path.name}")
        return 0
    src_cols = csv_columns or columns
    with csv_path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = []
        for i, row in enumerate(reader):
            if limit is not None and i >= limit:
                break
            values = [row[c] for c in src_cols]
            if table == "dietplan" and len(values) > 1:
                values[1] = str(values[1])[:50]
            if table == "healthrecord":
                if int(values[4]) > ANIMAL_LIMIT:
                    continue
                if values[3] not in VALID_HEALTH:
                    values[3] = "Sick"
            rows.append(values)
    if not rows:
        return 0
    cols = ", ".join(columns)
    extras.execute_values(
        cur,
        f"INSERT INTO {table} ({cols}) VALUES %s",
        rows,
        page_size=1000,
    )
    return len(rows)


def _copy_feeding_csv(cur, limit: int = 2000) -> int:
    """Daily feeding mock file has no header row."""
    if not FEEDING_CSV.is_file():
        return 0
    rows = []
    with FEEDING_CSV.open(encoding="utf-8", newline="") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) != 4:
                continue
            feeding_id, feeding_date, qty, animal_id = parts
            if int(animal_id) > ANIMAL_LIMIT:
                continue
            rows.append([feeding_id, feeding_date, qty, animal_id])
            if len(rows) >= limit:
                break
    if not rows:
        return 0
    extras.execute_values(
        cur,
        "INSERT INTO dailyfeeding (feedingid, feedingdate, foodconsumedqty, animalid) VALUES %s",
        rows,
        page_size=500,
    )
    return len(rows)


def _table_exists(cur, name: str) -> bool:
    cur.execute(
        "SELECT 1 FROM information_schema.tables "
        "WHERE table_schema = 'public' AND table_name = %s",
        (name.lower(),),
    )
    return cur.fetchone() is not None


def install_vet_schema(cur) -> None:
    if _table_exists(cur, "veterinarian"):
        print("  סכמת וטרינריה כבר קיימת")
        return
    if not INTEGRATE_SQL.is_file():
        print("  דילוג – Integrate.sql לא נמצא")
        return
    print("  מתקין Integrate.sql (שלב ג')...")
    cur.execute(_read_sql(INTEGRATE_SQL))


def seed_vet_demo_data(cur) -> None:
    cur.execute("SELECT COUNT(*) FROM veterinarian")
    if cur.fetchone()[0] > 0:
        print("  נתוני וטרינריה כבר קיימים")
        return
    print("  טוען נתוני דמו לווטרינריה...")
    vets = [
        (1, "דנה", "כהן", "VET-1001", "כירורגיה", "2018-03-15"),
        (2, "יוסי", "לוי", "VET-1002", "רפואה פנימית", "2019-07-01"),
        (3, "מיה", "ברק", "VET-1003", "דגים וזוחלים", "2020-11-20"),
    ]
    extras.execute_values(
        cur,
        "INSERT INTO veterinarian (vetid, firstname, lastname, licensenumber, specialization, hiredate) VALUES %s",
        vets,
    )
    visits = [
        (1, "2024-01-10", "בדיקה שגרתית", "בדיקה תקינה", 120.00, 1, 1),
        (2, "2024-02-05", "פציעה ברגל", "חבישה והחלמה", 350.00, 2, 1),
        (3, "2024-03-12", "חיסון שנתי", "חיסון הושלם", 80.00, 3, 2),
        (4, "2024-04-20", "אובדן תיאבון", "מעקב תזונה", 200.00, 10, 2),
        (5, "2024-05-08", "בדיקת שיניים", "ניקוי שיניים", 150.00, 25, 3),
        (6, "2024-06-01", "בעיית עור", "טיפול מקומי", 95.00, 50, 3),
    ]
    extras.execute_values(
        cur,
        """INSERT INTO medicalvisit
           (visitid, visitdate, reason, summary, cost, animalid, vetid) VALUES %s""",
        visits,
    )


def install_phase_d(cur) -> None:
    for path in PHASE_D_FILES:
        if not path.is_file():
            print(f"  דילוג – {path.name}")
            continue
        print(f"  מתקין {path.name}...")
        cur.execute(_read_sql(path))


def main() -> int:
    print(f"מתחבר ל-{DB_CONFIG['dbname']} @ {DB_CONFIG['host']}...")
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            print("מנקה טבלאות נתונים (שומר habitat)...")
            cur.execute(
                "TRUNCATE TABLE dailyfeeding, healthrecord, animal, dietplan, species "
                "RESTART IDENTITY CASCADE"
            )

            print("טוען species...")
            n = _copy_csv(
                cur, "species",
                ["speciesid", "commonname", "scientificname", "conservationstatus"],
                SPECIES_CSV,
                ["SpeciesID", "CommonName", "ScientificName", "ConservationStatus"],
            )
            print(f"  {n} מינים")

            print("טוען dietplan...")
            n = _copy_csv(
                cur, "dietplan",
                ["dietplanid", "planname", "dailycost"],
                DIET_CSV,
                ["DietPlanID", "PlanName", "DailyCost"],
            )
            print(f"  {n} תוכניות תזונה")

            print(f"טוען animals (עד {ANIMAL_LIMIT})...")
            n = _copy_csv(
                cur, "animal",
                ["animalid", "name", "dateofbirth", "gender", "habitatid", "speciesid", "dietplanid"],
                ANIMAL_CSV,
                ["AnimalID", "Name", "DateOfBirth", "Gender", "HabitatID", "SpeciesID", "DietPlanID"],
                limit=ANIMAL_LIMIT,
            )
            print(f"  {n} חיות")

            print(f"טוען healthrecord (עד {HEALTH_LIMIT})...")
            n = _copy_csv(
                cur, "healthrecord",
                ["recordid", "checkupdate", "weight", "healthstatus", "animalid"],
                HEALTH_CSV,
                ["RecordID", "CheckupDate", "Weight", "HealthStatus", "AnimalID"],
                limit=HEALTH_LIMIT,
            )
            print(f"  {n} רשומות בריאות")

            print("טוען dailyfeeding...")
            n = _copy_feeding_csv(cur)
            print(f"  {n} רשומות האכלה")

            print("מתקין מחלקה וטרינרית (שלב ג')...")
            install_vet_schema(cur)
            seed_vet_demo_data(cur)

            print("מתקין פונקציות/פרוצדורות/triggers שלב ד'...")
            install_phase_d(cur)

        conn.commit()
        print("\nהושלם בהצלחה.")
        with conn.cursor() as cur:
            for t in (
                "habitat", "species", "animal", "healthrecord", "dailyfeeding",
                "veterinarian", "medicalvisit",
            ):
                if _table_exists(cur, t):
                    cur.execute(f"SELECT COUNT(*) FROM {t}")
                    print(f"  {t}: {cur.fetchone()[0]}")
        return 0
    except Exception as exc:
        conn.rollback()
        print(f"\nשגיאה: {exc}", file=sys.stderr)
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
