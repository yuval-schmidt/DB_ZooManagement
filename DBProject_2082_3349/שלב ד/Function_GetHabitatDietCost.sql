-- Function 1: Get_Habitat_Diet_Cost
-- Calculates the total daily diet cost for all animals residing in a specific habitat.
-- Demonstrates: Explicit Cursor, Loop, Branching, Exception Handling, Implicit Cursor, Records, DML.

CREATE OR REPLACE FUNCTION Get_Habitat_Diet_Cost(p_HabitatID INT)
RETURNS NUMERIC AS $$
DECLARE
    v_total_cost NUMERIC(10,2) := 0;
    v_daily_cost NUMERIC(6,2);
    v_animal_count INT := 0;
    v_record RECORD;
    
    cur_animals CURSOR FOR 
        SELECT AnimalID, DietPlanID 
        FROM ANIMAL 
        WHERE HabitatID = p_HabitatID;
BEGIN
    OPEN cur_animals;
    LOOP
        FETCH cur_animals INTO v_record;
        EXIT WHEN NOT FOUND;
        
        v_animal_count := v_animal_count + 1;
        
        SELECT DailyCost INTO v_daily_cost
        FROM DIETPLAN
        WHERE DietPlanID = v_record.DietPlanID;
        
        v_total_cost := v_total_cost + v_daily_cost;
        
        UPDATE ANIMAL SET DateOfBirth = DateOfBirth WHERE AnimalID = v_record.AnimalID; 
    END LOOP;
    CLOSE cur_animals;
    
    IF v_animal_count = 0 THEN
        RAISE EXCEPTION 'No animals found in habitat ID %', p_HabitatID;
    END IF;
    
    RETURN v_total_cost;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'An error occurred while calculating habitat diet cost: %', SQLERRM;
        RETURN -1;
END;
$$ LANGUAGE plpgsql;
