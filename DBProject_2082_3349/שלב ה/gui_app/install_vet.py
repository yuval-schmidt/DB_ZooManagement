#!/usr/bin/env python3
"""התקנת מחלקה וטרינרית + פונקציה Get_Animals_By_Vet (ללא מחיקת נתונים קיימים)."""
import sys

import psycopg2

from config import DB_CONFIG
from seed_database import install_phase_d, install_vet_schema, seed_vet_demo_data

VET_FUNCTION_ONLY = [
    __import__("pathlib").Path(__file__).resolve().parents[2]
    / "שלב ד"
    / "Function_GetAnimalsByVet.sql",
]


def main() -> int:
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            install_vet_schema(cur)
            seed_vet_demo_data(cur)
            if VET_FUNCTION_ONLY[0].is_file():
                print("מתקין Function_GetAnimalsByVet.sql...")
                cur.execute(VET_FUNCTION_ONLY[0].read_text(encoding="utf-8"))
        conn.commit()
        print("הושלם – ניתן לפתוח את מסך הווטרינר בממשק.")
        return 0
    except Exception as exc:
        conn.rollback()
        print(f"שגיאה: {exc}", file=sys.stderr)
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
