-- Trigger 2: Trg_Habitat_Capacity_Log
-- Triggers AFTER UPDATE on HABITAT. 
-- Logs any changes made to the MaxCapacity of a habitat into a separate log table.
-- Demonstrates: Trigger on UPDATE, DML (INSERT).

CREATE OR REPLACE FUNCTION Func_Log_Habitat_Capacity()
RETURNS TRIGGER AS $$
BEGIN
    -- Branching to only log when the capacity actually changes
    IF OLD.MaxCapacity IS DISTINCT FROM NEW.MaxCapacity THEN
        -- Insert a record into the new table created in AlterTable.sql
        INSERT INTO HABITAT_CAPACITY_LOG (HabitatID, OldCapacity, NewCapacity)
        VALUES (NEW.HabitatID, OLD.MaxCapacity, NEW.MaxCapacity);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER Trg_Habitat_Capacity_Log
AFTER UPDATE ON HABITAT
FOR EACH ROW
EXECUTE FUNCTION Func_Log_Habitat_Capacity();
