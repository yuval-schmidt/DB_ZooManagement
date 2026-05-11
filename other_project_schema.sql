CREATE TABLE public.animal (
    animalid integer NOT NULL,
    name character varying(100) NOT NULL,
    species character varying(100) NOT NULL,
    birthdate date NOT NULL,
    gender character varying(20),
    weight numeric(5,2),
    CONSTRAINT animal_gender_check CHECK (((gender)::text = ANY ((ARRAY['Male'::character varying, 'Female'::character varying, 'Unknown'::character varying])::text[]))),
    CONSTRAINT animal_weight_check CHECK ((weight > (0)::numeric)),
    CONSTRAINT chk_animal_weight_range CHECK (((weight >= 0.01) AND (weight <= 999.99)))
);

CREATE TABLE public.hergel_treatment_medication (
    treatmentid integer NOT NULL,
    medid integer NOT NULL
);

CREATE TABLE public.medicalvisit (
    visitid integer NOT NULL,
    visitdate date NOT NULL,
    reason character varying(255) NOT NULL,
    summary text,
    cost numeric(10,2),
    animalid integer NOT NULL,
    vetid integer NOT NULL,
    CONSTRAINT chk_visit_not_future CHECK ((visitdate <= CURRENT_DATE)),
    CONSTRAINT medicalvisit_cost_check CHECK ((cost >= (0)::numeric))
);

CREATE TABLE public.medication (
    medid integer NOT NULL,
    commercialname character varying(100) NOT NULL,
    activeingredient character varying(255),
    dosageunit character varying(50),
    expirationdate date NOT NULL,
    CONSTRAINT chk_medication_min_expiration CHECK ((expirationdate >= '2020-01-01'::date))
);

CREATE TABLE public.mirsham_visit_treatment (
    visitid integer NOT NULL,
    treatmentid integer NOT NULL
);

CREATE TABLE public.treatment (
    treatmentid integer NOT NULL,
    description character varying(255) NOT NULL,
    duration character varying(50),
    type character varying(50),
    severity character varying(50),
    CONSTRAINT treatment_severity_check CHECK (((severity)::text = ANY ((ARRAY['Low'::character varying, 'Medium'::character varying, 'High'::character varying, 'Critical'::character varying])::text[])))
);

CREATE TABLE public.treatment_vaccination (
    treatmentid integer NOT NULL,
    vacid integer NOT NULL
);

CREATE TABLE public.vaccination (
    vacid integer NOT NULL,
    name character varying(100) NOT NULL,
    manufacturer character varying(100),
    frequencymonths integer,
    storagetemp character varying(50),
    CONSTRAINT vaccination_frequencymonths_check CHECK ((frequencymonths > 0))
);

CREATE TABLE public.veterinarian (
    vetid integer NOT NULL,
    firstname character varying(100) NOT NULL,
    lastname character varying(100) NOT NULL,
    licensenumber character varying(50) NOT NULL,
    specialization character varying(100),
    hiredate date NOT NULL,
    CONSTRAINT veterinarian_hiredate_check CHECK ((hiredate <= CURRENT_DATE))
);

