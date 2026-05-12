-- Main Program 1
-- Calls Function: Get_Habitat_Diet_Cost
-- Calls Procedure: Process_Routine_Checkups
-- Contains an anonymous PL/pgSQL block to execute and test the functionality.

DO $$
DECLARE
    -- We assume HabitatID 1 exists from mock data.
    v_habitat_id INT := 1; 
    v_total_cost NUMERIC;
    v_result_cursor REFCURSOR := 'my_result_cursor'; -- initialize it
    v_record RECORD;
BEGIN
    RAISE NOTICE '--- Starting Main Program 1 ---';
    
    -- 1. Calling the Procedure
    RAISE NOTICE 'Calling Procedure: Process_Routine_Checkups...';
    CALL Process_Routine_Checkups(v_result_cursor);
    
    -- Read from ref cursor
    LOOP
        FETCH v_result_cursor INTO v_record;
        EXIT WHEN NOT FOUND;
        RAISE NOTICE 'New Checkup Created - RecordID: %, AnimalID: %', v_record.RecordID, v_record.AnimalID;
    END LOOP;
    CLOSE v_result_cursor;
    
    -- 2. Calling the Function
    RAISE NOTICE 'Calling Function: Get_Habitat_Diet_Cost for Habitat ID %...', v_habitat_id;
    v_total_cost := Get_Habitat_Diet_Cost(v_habitat_id);
    RAISE NOTICE 'Total Daily Diet Cost for Habitat % is %', v_habitat_id, v_total_cost;
    
    RAISE NOTICE '--- Main Program 1 Completed Successfully ---';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Main Program 1 encountered an error: %', SQLERRM;
END;
$$;
