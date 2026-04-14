-- Constraint 1: Ensure DateOfBirth is not in the future
ALTER TABLE ANIMAL 
ADD CONSTRAINT check_dob_past 
CHECK (DateOfBirth <= CURRENT_DATE);

-- Constraint 2: Ensure valid health statuses in HealthRecord

ALTER TABLE HEALTHRECORD 
ADD CONSTRAINT check_valid_status 
CHECK (HealthStatus IN ('Healthy', 'Sick', 'Recovering', 'Critical', 'Deceased'));

-- Constraint 3: Ensure FeedingDate in DailyFeeding cannot be logged in the future
ALTER TABLE DAILYFEEDING
ADD CONSTRAINT check_feeding_past
CHECK (FeedingDate <= CURRENT_DATE);

-- ==================================================================
-- NEGATIVE TESTS: Queries designed to intentionally trigger the errors
-- ==================================================================

-- Negative Test for Constraint 1 (check_dob_past on ANIMAL)
-- Tries to insert an animal with a future DateOfBirth. This should fail!
INSERT INTO ANIMAL (AnimalID, Name, DateOfBirth, Gender, HabitatID, SpeciesID, DietPlanID)
VALUES (9999, 'Future Animal', CURRENT_DATE + INTERVAL '10 days', 'Male', 1, 1, 1);

-- Negative Test for Constraint 2 (check_valid_status on HEALTHRECORD)
-- Tries to insert a record with an invalid status 'Super Healthy'. This should fail!
INSERT INTO HEALTHRECORD (RecordID, CheckupDate, Weight, HealthStatus, AnimalID)
VALUES (9999, CURRENT_DATE, 50.0, 'Super Healthy', 1);

-- Negative Test for Constraint 3 (check_feeding_past on DAILYFEEDING)
-- Tries to log a feeding day that hasn't happened yet. This should fail!
INSERT INTO DAILYFEEDING (FeedingID, FeedingDate, FoodConsumedQty, AnimalID)
VALUES (9999, CURRENT_DATE + INTERVAL '5 days', 10.0, 1);
