-- Example 1: ROLLBACK demonstration
BEGIN TRANSACTION;

-- Show current state
SELECT DietPlanID, DailyCost FROM DIETPLAN WHERE DietPlanID = 1;

-- Attempt an update
UPDATE DIETPLAN SET DailyCost = 9999.99 WHERE DietPlanID = 1;

-- Show state after update
SELECT DietPlanID, DailyCost FROM DIETPLAN WHERE DietPlanID = 1;

-- Rollback the update
ROLLBACK;

-- Show state after rollback (should be reverted)
SELECT DietPlanID, DailyCost FROM DIETPLAN WHERE DietPlanID = 1;

-- ---------------------------------------------------------------------

-- Example 2: COMMIT demonstration
BEGIN TRANSACTION;

-- Insert a temporary record
INSERT INTO SPECIES (SpeciesID, CommonName, ScientificName, ConservationStatus)
VALUES (9999, 'Test Species', 'Testus Specificus', 'Least Concern');

-- Show after insert
SELECT * FROM SPECIES WHERE SpeciesID = 9999;

-- Commit the transaction
COMMIT;

-- Show that it was permanently saved
SELECT * FROM SPECIES WHERE SpeciesID = 9999;

-- Clean up
DELETE FROM SPECIES WHERE SpeciesID = 9999;
