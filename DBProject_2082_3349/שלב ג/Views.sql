-- ====================================================================================
-- 1. View from the perspective of the original department (Animal and Diet Management)
-- ====================================================================================
CREATE OR REPLACE VIEW View_Zoo_Animal_Status AS
SELECT A.AnimalID, A.Name AS AnimalName, S.CommonName AS Species, H.HabitatName, DP.PlanName AS DietPlan, HR.HealthStatus, HR.CheckupDate
FROM ANIMAL A
JOIN SPECIES S ON A.SpeciesID = S.SpeciesID
JOIN HABITAT H ON A.HabitatID = H.HabitatID
JOIN DIETPLAN DP ON A.DietPlanID = DP.DietPlanID
LEFT JOIN HEALTHRECORD HR ON A.AnimalID = HR.AnimalID;

-- Query 1.1: Display animals that are not in a "Healthy" health status
SELECT * FROM View_Zoo_Animal_Status WHERE HealthStatus <> 'Healthy';

-- Query 1.2: Count the number of animals in each habitat via the view
SELECT HabitatName, COUNT(AnimalID) as AnimalCount FROM View_Zoo_Animal_Status GROUP BY HabitatName;

-- ====================================================================================
-- 2. View from the perspective of the new department (Veterinary Clinic)
-- ====================================================================================
CREATE OR REPLACE VIEW View_Vet_Clinic_Activity AS
SELECT V.VetID, V.LastName AS VetName, V.Specialization, MV.VisitDate, MV.Reason, T.Description AS TreatmentDesc, T.Severity
FROM VETERINARIAN V
JOIN MEDICALVISIT MV ON V.VetID = MV.VetID
JOIN MIRSHAM_VISIT_TREATMENT MVT ON MV.VisitID = MVT.VisitID
JOIN TREATMENT T ON MVT.TreatmentID = T.TreatmentID;

-- Query 2.1: Display all clinic activities with Severity 'Medium' or higher
SELECT * FROM View_Vet_Clinic_Activity WHERE Severity IN ('Medium', 'High', 'Critical');

-- Query 2.2: Number of treatments performed by each veterinarian
SELECT VetName, COUNT(TreatmentDesc) AS TreatmentsCount FROM View_Vet_Clinic_Activity GROUP BY VetName;

-- ====================================================================================
-- 3. Integrated view - The original department and the new department together
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

-- Query 3.1: Display the complete medical profile for a specific animal (e.g., AnimalID = 1)
SELECT * FROM View_Integrated_Animal_Medical WHERE AnimalID = 1;

-- Query 3.2: List of all vaccinations ever given in the zoo
SELECT AnimalName, VisitDate, Vaccination FROM View_Integrated_Animal_Medical WHERE Vaccination IS NOT NULL;
