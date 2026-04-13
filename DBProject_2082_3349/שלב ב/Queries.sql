-- ==============================================================================
-- 8 SELECT QUERIES (COMPLIANT: JOIN, GROUP BY, ORDER BY, DATE MANIPULATION, GUI COLUMNS)
-- ==============================================================================

-- =========================================================
-- Double Query 1: Total food consumed per species for animals born after year 2020.
-- Efficiency: JOIN allows the database query optimizer to execute in a single sweep based on indices, while SUBQUERY (IN/Derived) may execute slightly slower if the subquery returns highly duplicated IDs without an index. Here, both approaches yield excellent performance on modern PostgreSQL, though Version A (Standard JOIN) is strictly preferred.
-- =========================================================

-- Version A: Using Standard JOIN
SELECT S.CommonName, S.ScientificName, SUM(DF.FoodConsumedQty) AS TotalFoodConsumed
FROM SPECIES S
JOIN ANIMAL A ON S.SpeciesID = A.SpeciesID
JOIN DAILYFEEDING DF ON A.AnimalID = DF.AnimalID
WHERE EXTRACT(YEAR FROM A.DateOfBirth) > 2020
GROUP BY S.CommonName, S.ScientificName
ORDER BY TotalFoodConsumed DESC;

-- Version B: Using Derived Table Subquery
SELECT S.CommonName, S.ScientificName, Agg.TotalQty AS TotalFoodConsumed
FROM SPECIES S
JOIN (
    SELECT A.SpeciesID, SUM(DF.FoodConsumedQty) as TotalQty
    FROM ANIMAL A
    JOIN DAILYFEEDING DF ON A.AnimalID = DF.AnimalID
    WHERE EXTRACT(YEAR FROM A.DateOfBirth) > 2020
    GROUP BY A.SpeciesID
) Agg ON S.SpeciesID = Agg.SpeciesID
ORDER BY TotalFoodConsumed DESC;

-- =========================================================
-- Double Query 2: Habitat population count for animals missing checkups this year.
-- Efficiency: NOT EXISTS is significantly more efficient than NOT IN for an "Anti-Join". NOT IN can fail silently if the subquery returns NULL values, whereas NOT EXISTS safely short-circuits evaluation as soon as it finds a single match, making it much faster for large tables.
-- =========================================================

-- Version A: Using NOT IN
SELECT H.HabitatName, H.ClimateType, COUNT(A.AnimalID) AS AnimalCount
FROM HABITAT H
JOIN ANIMAL A ON H.HabitatID = A.HabitatID
WHERE H.HabitatID NOT IN (
    SELECT DISTINCT A2.HabitatID
    FROM ANIMAL A2
    JOIN HEALTHRECORD HR ON A2.AnimalID = HR.AnimalID
    WHERE EXTRACT(YEAR FROM HR.CheckupDate) = EXTRACT(YEAR FROM CURRENT_DATE)
)
GROUP BY H.HabitatName, H.ClimateType
ORDER BY AnimalCount DESC;

-- Version B: Using NOT EXISTS
SELECT H.HabitatName, H.ClimateType, COUNT(A.AnimalID) AS AnimalCount
FROM HABITAT H
JOIN ANIMAL A ON H.HabitatID = A.HabitatID
WHERE NOT EXISTS (
    SELECT 1
    FROM ANIMAL A2
    JOIN HEALTHRECORD HR ON A2.AnimalID = HR.AnimalID
    WHERE A2.HabitatID = H.HabitatID 
      AND EXTRACT(YEAR FROM HR.CheckupDate) = EXTRACT(YEAR FROM CURRENT_DATE)
)
GROUP BY H.HabitatName, H.ClimateType
ORDER BY AnimalCount DESC;

-- =========================================================
-- Double Query 3: Average dietary cost per habitat for feedings in May.
-- Efficiency: The GROUP BY approach (Version A) relies on efficient Set-Based Hash Aggregation. Version B forces a correlated subquery in the SELECT clause, triggering an "N+1 execution" where the inner query runs sequentially for every grouped habitat row, scaling poorly as table sizes increase.
-- =========================================================

-- Version A: Using GROUP BY with standard JOIN
SELECT H.HabitatName, H.ClimateType, AVG(D.DailyCost) AS AverageDietCost
FROM HABITAT H
JOIN ANIMAL A ON H.HabitatID = A.HabitatID
JOIN DIETPLAN D ON A.DietPlanID = D.DietPlanID
JOIN DAILYFEEDING DF ON A.AnimalID = DF.AnimalID
WHERE EXTRACT(MONTH FROM DF.FeedingDate) = 5
GROUP BY H.HabitatName, H.ClimateType
ORDER BY AverageDietCost DESC;

-- Version B: Using Correlated Subquery inside SELECT
SELECT H.HabitatName, H.ClimateType, 
       (SELECT AVG(D2.DailyCost)
        FROM ANIMAL A2
        JOIN DIETPLAN D2 ON A2.DietPlanID = D2.DietPlanID
        JOIN DAILYFEEDING DF2 ON A2.AnimalID = DF2.AnimalID
        WHERE A2.HabitatID = H.HabitatID 
          AND EXTRACT(MONTH FROM DF2.FeedingDate) = 5) AS AverageDietCost
FROM HABITAT H
JOIN ANIMAL A ON H.HabitatID = A.HabitatID
GROUP BY H.HabitatName, H.ClimateType
ORDER BY AverageDietCost DESC;

-- =========================================================
-- Double Query 4: Most frequent health status per species in 2024.
-- Efficiency: Version A uses Window Functions (`ROW_NUMBER`) allowing the engine to traverse the dataset once in-memory. Version B relies on a heavy correlated `HAVING MAX` subquery that requires rescanning the table multiple times, making Version A vastly superior.
-- =========================================================

-- Version A: Using Window Function
WITH StatusAgg AS (
    SELECT S.CommonName, HR.HealthStatus, COUNT(HR.RecordID) AS StatusOccurrences,
           EXTRACT(YEAR FROM HR.CheckupDate) AS CheckupYear
    FROM SPECIES S
    JOIN ANIMAL A ON S.SpeciesID = A.SpeciesID
    JOIN HEALTHRECORD HR ON A.AnimalID = HR.AnimalID
    GROUP BY S.CommonName, HR.HealthStatus, EXTRACT(YEAR FROM HR.CheckupDate)
)
SELECT CommonName, HealthStatus, StatusOccurrences
FROM (
    SELECT CommonName, HealthStatus, StatusOccurrences,
           ROW_NUMBER() OVER(PARTITION BY CommonName ORDER BY StatusOccurrences DESC) as rn
    FROM StatusAgg
    WHERE CheckupYear = 2024
) Ranked
WHERE rn = 1
ORDER BY StatusOccurrences DESC;

-- Version B: Using MAX Subquery in HAVING
SELECT S.CommonName, HR.HealthStatus, COUNT(HR.RecordID) AS StatusOccurrences
FROM SPECIES S
JOIN ANIMAL A ON S.SpeciesID = A.SpeciesID
JOIN HEALTHRECORD HR ON A.AnimalID = HR.AnimalID
WHERE EXTRACT(YEAR FROM HR.CheckupDate) = 2024
GROUP BY S.CommonName, HR.HealthStatus
HAVING COUNT(HR.RecordID) = (
    SELECT MAX(Occurrences)
    FROM (
        SELECT COUNT(HR2.RecordID) AS Occurrences
        FROM ANIMAL A2
        JOIN HEALTHRECORD HR2 ON A2.AnimalID = HR2.AnimalID
        WHERE A2.SpeciesID = S.SpeciesID 
          AND EXTRACT(YEAR FROM HR2.CheckupDate) = 2024
        GROUP BY HR2.HealthStatus
    ) InnerAgg
)
ORDER BY StatusOccurrences DESC;

-- ==============================================================================
-- REGULAR QUERIES
-- ==============================================================================

-- Regular Query 1: Total daily dietary cost for each species, observing only checkups in April.
SELECT S.CommonName, S.ScientificName, SUM(D.DailyCost) AS TotalSpeciesDietCost
FROM SPECIES S
JOIN ANIMAL A ON S.SpeciesID = A.SpeciesID
JOIN DIETPLAN D ON A.DietPlanID = D.DietPlanID
JOIN HEALTHRECORD HR ON A.AnimalID = HR.AnimalID
WHERE EXTRACT(MONTH FROM HR.CheckupDate) = 4
GROUP BY S.CommonName, S.ScientificName
ORDER BY TotalSpeciesDietCost DESC;

-- Regular Query 2: Average habitat capacity per climate type for animals fed on the 15th of any month.
SELECT H.ClimateType, S.CommonName, AVG(H.MaxCapacity) AS AvgCapacity
FROM HABITAT H
JOIN ANIMAL A ON H.HabitatID = A.HabitatID
JOIN SPECIES S ON A.SpeciesID = S.SpeciesID
JOIN DAILYFEEDING DF ON A.AnimalID = DF.AnimalID
WHERE EXTRACT(DAY FROM DF.FeedingDate) = 15
GROUP BY H.ClimateType, S.CommonName
ORDER BY AvgCapacity DESC;

-- Regular Query 3: Count of surviving animals based on Diet Plan, born outside of the year 2020.
SELECT DP.PlanName, DP.DailyCost, COUNT(A.AnimalID) AS AssignedAnimalsCount
FROM DIETPLAN DP
JOIN ANIMAL A ON DP.DietPlanID = A.DietPlanID
JOIN HEALTHRECORD HR ON A.AnimalID = HR.AnimalID
WHERE EXTRACT(YEAR FROM A.DateOfBirth) <> 2020
  AND HR.HealthStatus <> 'Deceased'
GROUP BY DP.PlanName, DP.DailyCost
ORDER BY AssignedAnimalsCount DESC;

-- Regular Query 4: Total weight recorded per habitat for checkups occurring in December.
SELECT H.HabitatName, H.ClimateType, SUM(HR.Weight) AS TotalWeightRecorded
FROM HABITAT H
JOIN ANIMAL A ON H.HabitatID = A.HabitatID
JOIN HEALTHRECORD HR ON A.AnimalID = HR.AnimalID
WHERE EXTRACT(MONTH FROM HR.CheckupDate) = 12
GROUP BY H.HabitatName, H.ClimateType
ORDER BY TotalWeightRecorded DESC;


-- ==============================================================================
-- 3 UPDATE QUERIES (NON-TRIVIAL WITH MULTI-TABLE LOGIC)
-- ==============================================================================

-- UPDATE 1: Increase daily cost by 15% for diet plans assigned to strictly 'Endangered' species.
UPDATE DIETPLAN
SET DailyCost = DailyCost * 1.15
WHERE DietPlanID IN (
    SELECT A.DietPlanID
    FROM ANIMAL A
    JOIN SPECIES S ON A.SpeciesID = S.SpeciesID
    WHERE S.ConservationStatus = 'Endangered'
);

-- UPDATE 2: Transfer animals born before 2015 to the habitat with the largest theoretical capacity.
UPDATE ANIMAL
SET HabitatID = (
    SELECT HabitatID 
    FROM HABITAT 
    ORDER BY MaxCapacity DESC 
    LIMIT 1
)
WHERE EXTRACT(YEAR FROM DateOfBirth) < 2015;

-- UPDATE 3: Mark animal health as 'Critical' if their consumed food was concerningly low this current month.
UPDATE HEALTHRECORD
SET HealthStatus = 'Critical'
WHERE AnimalID IN (
    SELECT DF.AnimalID
    FROM DAILYFEEDING DF
    WHERE DF.FoodConsumedQty < 2.0
      AND EXTRACT(MONTH FROM DF.FeedingDate) = EXTRACT(MONTH FROM CURRENT_DATE)
);


-- ==============================================================================
-- 3 DELETE QUERIES (NON-TRIVIAL WITH MULTI-TABLE LOGIC)
-- ==============================================================================

-- DELETE 1: Remove daily feeding logs from previous years for animals inhabiting 'Arctic' climates.
DELETE FROM DAILYFEEDING
WHERE EXTRACT(YEAR FROM FeedingDate) < EXTRACT(YEAR FROM CURRENT_DATE)
  AND AnimalID IN (
      SELECT A.AnimalID
      FROM ANIMAL A
      JOIN HABITAT H ON A.HabitatID = H.HabitatID
      WHERE H.ClimateType = 'Arctic'
  );

-- DELETE 2: Delete health records of animals that consumed strictly 0 food during the current year.
DELETE FROM HEALTHRECORD
WHERE AnimalID IN (
    SELECT AnimalID 
    FROM DAILYFEEDING 
    WHERE FoodConsumedQty = 0
      AND EXTRACT(YEAR FROM FeedingDate) = EXTRACT(YEAR FROM CURRENT_DATE)
);

-- DELETE 3: Delete daily feeding records from the first quarter of the year (Jan-Mar) for animals residing in 'Arid' climates.
DELETE FROM DAILYFEEDING
WHERE EXTRACT(MONTH FROM FeedingDate) IN (1, 2, 3)
  AND AnimalID IN (
      SELECT A.AnimalID FROM ANIMAL A
      JOIN HABITAT H ON A.HabitatID = H.HabitatID 
      WHERE H.ClimateType = 'Arid'
  );
