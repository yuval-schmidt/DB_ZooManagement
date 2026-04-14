import random
import csv
import os
from datetime import datetime, timedelta

def random_date(start, end):
    return start + timedelta(days=random.randint(0, int((end - start).days)))

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_import_dir = os.path.join(base_dir, 'DataImportFiles')
    os.makedirs(data_import_dir, exist_ok=True)
    
    # 1. Generate insertTables.sql for HABITAT (500 records)
    climates = ['Tropical', 'Arid', 'Temperate', 'Continental', 'Polar', 'Marine']
    habitats = []
    
    insert_sql_path = os.path.join(base_dir, 'insertTables.sql')
    with open(insert_sql_path, 'w', encoding='utf-8') as f:
        f.write("-- Manual INSERTS for HABITAT table (500 records)\n")
        f.write("DELETE FROM HABITAT;\n") # Optional clear
        for i in range(1, 501):
            name = f"Habitat Zone {i}"
            climate = random.choice(climates)
            max_cap = random.randint(10, 100)
            f.write(f"INSERT INTO HABITAT (HabitatID, HabitatName, ClimateType, MaxCapacity) VALUES ({i}, '{name}', '{climate}', {max_cap});\n")
            habitats.append(i)
    
    print(f"Generated {insert_sql_path}")

    # 2. Generate 20,000 records for ANIMAL and HEALTHRECORD
    genders = ['Male', 'Female']
    species_ids = list(range(1, 501)) # Assuming 500 species from mockaroo
    diet_ids = list(range(1, 501)) # Assuming 500 diet plans from mockaroo

    start_date = datetime(2010, 1, 1)
    end_date = datetime(2025, 1, 1)
    
    animal_csv_path = os.path.join(data_import_dir, 'ANIMAL.csv')
    health_csv_path = os.path.join(data_import_dir, 'HEALTHRECORD.csv')

    with open(animal_csv_path, 'w', newline='', encoding='utf-8') as f_animal, \
         open(health_csv_path, 'w', newline='', encoding='utf-8') as f_health:
        
        animal_writer = csv.writer(f_animal)
        health_writer = csv.writer(f_health)
        
        # Headers
        animal_writer.writerow(['AnimalID', 'Name', 'DateOfBirth', 'Gender', 'HabitatID', 'SpeciesID', 'DietPlanID'])
        health_writer.writerow(['RecordID', 'CheckupDate', 'Weight', 'HealthStatus', 'AnimalID'])
        
        health_record_id = 1
        statuses = ['Healthy', 'Sick', 'Under Observation', 'Recovering', 'Critical']
        
        for animal_id in range(1, 20001):
            name = f"Animal_{animal_id}"
            dob = random_date(start_date, end_date)
            gender = random.choice(genders)
            habitat_id = random.choice(habitats)
            species_id = random.choice(species_ids)
            diet_id = random.choice(diet_ids)
            
            animal_writer.writerow([animal_id, name, dob.strftime('%Y-%m-%d'), gender, habitat_id, species_id, diet_id])
            
            # Health record
            checkup_date = random_date(dob, datetime.now())
            weight = f"{random.uniform(5.0, 500.0):.2f}"
            status = random.choice(statuses)
            health_writer.writerow([health_record_id, checkup_date.strftime('%Y-%m-%d'), weight, status, animal_id])
            health_record_id += 1

    print(f"Generated {animal_csv_path} with 20000 records")
    print(f"Generated {health_csv_path} with 20000 records")

    # 3. Generate 500 records for EMPLOYEE, ACTIVITY_TYPE, ACTIVITY, ACTIVITY_EMPLOYEE, ACTIVITY_ANIMAL
    employee_csv_path = os.path.join(data_import_dir, 'EMPLOYEE.csv')
    activity_type_csv_path = os.path.join(data_import_dir, 'ACTIVITY_TYPE.csv')
    activity_csv_path = os.path.join(data_import_dir, 'ACTIVITY.csv')
    activity_employee_csv_path = os.path.join(data_import_dir, 'ACTIVITY_EMPLOYEE.csv')
    activity_animal_csv_path = os.path.join(data_import_dir, 'ACTIVITY_ANIMAL.csv')

    with open(employee_csv_path, 'w', newline='', encoding='utf-8') as f_emp, \
         open(activity_type_csv_path, 'w', newline='', encoding='utf-8') as f_at, \
         open(activity_csv_path, 'w', newline='', encoding='utf-8') as f_act, \
         open(activity_employee_csv_path, 'w', newline='', encoding='utf-8') as f_act_emp, \
         open(activity_animal_csv_path, 'w', newline='', encoding='utf-8') as f_act_anim:
         
        emp_writer = csv.writer(f_emp)
        at_writer = csv.writer(f_at)
        act_writer = csv.writer(f_act)
        act_emp_writer = csv.writer(f_act_emp)
        act_anim_writer = csv.writer(f_act_anim)
        
        emp_writer.writerow(['EmployeeID', 'FirstName', 'LastName', 'JobRole'])
        at_writer.writerow(['ActivityTypeID', 'TypeName', 'GeneralDetails'])
        act_writer.writerow(['ActivityID', 'ActivityTypeID', 'ActivityDate', 'SpecificDetails'])
        act_emp_writer.writerow(['ActivityID', 'EmployeeID'])
        act_anim_writer.writerow(['ActivityID', 'AnimalID'])
        
        roles = ['Zookeeper', 'Veterinarian', 'Trainer', 'Nutritionist', 'Manager']
        first_names = ['John', 'Jane', 'Michael', 'Emily', 'David', 'Sarah', 'James', 'Jessica', 'William', 'Ashley']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
        
        # 500 Employees
        for i in range(1, 501):
            fname = random.choice(first_names)
            lname = random.choice(last_names)
            role = random.choice(roles)
            emp_writer.writerow([i, fname, lname, role])
            
        # 500 Activity Types
        activities = ['Feeding', 'Training', 'Medical Checkup', 'Enrichment', 'Habitat Cleaning', 'Public Show', 'Weigh-in']
        for i in range(1, 501):
            t_name = random.choice(activities) + f" Type {i}"
            details = f"General procedure for {t_name}. Must strictly follow safety guidelines."
            at_writer.writerow([i, t_name, details])
            
        # 500 Activities with Many-to-Many mappings
        for i in range(1, 501):
            at_id = random.randint(1, 500)
            act_date = random_date(datetime(2023, 1, 1), datetime(2025, 12, 31)).strftime('%Y-%m-%d')
            spec_details = f"Specific observation for activity {i}."
            act_writer.writerow([i, at_id, act_date, spec_details])
            
            # 1 to 3 employees per activity
            num_employees = random.randint(1, 3)
            assigned_emps = random.sample(range(1, 501), num_employees)
            for e_id in assigned_emps:
                act_emp_writer.writerow([i, e_id])
                
            # 1 to 5 animals per activity
            num_animals = random.randint(1, 5)
            assigned_animals = random.sample(range(1, 20001), num_animals)
            for a_id in assigned_animals:
                act_anim_writer.writerow([i, a_id])

    print(f"Generated {employee_csv_path} with 500 records")
    print(f"Generated {activity_type_csv_path} with 500 records")
    print(f"Generated {activity_csv_path} with 500 records")
    print(f"Generated {activity_employee_csv_path} with variable records")
    print(f"Generated {activity_animal_csv_path} with variable records")

if __name__ == '__main__':
    main()
