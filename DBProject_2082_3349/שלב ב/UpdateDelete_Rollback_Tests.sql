-- ==============================================================================
-- UPDATE AND DELETE ROLLBACK TESTS
-- Script designed to show state before, perform action, show state after,
-- and then rollback to restore the original state (as required by the assignment).
-- ==============================================================================

-- ==============================================================================
-- UPDATE 1
-- Increase daily cost by 15% for diet plans assigned to strictly 'Endangered' species.
-- ==============================================================================
BEGIN;

-- 1. Show Before
SELECT DietPlanID, PlanName, DailyCost 
FROM DIETPLAN 
WHERE DietPlanID IN (
    SELECT A.DietPlanID
    FROM ANIMAL A
    JOIN SPECIES S ON A.SpeciesID = S.SpeciesID
    WHERE S.ConservationStatus = 'Endangered'
);

-- 2. Execute Update
UPDATE DIETPLAN
SET DailyCost = DailyCost * 1.15
WHERE DietPlanID IN (
    SELECT A.DietPlanID
    FROM ANIMAL A
    JOIN SPECIES S ON A.SpeciesID = S.SpeciesID
    WHERE S.ConservationStatus = 'Endangered'
);

-- 3. Show After
SELECT DietPlanID, PlanName, DailyCost 
FROM DIETPLAN 
WHERE DietPlanID IN (
    SELECT A.DietPlanID
    FROM ANIMAL A
    JOIN SPECIES S ON A.SpeciesID = S.SpeciesID
    WHERE S.ConservationStatus = 'Endangered'
);

-- 4. Rollback to original state
ROLLBACK;


-- ==============================================================================
-- UPDATE 2
-- Transfer animals born before 2015 to the habitat with the largest theoretical capacity.
-- ==============================================================================
BEGIN;

-- 1. Show Before
SELECT AnimalID, Name, HabitatID 
FROM ANIMAL
WHERE EXTRACT(YEAR FROM DateOfBirth) < 2015
ORDER BY AnimalID;

-- 2. Execute Update
UPDATE ANIMAL
SET HabitatID = (
    SELECT HabitatID 
    FROM HABITAT 
    ORDER BY MaxCapacity DESC 
    LIMIT 1
)
WHERE EXTRACT(YEAR FROM DateOfBirth) < 2015;

-- 3. Show After
SELECT AnimalID, Name, HabitatID 
FROM ANIMAL
WHERE EXTRACT(YEAR FROM DateOfBirth) < 2015;

-- 4. Rollback to original state
ROLLBACK;


-- ==============================================================================
-- UPDATE 3
-- Mark animal health as 'Critical' if their consumed food was concerningly low this current month.
-- ==============================================================================
BEGIN;

-- 1. Show Before
SELECT RecordID, AnimalID, HealthStatus 
FROM HEALTHRECORD
WHERE AnimalID IN (
    SELECT DF.AnimalID
    FROM DAILYFEEDING DF
    WHERE DF.FoodConsumedQty < 2.0
      AND EXTRACT(MONTH FROM DF.FeedingDate) = EXTRACT(MONTH FROM CURRENT_DATE)
);

-- 2. Execute Update
UPDATE HEALTHRECORD
SET HealthStatus = 'Critical'
WHERE AnimalID IN (
    SELECT DF.AnimalID
    FROM DAILYFEEDING DF
    WHERE DF.FoodConsumedQty < 2.0
      AND EXTRACT(MONTH FROM DF.FeedingDate) = EXTRACT(MONTH FROM CURRENT_DATE)
);

-- 3. Show After
SELECT RecordID, AnimalID, HealthStatus 
FROM HEALTHRECORD
WHERE AnimalID IN (
    SELECT DF.AnimalID
    FROM DAILYFEEDING DF
    WHERE DF.FoodConsumedQty < 2.0
      AND EXTRACT(MONTH FROM DF.FeedingDate) = EXTRACT(MONTH FROM CURRENT_DATE)
);

-- 4. Rollback to original state
ROLLBACK;


-- ==============================================================================
-- DELETE 1
-- Remove daily feeding logs from previous years for animals inhabiting 'Continental' climates.
-- ==============================================================================
BEGIN;

-- 1. Show Before (Rows exist)
SELECT FeedingID, AnimalID, FeedingDate 
FROM DAILYFEEDING
WHERE EXTRACT(YEAR FROM FeedingDate) < EXTRACT(YEAR FROM CURRENT_DATE)
  AND AnimalID IN (
      SELECT A.AnimalID
      FROM ANIMAL A
      JOIN HABITAT H ON A.HabitatID = H.HabitatID
      WHERE H.ClimateType = 'Continental'
  );

-- 2. Execute Delete
DELETE FROM DAILYFEEDING
WHERE EXTRACT(YEAR FROM FeedingDate) < EXTRACT(YEAR FROM CURRENT_DATE)
  AND AnimalID IN (
      SELECT A.AnimalID
      FROM ANIMAL A
      JOIN HABITAT H ON A.HabitatID = H.HabitatID
      WHERE H.ClimateType = 'Continental'
  );

-- 3. Show After (Should be empty)
SELECT FeedingID, AnimalID, FeedingDate 
FROM DAILYFEEDING
WHERE EXTRACT(YEAR FROM FeedingDate) < EXTRACT(YEAR FROM CURRENT_DATE)
  AND AnimalID IN (
      SELECT A.AnimalID
      FROM ANIMAL A
      JOIN HABITAT H ON A.HabitatID = H.HabitatID
      WHERE H.ClimateType = 'Arctic'
  );

-- 4. Rollback to original state
ROLLBACK;


-- ==============================================================================
-- DELETE 2
-- Delete health records of animals that ate less than 10 units of food in previous years.
-- ==============================================================================
BEGIN;

-- 1. Show Before
SELECT RecordID, AnimalID, HealthStatus 
FROM HEALTHRECORD
WHERE AnimalID IN (
    SELECT AnimalID 
    FROM DAILYFEEDING 
    WHERE FoodConsumedQty < 10
      AND EXTRACT(YEAR FROM FeedingDate) < EXTRACT(YEAR FROM CURRENT_DATE)
);

-- 2. Execute Delete
DELETE FROM HEALTHRECORD
WHERE AnimalID IN (
    SELECT AnimalID 
    FROM DAILYFEEDING 
    WHERE FoodConsumedQty < 10
      AND EXTRACT(YEAR FROM FeedingDate) = EXTRACT(YEAR FROM CURRENT_DATE)
);

-- 3. Show After (Should be empty)
SELECT RecordID, AnimalID, HealthStatus 
FROM HEALTHRECORD
WHERE AnimalID IN (
    SELECT AnimalID 
    FROM DAILYFEEDING 
    WHERE FoodConsumedQty < 10
      AND EXTRACT(YEAR FROM FeedingDate) = EXTRACT(YEAR FROM CURRENT_DATE)
);

-- 4. Rollback to original state
ROLLBACK;


-- ==============================================================================
-- DELETE 3
-- Delete daily feeding records from the first quarter of the year for 'Arid' animals.
-- ==============================================================================
BEGIN;

-- 1. Show Before
SELECT FeedingID, AnimalID, FeedingDate 
FROM DAILYFEEDING
WHERE EXTRACT(MONTH FROM FeedingDate) IN (1, 2, 3)
  AND AnimalID IN (
      SELECT A.AnimalID
      FROM ANIMAL A
      JOIN HABITAT H ON A.HabitatID = H.HabitatID
      WHERE H.ClimateType = 'Arid'
  )
ORDER BY FeedingID;

-- 2. Execute Delete
DELETE FROM DAILYFEEDING
WHERE EXTRACT(MONTH FROM FeedingDate) IN (1, 2, 3)
  AND AnimalID IN (
      SELECT A.AnimalID
      FROM ANIMAL A
      JOIN HABITAT H ON A.HabitatID = H.HabitatID
      WHERE H.ClimateType = 'Arid'
  );

-- 3. Show After (Should be empty)
SELECT FeedingID, AnimalID, FeedingDate 
FROM DAILYFEEDING
WHERE EXTRACT(MONTH FROM FeedingDate) IN (1, 2, 3)
  AND AnimalID IN (
      SELECT A.AnimalID
      FROM ANIMAL A
      JOIN HABITAT H ON A.HabitatID = H.HabitatID
      WHERE H.ClimateType = 'Arid'
  )
ORDER BY FeedingID;

-- 4. Rollback to original state
ROLLBACK;
