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

if __name__ == '__main__':
    main()
