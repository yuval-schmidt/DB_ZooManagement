-- Function 2: Get_Animals_By_Vet_RefCursor
-- Returns a Ref Cursor pointing to a list of animals treated by a specific veterinarian.
-- Demonstrates: Returning a Ref Cursor, Branching, Exception Handling, Explicit/Implicit Cursor, Loops, Records, DML.

CREATE OR REPLACE FUNCTION Get_Animals_By_Vet_RefCursor(p_VetID INT)
RETURNS REFCURSOR AS $$
DECLARE
    v_refcur REFCURSOR;
    v_vet_exists INT;
    v_visit_record RECORD; 
    
    
    cur_visits CURSOR FOR 
        SELECT VisitID FROM MEDICALVISIT WHERE VetID = p_VetID;
BEGIN
    
    SELECT COUNT(*) INTO v_vet_exists FROM VETERINARIAN WHERE VetID = p_VetID;
    
    IF v_vet_exists = 0 THEN
        RAISE EXCEPTION 'Veterinarian with ID % does not exist in the system.', p_VetID;
    END IF;

    OPEN cur_visits;
    LOOP
        FETCH cur_visits INTO v_visit_record;
        EXIT WHEN NOT FOUND;
        
        UPDATE MEDICALVISIT 
        SET Summary = COALESCE(Summary, 'Reviewed by System') 
        WHERE VisitID = v_visit_record.VisitID;
    END LOOP;
    CLOSE cur_visits;

    OPEN v_refcur FOR
        SELECT DISTINCT A.AnimalID, A.Name, A.DateOfBirth, MV.VisitDate, MV.Reason
        FROM ANIMAL A
        JOIN MEDICALVISIT MV ON A.AnimalID = MV.AnimalID
        WHERE MV.VetID = p_VetID
        ORDER BY MV.VisitDate DESC;
        
    RETURN v_refcur;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error in Get_Animals_By_Vet_RefCursor: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;
