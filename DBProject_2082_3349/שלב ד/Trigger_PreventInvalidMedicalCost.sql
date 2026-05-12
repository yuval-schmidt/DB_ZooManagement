-- Trigger 1: Trg_Prevent_Invalid_Medical_Cost
-- Triggers BEFORE UPDATE on MEDICALVISIT. 
-- Validates the medical cost and prevents excessively high costs without a descriptive summary.
-- Demonstrates: Trigger on UPDATE, Branching, Exceptions.

CREATE OR REPLACE FUNCTION Func_Check_Medical_Cost()
RETURNS TRIGGER AS $$
BEGIN
    -- Branching
    IF NEW.Cost < 0 THEN
        RAISE EXCEPTION 'Medical visit cost cannot be negative.';
    END IF;
    
    -- If cost is updated to a very high amount without summary
    IF NEW.Cost > 500 AND NEW.Cost > OLD.Cost AND (NEW.Summary IS NULL OR TRIM(NEW.Summary) = '') THEN
         RAISE EXCEPTION 'A high medical cost (> 500) requires a detailed summary of the visit.';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER Trg_Prevent_Invalid_Medical_Cost
BEFORE UPDATE ON MEDICALVISIT
FOR EACH ROW
EXECUTE FUNCTION Func_Check_Medical_Cost();
