-- Data Dictionary & Explanations: HABITAT Table
-- This table stores information about the various animal habitats in the zoo, including name, climate type, and maximum capacity.
CREATE TABLE HABITAT
(
  HabitatID INT NOT NULL,
  HabitatName VARCHAR2(50) NOT NULL,
  ClimateType VARCHAR2(50) NOT NULL,
  MaxCapacity INT NOT NULL CHECK (MaxCapacity > 0),
  PRIMARY KEY (HabitatID)
);

-- Data Dictionary & Explanations: SPECIES Table
-- This table stores information about animal species, such as their common and scientific names, and their conservation status.
CREATE TABLE SPECIES
(
  SpeciesID INT NOT NULL,
  CommonName VARCHAR2(50) NOT NULL,
  ScientificName VARCHAR2(50) NOT NULL,
  ConservationStatus VARCHAR2(50) NOT NULL,
  PRIMARY KEY (SpeciesID)
);

-- Data Dictionary & Explanations: DIETPLAN Table
-- This table defines the possible nutritional diet plans and their daily cost.
CREATE TABLE DIETPLAN
(
  DietPlanID INT NOT NULL,
  PlanName VARCHAR2(50) NOT NULL,
  DailyCost NUMERIC(6,2) NOT NULL CHECK (DailyCost >= 0),
  PRIMARY KEY (DietPlanID)
);

-- Data Dictionary & Explanations: ANIMAL Table
-- This table records each individual animal, its birth details, gender, and its assignment to a habitat, species, and diet plan.
CREATE TABLE ANIMAL
(
  AnimalID INT NOT NULL,
  Name VARCHAR2(50) NOT NULL,
  DateOfBirth DATE NOT NULL,
  Gender VARCHAR2(50) NOT NULL,
  HabitatID INT NOT NULL,
  SpeciesID INT NOT NULL,
  DietPlanID INT NOT NULL,
  PRIMARY KEY (AnimalID),
  FOREIGN KEY (HabitatID) REFERENCES HABITAT(HabitatID),
  FOREIGN KEY (SpeciesID) REFERENCES SPECIES(SpeciesID),
  FOREIGN KEY (DietPlanID) REFERENCES DIETPLAN(DietPlanID)
);

-- Data Dictionary & Explanations: HEALTHRECORD Table
-- This table records periodic checkups, health status, and recorded weight for an animal at a specific date.
CREATE TABLE HEALTHRECORD
(
  RecordID INT NOT NULL,
  CheckupDate DATE NOT NULL,
  Weight NUMERIC(6,2) NOT NULL CHECK (Weight > 0),
  HealthStatus VARCHAR2(50) NOT NULL,
  AnimalID INT NOT NULL,
  PRIMARY KEY (RecordID),
  FOREIGN KEY (AnimalID) REFERENCES ANIMAL(AnimalID)
);

-- Data Dictionary & Explanations: DAILYFEEDING Table
-- This table is used for daily tracking of the actual food quantity consumed by each animal on different days.
CREATE TABLE DAILYFEEDING
(
  FeedingID INT NOT NULL,
  FeedingDate DATE NOT NULL,
  FoodConsumedQty NUMERIC(5,2) NOT NULL CHECK (FoodConsumedQty >= 0),
  AnimalID INT NOT NULL,
  PRIMARY KEY (FeedingID),
  FOREIGN KEY (AnimalID) REFERENCES ANIMAL(AnimalID)
);

-- Data Dictionary & Explanations: EMPLOYEE Table
-- This table stores information about the zoo staff members.
CREATE TABLE EMPLOYEE
(
  EmployeeID INT NOT NULL,
  FirstName VARCHAR2(50) NOT NULL,
  LastName VARCHAR2(50) NOT NULL,
  JobRole VARCHAR2(50) NOT NULL,
  PRIMARY KEY (EmployeeID)
);

-- Data Dictionary & Explanations: ACTIVITY_TYPE Table
-- This table defines the various types of activities and general details.
CREATE TABLE ACTIVITY_TYPE
(
  ActivityTypeID INT NOT NULL,
  TypeName VARCHAR2(50) NOT NULL,
  GeneralDetails VARCHAR2(255) NOT NULL,
  PRIMARY KEY (ActivityTypeID)
);

-- Data Dictionary & Explanations: ACTIVITY Table
-- This table logs individual activity instances.
CREATE TABLE ACTIVITY
(
  ActivityID INT NOT NULL,
  ActivityTypeID INT NOT NULL,
  ActivityDate DATE NOT NULL,
  SpecificDetails VARCHAR2(255) NOT NULL,
  PRIMARY KEY (ActivityID),
  FOREIGN KEY (ActivityTypeID) REFERENCES ACTIVITY_TYPE(ActivityTypeID)
);

-- Data Dictionary & Explanations: ACTIVITY_EMPLOYEE Table
-- Many-to-Many junction mapping multiple employees performing an activity.
CREATE TABLE ACTIVITY_EMPLOYEE
(
  ActivityID INT NOT NULL,
  EmployeeID INT NOT NULL,
  PRIMARY KEY (ActivityID, EmployeeID),
  FOREIGN KEY (ActivityID) REFERENCES ACTIVITY(ActivityID),
  FOREIGN KEY (EmployeeID) REFERENCES EMPLOYEE(EmployeeID)
);

-- Data Dictionary & Explanations: ACTIVITY_ANIMAL Table
-- Many-to-Many junction mapping multiple animals participating in an activity.
CREATE TABLE ACTIVITY_ANIMAL
(
  ActivityID INT NOT NULL,
  AnimalID INT NOT NULL,
  PRIMARY KEY (ActivityID, AnimalID),
  FOREIGN KEY (ActivityID) REFERENCES ACTIVITY(ActivityID),
  FOREIGN KEY (AnimalID) REFERENCES ANIMAL(AnimalID)
);