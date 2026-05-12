-- Procedure 1: Process_Routine_Checkups
-- Automatically generates a new 'Healthy' health record for animals that haven't had a checkup in over a year.
-- Demonstrates: DML (INSERT), Implicit Cursor, Explicit Cursor, Records, Loop, Exceptions, Branching, Ref Cursor.

CREATE OR REPLACE PROCEDURE Process_Routine_Checkups(INOUT p_result_cursor REFCURSOR DEFAULT NULL)
LANGUAGE plpgsql AS $$
DECLARE
    rec_animal RECORD; 
    v_latest_weight NUMERIC(6,2);
    v_checkup_count INT := 0;
    v_new_record_id INT;
BEGIN
    SELECT COALESCE(MAX(RecordID), 0) INTO v_new_record_id FROM HEALTHRECORD;

    FOR rec_animal IN (
        SELECT A.AnimalID, A.Name
        FROM ANIMAL A
        WHERE A.AnimalID NOT IN (
            SELECT AnimalID FROM HEALTHRECORD WHERE CheckupDate >= CURRENT_DATE - INTERVAL '1 year'
        )
    )
    LOOP
        SELECT COALESCE((SELECT Weight FROM HEALTHRECORD WHERE AnimalID = rec_animal.AnimalID ORDER BY CheckupDate DESC LIMIT 1), 10.00)
        INTO v_latest_weight;
        
        v_new_record_id := v_new_record_id + 1;
        
        INSERT INTO HEALTHRECORD (RecordID, CheckupDate, Weight, HealthStatus, AnimalID)
        VALUES (v_new_record_id, CURRENT_DATE, v_latest_weight, 'Healthy', rec_animal.AnimalID);
        
        v_checkup_count := v_checkup_count + 1;
    END LOOP;
    
    IF v_checkup_count = 0 THEN
        RAISE NOTICE 'No routine checkups were needed.';
    ELSE
        RAISE NOTICE 'Processed % routine checkups successfully.', v_checkup_count;
    END IF;

    OPEN p_result_cursor FOR 
        SELECT * FROM HEALTHRECORD WHERE RecordID > (v_new_record_id - v_checkup_count);

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error processing routine checkups: %', SQLERRM;
END;
$$;
