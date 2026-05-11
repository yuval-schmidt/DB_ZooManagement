-- Views.sql
-- מבטים ושאילתות לשלב ג'

-- ====================================================================================
-- 1. מבט מנקודת המבט של האגף המקורי (ניהול בעלי חיים ותזונה)
-- ====================================================================================
CREATE OR REPLACE VIEW View_Zoo_Animal_Status AS
SELECT A.AnimalID, A.Name AS AnimalName, S.CommonName AS Species, H.HabitatName, DP.PlanName AS DietPlan, HR.HealthStatus, HR.CheckupDate
FROM ANIMAL A
JOIN SPECIES S ON A.SpeciesID = S.SpeciesID
JOIN HABITAT H ON A.HabitatID = H.HabitatID
JOIN DIETPLAN DP ON A.DietPlanID = DP.DietPlanID
LEFT JOIN HEALTHRECORD HR ON A.AnimalID = HR.AnimalID;

-- שאילתה 1.1: הצגת חיות שאינן במצב בריאותי "Healthy"
SELECT * FROM View_Zoo_Animal_Status WHERE HealthStatus <> 'Healthy';

-- שאילתה 1.2: ספירת כמות החיות בכל אזור מחיה דרך המבט
SELECT HabitatName, COUNT(AnimalID) as AnimalCount FROM View_Zoo_Animal_Status GROUP BY HabitatName;

-- ====================================================================================
-- 2. מבט מנקודת המבט של האגף החדש (מרפאה ווטרינרית)
-- ====================================================================================
CREATE OR REPLACE VIEW View_Vet_Clinic_Activity AS
SELECT V.VetID, V.LastName AS VetName, V.Specialization, MV.VisitDate, MV.Reason, T.Description AS TreatmentDesc, T.Severity
FROM VETERINARIAN V
JOIN MEDICALVISIT MV ON V.VetID = MV.VetID
JOIN MIRSHAM_VISIT_TREATMENT MVT ON MV.VisitID = MVT.VisitID
JOIN TREATMENT T ON MVT.TreatmentID = T.TreatmentID;

-- שאילתה 2.1: הצגת כל פעילויות המרפאה בדרגות חומרה Medium ומעלה
SELECT * FROM View_Vet_Clinic_Activity WHERE Severity IN ('Medium', 'High', 'Critical');

-- שאילתה 2.2: מספר הטיפולים שבוצעו על ידי כל ווטרינר
SELECT VetName, COUNT(TreatmentDesc) AS TreatmentsCount FROM View_Vet_Clinic_Activity GROUP BY VetName;

-- ====================================================================================
-- 3. מבט משולב - האגף המקורי והאגף החדש יחד
-- ====================================================================================
CREATE OR REPLACE VIEW View_Integrated_Animal_Medical AS
SELECT A.AnimalID, A.Name AS AnimalName, A.DateOfBirth, 
       V.LastName AS TreatingVet, MV.VisitDate, MV.Reason, T.Type AS TreatmentType,
       MED.CommercialName AS Medication, VAC.Name AS Vaccination
FROM ANIMAL A
JOIN MEDICALVISIT MV ON A.AnimalID = MV.AnimalID
JOIN VETERINARIAN V ON MV.VetID = V.VetID
LEFT JOIN MIRSHAM_VISIT_TREATMENT MVT ON MV.VisitID = MVT.VisitID
LEFT JOIN TREATMENT T ON MVT.TreatmentID = T.TreatmentID
LEFT JOIN HERGEL_TREATMENT_MEDICATION HTM ON T.TreatmentID = HTM.TreatmentID
LEFT JOIN MEDICATION MED ON HTM.MedID = MED.MedID
LEFT JOIN TREATMENT_VACCINATION TV ON T.TreatmentID = TV.TreatmentID
LEFT JOIN VACCINATION VAC ON TV.VacID = VAC.VacID;

-- שאילתה 3.1: הצגת הפרופיל הרפואי המלא עבור חיה ספציפית (לדוגמה AnimalID = 1)
SELECT * FROM View_Integrated_Animal_Medical WHERE AnimalID = 1;

-- שאילתה 3.2: רשימת כל החיסונים שניתנו אי פעם בגן החיות
SELECT AnimalName, VisitDate, Vaccination FROM View_Integrated_Animal_Medical WHERE Vaccination IS NOT NULL;
