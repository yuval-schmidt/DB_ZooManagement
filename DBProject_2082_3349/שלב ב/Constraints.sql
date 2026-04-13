-- Constraint 1: Ensure DateOfBirth is not in the future
ALTER TABLE ANIMAL 
ADD CONSTRAINT check_dob_past 
CHECK (DateOfBirth <= CURRENT_DATE);

-- Constraint 2: Ensure valid health statuses in HealthRecord
ALTER TABLE HEALTHRECORD 
ADD CONSTRAINT check_valid_status 
CHECK (HealthStatus IN ('Healthy', 'Sick', 'Recovering', 'Critical', 'Deceased'));
