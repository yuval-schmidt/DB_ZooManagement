-- Main Program 2
-- Calls Procedure: Adjust_Diet_Cost_By_Species
-- Calls Function: Get_Animals_By_Vet_RefCursor
-- Contains an anonymous PL/pgSQL block to execute and test the functionality.

DO $$
DECLARE
    -- We assume VetID 1 and SpeciesID 1 exist from mock data.
    v_vet_id INT := 1; 
    v_species_id INT := 1; 
    v_refcur REFCURSOR;
    v_animal_record RECORD;
    v_updated_plans_cursor REFCURSOR := 'my_updated_plans';
BEGIN
    RAISE NOTICE '--- Starting Main Program 2 ---';
    
    -- 1. Calling the Procedure
    RAISE NOTICE 'Calling Procedure: Adjust_Diet_Cost_By_Species for Species ID %...', v_species_id;
    -- Increasing cost by 10.5%
    CALL Adjust_Diet_Cost_By_Species(v_species_id, 10.5, v_updated_plans_cursor); 
    
    -- Read from returned ref cursor from procedure
    LOOP
        FETCH v_updated_plans_cursor INTO v_animal_record;
        EXIT WHEN NOT FOUND;
        RAISE NOTICE 'Updated Diet Plan ID: %, New Cost: %', v_animal_record.DietPlanID, v_animal_record.DailyCost;
    END LOOP;
    CLOSE v_updated_plans_cursor;

    -- 2. Calling the Function
    RAISE NOTICE 'Calling Function: Get_Animals_By_Vet_RefCursor for Vet ID %...', v_vet_id;
    v_refcur := Get_Animals_By_Vet_RefCursor(v_vet_id);
    
    -- Loop through the ref cursor to process and print results
    LOOP
        FETCH v_refcur INTO v_animal_record;
        EXIT WHEN NOT FOUND;
        RAISE NOTICE 'Vet % Treated Animal ID: %, Name: %, Reason: %', 
            v_vet_id, v_animal_record.AnimalID, v_animal_record.Name, v_animal_record.Reason;
    END LOOP;
    
    -- Remember to close the cursor
    CLOSE v_refcur;
    
    RAISE NOTICE '--- Main Program 2 Completed Successfully ---';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Main Program 2 encountered an error: %', SQLERRM;
END;
$$;
