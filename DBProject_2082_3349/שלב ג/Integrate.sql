-- Integrate.sql
-- סקריפט לשילוב מערכת המרפאה הווטרינרית לתוך מאגר הנתונים הקיים של גן החיות.

-- 1. יצירת טבלאות האגף החדש
CREATE TABLE VETERINARIAN (
    VetID INTEGER PRIMARY KEY,
    FirstName VARCHAR(100) NOT NULL,
    LastName VARCHAR(100) NOT NULL,
    LicenseNumber VARCHAR(50) UNIQUE NOT NULL,
    Specialization VARCHAR(100),
    HireDate DATE NOT NULL CHECK (HireDate <= CURRENT_DATE)
);

CREATE TABLE MEDICALVISIT (
    VisitID INTEGER PRIMARY KEY,
    VisitDate DATE NOT NULL CHECK (VisitDate <= CURRENT_DATE),
    Reason VARCHAR(255) NOT NULL,
    Summary TEXT,
    Cost NUMERIC(10,2) CHECK (Cost >= 0),
    AnimalID INTEGER NOT NULL,
    VetID INTEGER NOT NULL
);

CREATE TABLE TREATMENT (
    TreatmentID INTEGER PRIMARY KEY,
    Description VARCHAR(255) NOT NULL,
    Duration VARCHAR(50),
    Type VARCHAR(50),
    Severity VARCHAR(50) CHECK (Severity IN ('Low', 'Medium', 'High', 'Critical'))
);

CREATE TABLE MEDICATION (
    MedID INTEGER PRIMARY KEY,
    CommercialName VARCHAR(100) NOT NULL,
    ActiveIngredient VARCHAR(255),
    DosageUnit VARCHAR(50),
    ExpirationDate DATE NOT NULL CHECK (ExpirationDate >= '2020-01-01')
);

CREATE TABLE VACCINATION (
    VacID INTEGER PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Manufacturer VARCHAR(100),
    FrequencyMonths INTEGER CHECK (FrequencyMonths > 0),
    StorageTemp VARCHAR(50)
);

CREATE TABLE MIRSHAM_VISIT_TREATMENT (
    VisitID INTEGER NOT NULL,
    TreatmentID INTEGER NOT NULL,
    PRIMARY KEY (VisitID, TreatmentID)
);

CREATE TABLE HERGEL_TREATMENT_MEDICATION (
    TreatmentID INTEGER NOT NULL,
    MedID INTEGER NOT NULL,
    PRIMARY KEY (TreatmentID, MedID)
);

CREATE TABLE TREATMENT_VACCINATION (
    TreatmentID INTEGER NOT NULL,
    VacID INTEGER NOT NULL,
    PRIMARY KEY (TreatmentID, VacID)
);

-- 2. פקודות עיצוב טבלאות (ALTER) לאינטגרציה עם מסד הנתונים הקיים
-- מקשרים את הביקורים הרפואיים לטבלת החיות הקיימת שלנו ולטבלת הווטרינרים החדשה
ALTER TABLE MEDICALVISIT ADD CONSTRAINT fk_visit_animal FOREIGN KEY (AnimalID) REFERENCES ANIMAL(AnimalID) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE MEDICALVISIT ADD CONSTRAINT fk_visit_vet FOREIGN KEY (VetID) REFERENCES VETERINARIAN(VetID) ON DELETE CASCADE ON UPDATE CASCADE;

-- מפתחות זרים עבור טבלאות הקשר של האגף החדש
ALTER TABLE MIRSHAM_VISIT_TREATMENT ADD CONSTRAINT fk_mirsham_visit FOREIGN KEY (VisitID) REFERENCES MEDICALVISIT(VisitID) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE MIRSHAM_VISIT_TREATMENT ADD CONSTRAINT fk_mirsham_treatment FOREIGN KEY (TreatmentID) REFERENCES TREATMENT(TreatmentID) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE HERGEL_TREATMENT_MEDICATION ADD CONSTRAINT fk_hergel_treatment FOREIGN KEY (TreatmentID) REFERENCES TREATMENT(TreatmentID) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE HERGEL_TREATMENT_MEDICATION ADD CONSTRAINT fk_hergel_medication FOREIGN KEY (MedID) REFERENCES MEDICATION(MedID) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE TREATMENT_VACCINATION ADD CONSTRAINT fk_tv_treatment FOREIGN KEY (TreatmentID) REFERENCES TREATMENT(TreatmentID) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE TREATMENT_VACCINATION ADD CONSTRAINT fk_tv_vaccination FOREIGN KEY (VacID) REFERENCES VACCINATION(VacID) ON DELETE CASCADE ON UPDATE CASCADE;

-- הוספת אינדקס לשיפור ביצועים של שאילתות משותפות
CREATE INDEX idx_medicalvisit_animal ON MEDICALVISIT(AnimalID);

-- 3. הכנסת נתוני דוגמה לטבלאות החדשות כדי שניתן יהיה לבדוק את המבטים והשאילתות
-- (הנתונים מסתמכים על כך שיש חיות בטבלת ANIMAL עם מזהים 1, 2, 3)
INSERT INTO VETERINARIAN VALUES 
(1, 'John', 'Doe', 'VET123', 'Large Animals', '2015-05-10'),
(2, 'Jane', 'Smith', 'VET456', 'Avian', '2018-08-22'),
(3, 'Emily', 'Jones', 'VET789', 'Reptiles', '2020-11-01');

INSERT INTO MEDICALVISIT VALUES 
(1, CURRENT_DATE - INTERVAL '10 days', 'Routine check', 'All good', 100.00, 1, 1),
(2, CURRENT_DATE - INTERVAL '5 days', 'Limping', 'Sprained leg', 250.00, 2, 1),
(3, CURRENT_DATE - INTERVAL '2 days', 'Not eating', 'Digestive issue', 150.00, 3, 2);

INSERT INTO TREATMENT VALUES 
(1, 'Rest and observation', '1 week', 'Physical', 'Low'),
(2, 'Antibiotics course', '2 weeks', 'Medical', 'Medium'),
(3, 'Vaccination shot', '1 day', 'Preventative', 'Low');

INSERT INTO MEDICATION VALUES 
(1, 'Amoxicillin', 'Amoxicillin', '500mg', '2027-01-01'),
(2, 'Painkiller X', 'Ibuprofen', '200mg', '2026-12-31');

INSERT INTO VACCINATION VALUES 
(1, 'Rabies Vax', 'PharmaZ', 12, 'Cold Storage'),
(2, 'Avian Flu Vax', 'BirdMed', 6, 'Room Temp');

INSERT INTO MIRSHAM_VISIT_TREATMENT VALUES (1, 3), (2, 1), (3, 2);
INSERT INTO HERGEL_TREATMENT_MEDICATION VALUES (2, 1);
INSERT INTO TREATMENT_VACCINATION VALUES (3, 1);
