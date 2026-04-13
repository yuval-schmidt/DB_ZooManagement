-- Double Query 1: Find the animals and their species details that live in the 'Tropical Rain' climate.
-- Version A: JOIN
SELECT A.Name, S.CommonName, S.ScientificName
FROM ANIMAL A
JOIN HABITAT H ON A.HabitatID = H.HabitatID
JOIN SPECIES S ON A.SpeciesID = S.SpeciesID
WHERE H.ClimateType = 'Tropical Rain';

-- Version B: IN Subquery
SELECT A.Name, S.CommonName, S.ScientificName
FROM ANIMAL A
JOIN SPECIES S ON A.SpeciesID = S.SpeciesID
WHERE A.HabitatID IN (
    SELECT HabitatID 
    FROM HABITAT 
    WHERE ClimateType = 'Tropical Rain'
);

-- -----------------------------------------------------------------------------
-- Double Query 2: Find diet plans that are currently not assigned to any living animal.
-- Version A: NOT IN
SELECT * FROM DIETPLAN
WHERE DietPlanID NOT IN (
    SELECT DietPlanID 
    FROM ANIMAL 
    WHERE DietPlanID IS NOT NULL
);

-- Version B: NOT EXISTS
SELECT * FROM DIETPLAN D
WHERE NOT EXISTS (
    SELECT 1 
    FROM ANIMAL A 
    WHERE A.DietPlanID = D.DietPlanID
);

-- -----------------------------------------------------------------------------
-- Double Query 3: Find the total daily food consumption cost per habitat.
-- Version A: GROUP BY with JOIN
SELECT H.HabitatName, SUM(D.DailyCost) AS TotalDailyCost
FROM HABITAT H
JOIN ANIMAL A ON H.HabitatID = A.HabitatID
JOIN DIETPLAN D ON A.DietPlanID = D.DietPlanID
GROUP BY H.HabitatName;

-- Version B: Subquery in SELECT
SELECT H.HabitatName,
    (SELECT COALESCE(SUM(D.DailyCost), 0)
     FROM ANIMAL A
     JOIN DIETPLAN D ON A.DietPlanID = D.DietPlanID
     WHERE A.HabitatID = H.HabitatID) AS TotalDailyCost
FROM HABITAT H;

-- -----------------------------------------------------------------------------
-- Double Query 4: Get the latest health checkup date and weight for each animal.
-- Version A: Window Function
WITH RankedRecords AS (
    SELECT AnimalID, CheckupDate, Weight,
           ROW_NUMBER() OVER(PARTITION BY AnimalID ORDER BY CheckupDate DESC) as rn
    FROM HEALTHRECORD
)
SELECT AnimalID, CheckupDate, Weight
FROM RankedRecords
WHERE rn = 1;

-- Version B: Subquery
SELECT H.AnimalID, H.CheckupDate, H.Weight
FROM HEALTHRECORD H
WHERE H.CheckupDate = (
    SELECT MAX(CheckupDate)
    FROM HEALTHRECORD H2
    WHERE H.AnimalID = H2.AnimalID
);

-- -----------------------------------------------------------------------------
-- Regular Query 1: Extract animals born in the last 2 years 
SELECT * FROM ANIMAL 
WHERE DateOfBirth >= CURRENT_DATE - INTERVAL '2 years';

-- -----------------------------------------------------------------------------
-- Regular Query 2: Find the most populated habitat comparing COUNT to MaxCapacity.
SELECT H.HabitatName, COUNT(A.AnimalID) AS CurrentPopulation, H.MaxCapacity
FROM HABITAT H
JOIN ANIMAL A ON H.HabitatID = A.HabitatID
GROUP BY H.HabitatID, H.HabitatName, H.MaxCapacity
ORDER BY CurrentPopulation DESC
LIMIT 1;

-- -----------------------------------------------------------------------------
-- Regular Query 3: List the top 3 most expensive animals to feed per day based on their diet plan.
SELECT A.Name, D.PlanName, D.DailyCost
FROM ANIMAL A
JOIN DIETPLAN D ON A.DietPlanID = D.DietPlanID
ORDER BY D.DailyCost DESC
LIMIT 3;

-- -----------------------------------------------------------------------------
-- Regular Query 4: Find the average food consumption quantity by animal gender in the year 2025.
SELECT A.Gender, AVG(DF.FoodConsumedQty) AS AvgDailyConsumption
FROM ANIMAL A
JOIN DAILYFEEDING DF ON A.AnimalID = DF.AnimalID
WHERE EXTRACT(YEAR FROM DF.FeedingDate) = 2025
GROUP BY A.Gender;

-- -----------------------------------------------------------------------------
-- UPDATE 1: Give a 10% raise to DailyCost for all Diets where DailyCost < 50.
UPDATE DIETPLAN
SET DailyCost = DailyCost * 1.10
WHERE DailyCost < 50;

-- -----------------------------------------------------------------------------
-- UPDATE 2: Update HealthStatus to 'Critical' for animals whose collected weight is suspiciously low.
UPDATE HEALTHRECORD
SET HealthStatus = 'Critical'
WHERE Weight < 5;

-- -----------------------------------------------------------------------------
-- UPDATE 3: Move animals from Habitat 1 to another to balance capacity.
UPDATE ANIMAL
SET HabitatID = (SELECT HabitatID FROM HABITAT WHERE HabitatID != 1 AND MaxCapacity > 10 LIMIT 1)
WHERE HabitatID = 1;

-- -----------------------------------------------------------------------------
-- DELETE 1: Delete health records older than 10 years.
DELETE FROM HEALTHRECORD
WHERE CheckupDate < CURRENT_DATE - INTERVAL '10 years';

-- -----------------------------------------------------------------------------
-- DELETE 2: Delete unused Diet Plans.
DELETE FROM DIETPLAN
WHERE DietPlanID NOT IN (SELECT DietPlanID FROM ANIMAL WHERE DietPlanID IS NOT NULL);

-- -----------------------------------------------------------------------------
-- DELETE 3: Delete daily feeding logs where the consumed quantity is exactly 0.
DELETE FROM DAILYFEEDING
WHERE FoodConsumedQty = 0;
