-- Phase 4: AlterTable.sql
-- Contains schema changes necessary for Phase 4 triggers and procedures.

-- 1. Create a log table for recording changes in habitat capacity
CREATE TABLE HABITAT_CAPACITY_LOG (
    LogID SERIAL PRIMARY KEY,
    HabitatID INT NOT NULL,
    OldCapacity INT,
    NewCapacity INT,
    ChangeDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (HabitatID) REFERENCES HABITAT(HabitatID)
);
