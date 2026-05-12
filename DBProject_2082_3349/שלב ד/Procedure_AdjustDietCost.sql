-- Procedure 2: Adjust_Diet_Cost_By_Species
-- Increases the daily cost of diet plans for all animals of a specific species by a percentage.
-- Demonstrates: DML (UPDATE), Explicit/Implicit Cursor, Records, Loop, Branching, Exception Handling, Ref Cursor.

CREATE OR REPLACE PROCEDURE Adjust_Diet_Cost_By_Species(
    p_SpeciesID INT, 
    p_PercentageIncrease NUMERIC,
    INOUT p_updated_plans_cursor REFCURSOR DEFAULT NULL
)
LANGUAGE plpgsql AS $$
DECLARE
    cur_diet_plans CURSOR FOR
        SELECT DISTINCT DP.DietPlanID, DP.DailyCost
        FROM DIETPLAN DP
        JOIN ANIMAL A ON DP.DietPlanID = A.DietPlanID
        WHERE A.SpeciesID = p_SpeciesID;
        
    v_diet_record RECORD;
    v_updated_count INT := 0;
    v_dummy_var INT;
BEGIN
    IF p_PercentageIncrease <= 0 THEN
        RAISE EXCEPTION 'Percentage increase must be greater than 0';
    END IF;

    SELECT COUNT(*) INTO v_dummy_var FROM SPECIES WHERE SpeciesID = p_SpeciesID;
    IF v_dummy_var = 0 THEN
        RAISE EXCEPTION 'Species ID % does not exist', p_SpeciesID;
    END IF;

    OPEN cur_diet_plans;
    LOOP
        FETCH cur_diet_plans INTO v_diet_record;
        EXIT WHEN NOT FOUND;
        
        UPDATE DIETPLAN
        SET DailyCost = v_diet_record.DailyCost * (1 + (p_PercentageIncrease / 100))
        WHERE DietPlanID = v_diet_record.DietPlanID;
        
        v_updated_count := v_updated_count + 1;
    END LOOP;
    CLOSE cur_diet_plans;
    
    OPEN p_updated_plans_cursor FOR
        SELECT DISTINCT DP.DietPlanID, DP.DailyCost, DP.PlanName
        FROM DIETPLAN DP
        JOIN ANIMAL A ON DP.DietPlanID = A.DietPlanID
        WHERE A.SpeciesID = p_SpeciesID;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Failed to adjust diet costs: %', SQLERRM;
END;
$$;
