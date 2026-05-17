"""Phase B queries and Phase D routines exposed in the GUI."""

PHASE_B_QUERIES = {
    "food_by_species": {
        "title": "סך מזון לפי מין – חיות שנולדו אחרי 2020",
        "description": "שאילתה כפולה (JOIN) – שלב ב'",
        "sql": """
            SELECT S.CommonName, S.ScientificName, SUM(DF.FoodConsumedQty) AS TotalFoodConsumed
            FROM SPECIES S
            JOIN ANIMAL A ON S.SpeciesID = A.SpeciesID
            JOIN DAILYFEEDING DF ON A.AnimalID = DF.AnimalID
            WHERE EXTRACT(YEAR FROM A.DateOfBirth) > 2020
            GROUP BY S.CommonName, S.ScientificName
            ORDER BY TotalFoodConsumed DESC
            LIMIT 100
        """,
    },
    "habitat_missing_checkups": {
        "title": "בתי גידול ללא בדיקות השנה",
        "description": "שאילתה כפולה (NOT EXISTS) – שלב ב'",
        "sql": """
            SELECT H.HabitatName, H.ClimateType, COUNT(A.AnimalID) AS AnimalCount
            FROM HABITAT H
            JOIN ANIMAL A ON H.HabitatID = A.HabitatID
            WHERE NOT EXISTS (
                SELECT 1 FROM ANIMAL A2
                JOIN HEALTHRECORD HR ON A2.AnimalID = HR.AnimalID
                WHERE A2.HabitatID = H.HabitatID
                  AND EXTRACT(YEAR FROM HR.CheckupDate) = EXTRACT(YEAR FROM CURRENT_DATE)
            )
            GROUP BY H.HabitatName, H.ClimateType
            ORDER BY AnimalCount DESC
            LIMIT 100
        """,
    },
    "diet_cost_april": {
        "title": "עלות תזונה יומית לפי מין – בדיקות באפריל",
        "description": "שאילתה רגילה – שלב ב'",
        "sql": """
            SELECT S.CommonName, S.ScientificName, SUM(D.DailyCost) AS TotalSpeciesDietCost
            FROM SPECIES S
            JOIN ANIMAL A ON S.SpeciesID = A.SpeciesID
            JOIN DIETPLAN D ON A.DietPlanID = D.DietPlanID
            JOIN HEALTHRECORD HR ON A.AnimalID = HR.AnimalID
            WHERE EXTRACT(MONTH FROM HR.CheckupDate) = 4
            GROUP BY S.CommonName, S.ScientificName
            ORDER BY TotalSpeciesDietCost DESC
            LIMIT 100
        """,
    },
    "weight_december": {
        "title": "סך משקל בדיקות בדצמבר לפי בית גידול",
        "description": "שאילתה רגילה – שלב ב'",
        "sql": """
            SELECT H.HabitatName, H.ClimateType, SUM(HR.Weight) AS TotalWeightRecorded
            FROM HABITAT H
            JOIN ANIMAL A ON H.HabitatID = A.HabitatID
            JOIN HEALTHRECORD HR ON A.AnimalID = HR.AnimalID
            WHERE EXTRACT(MONTH FROM HR.CheckupDate) = 12
            GROUP BY H.HabitatName, H.ClimateType
            ORDER BY TotalWeightRecorded DESC
            LIMIT 100
        """,
    },
}
