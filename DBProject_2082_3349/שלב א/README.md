# Zoo Animal Management Data System - Stage A Report

## Cover Page
**Project Topic:** Zoo Animal Management
**Date:** March 25, 2026

## Table of Contents
1. [Introduction](#introduction)
2. [System Characterization (UI)](#system-characterization)
3. [Database Design & Dictionary](#database-design--dictionary)
4. [ERD & DSD Diagrams](#erd--dsd-diagrams)
5. [Design Decisions & Justifications](#design-decisions--justifications)

## Introduction
The Zoo Animal Management database system is designed to streamline and organize the complex processes of managing a modern zoological facility. It tracks essential data such as animals, their species, living habitats, diet plans, health records, and daily feeding logs. The system enables zoo staff to accurately monitor animal nutrition, effectively allocate habitats, and ensure up-to-date veterinary health tracking.

## System Characterization
The system is built around 4 primary screens integrated into a main Google AI Studio UI concept:
1. **Animal Registry Dashboard:** Allows keepers to add new animals, view animal details (Gender, Species, Habitat, Date of Birth), and quickly locate specific animals based on their unique IDs.
2. **Veterinary Checkup Interface:** A dedicated medical screen to log and track `HEALTHRECORD` details. Staff can monitor the checkup dates, animal weights, and current health status.
3. **Feeding & Nutrition Manager:** Cross-references `DIETPLAN` parameters and logs real-time `DAILYFEEDING` data to ensure proper daily nutrition is achieved without exceeding resource bounds.
4. **Habitat Allocation Screen:** A spatial management dashboard summarizing `HABITAT` capacity, tracking the specific climate conditions, and warning if a habitat exceeds `MaxCapacity`.

*Link to AI Studio UI Design:* `[Placeholder for AI Studio Project Link]`

## Database Design & Dictionary
The database consists of 6 primary entities normalized strictly to 3NF. No simple lookup tables (e.g., gender enums) were counted towards the 6 main tables.

### Data Dictionary

| Table Name | Description |
|---|---|
| **HABITAT** | Represents the physical living areas within the zoo. Contains specific climate controls and capacity restrictions. |
| **SPECIES** | Taxonomic data for animals, outlining their common name, scientific name, and current conservation status. |
| **DIETPLAN** | Cost tracking and dietary configuration identifying what animals eat and the daily cost parameter. |
| **ANIMAL** | The core entity representing individual animals. Tracks biological data and links to habitat, species, and diet. |
| **HEALTHRECORD** | Tracks individual veterinary checkups, monitoring weight and health status chronologically. |
| **DAILYFEEDING** | Logs the exact date and quantity of food consumed by an animal to ensure diet compliance. |

#### Entities and Attributes
- **HABITAT:** `HabitatID` (PK), `HabitatName`, `ClimateType`, `MaxCapacity`
- **SPECIES:** `SpeciesID` (PK), `CommonName`, `ScientificName`, `ConservationStatus`
- **DIETPLAN:** `DietPlanID` (PK), `PlanName`, `DailyCost`
- **ANIMAL:** `AnimalID` (PK), `Name`, `DateOfBirth` (DATE), `Gender`, `HabitatID` (FK), `SpeciesID` (FK), `DietPlanID` (FK)
- **HEALTHRECORD:** `RecordID` (PK), `CheckupDate` (DATE), `Weight`, `HealthStatus`, `AnimalID` (FK)
- **DAILYFEEDING:** `FeedingID` (PK), `FeedingDate` (DATE), `FoodConsumedQty`, `AnimalID` (FK)

## ERD & DSD Diagrams
*(Screenshots from ERD Plus and DSD schemas to be pasted here)*
`![ERD Placeholder](erd.png)`
`![DSD Placeholder](RelationalSchema.png)`

## Design Decisions & Justifications
- **Normalization (3NF):** We eliminated transitive dependencies by separating `DIETPLAN` from `ANIMAL`. Rather than storing diet cost directly on the animal, it references the plan. `SPECIES` is separated so the conservation status is logically tied to the species, not the individual animal.
- **Date Fields (3 Total):** We utilized `DateOfBirth` in the `ANIMAL` table to calculate exact age for developmental tracking, `CheckupDate` in `HEALTHRECORD` for time-series medical tracking, and `FeedingDate` in `DAILYFEEDING`.
- **Constraint Implementations:** Strong `CHECK` constraints prevent negative or zero values on logical attributes (e.g., `MaxCapacity > 0`, `Weight > 0`, `DailyCost >= 0`). This enforces strict data integrity on insertion parameters.
- **Data Volume Strategy:** Python generation was leveraged to securely scale the `ANIMAL` and `HEALTHRECORD` tables past 20,000 respective rows to stress-test future DB performance capabilities. Mockaroo and Manual insertions populate the remaining foundation tables.
