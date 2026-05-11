ALTER TABLE ONLY public.animal
    ADD CONSTRAINT animal_pkey PRIMARY KEY (animalid);

ALTER TABLE ONLY public.animal DROP CONSTRAINT animal_pkey;

ALTER TABLE ONLY public.hergel_treatment_medication
    ADD CONSTRAINT hergel_treatment_medication_pkey PRIMARY KEY (treatmentid, medid);

ALTER TABLE ONLY public.hergel_treatment_medication DROP CONSTRAINT hergel_treatment_medication_pkey;

ALTER TABLE ONLY public.medicalvisit
    ADD CONSTRAINT medicalvisit_pkey PRIMARY KEY (visitid);

ALTER TABLE ONLY public.medicalvisit DROP CONSTRAINT medicalvisit_pkey;

ALTER TABLE ONLY public.medication
    ADD CONSTRAINT medication_pkey PRIMARY KEY (medid);

ALTER TABLE ONLY public.medication DROP CONSTRAINT medication_pkey;

ALTER TABLE ONLY public.mirsham_visit_treatment
    ADD CONSTRAINT mirsham_visit_treatment_pkey PRIMARY KEY (visitid, treatmentid);

ALTER TABLE ONLY public.mirsham_visit_treatment DROP CONSTRAINT mirsham_visit_treatment_pkey;

ALTER TABLE ONLY public.treatment
    ADD CONSTRAINT treatment_pkey PRIMARY KEY (treatmentid);

ALTER TABLE ONLY public.treatment DROP CONSTRAINT treatment_pkey;

ALTER TABLE ONLY public.treatment_vaccination
    ADD CONSTRAINT treatment_vaccination_pkey PRIMARY KEY (treatmentid, vacid);

ALTER TABLE ONLY public.treatment_vaccination DROP CONSTRAINT treatment_vaccination_pkey;

ALTER TABLE ONLY public.medicalvisit
    ADD CONSTRAINT uq_one_visit_per_animal_per_vet_per_day UNIQUE (animalid, vetid, visitdate);

ALTER TABLE ONLY public.medicalvisit DROP CONSTRAINT uq_one_visit_per_animal_per_vet_per_day;

ALTER TABLE ONLY public.vaccination
    ADD CONSTRAINT vaccination_pkey PRIMARY KEY (vacid);

ALTER TABLE ONLY public.vaccination DROP CONSTRAINT vaccination_pkey;

ALTER TABLE ONLY public.veterinarian
    ADD CONSTRAINT veterinarian_licensenumber_key UNIQUE (licensenumber);

ALTER TABLE ONLY public.veterinarian DROP CONSTRAINT veterinarian_licensenumber_key;

ALTER TABLE ONLY public.veterinarian
    ADD CONSTRAINT veterinarian_pkey PRIMARY KEY (vetid);

ALTER TABLE ONLY public.veterinarian DROP CONSTRAINT veterinarian_pkey;

ALTER TABLE ONLY public.hergel_treatment_medication
    ADD CONSTRAINT hergel_treatment_medication_medid_fkey FOREIGN KEY (medid) REFERENCES public.medication(medid) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE ONLY public.hergel_treatment_medication DROP CONSTRAINT hergel_treatment_medication_medid_fkey;

ALTER TABLE ONLY public.hergel_treatment_medication
    ADD CONSTRAINT hergel_treatment_medication_treatmentid_fkey FOREIGN KEY (treatmentid) REFERENCES public.treatment(treatmentid) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE ONLY public.hergel_treatment_medication DROP CONSTRAINT hergel_treatment_medication_treatmentid_fkey;

ALTER TABLE ONLY public.medicalvisit
    ADD CONSTRAINT medicalvisit_animalid_fkey FOREIGN KEY (animalid) REFERENCES public.animal(animalid) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE ONLY public.medicalvisit DROP CONSTRAINT medicalvisit_animalid_fkey;

ALTER TABLE ONLY public.medicalvisit
    ADD CONSTRAINT medicalvisit_vetid_fkey FOREIGN KEY (vetid) REFERENCES public.veterinarian(vetid) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE ONLY public.medicalvisit DROP CONSTRAINT medicalvisit_vetid_fkey;

ALTER TABLE ONLY public.mirsham_visit_treatment
    ADD CONSTRAINT mirsham_visit_treatment_treatmentid_fkey FOREIGN KEY (treatmentid) REFERENCES public.treatment(treatmentid) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE ONLY public.mirsham_visit_treatment DROP CONSTRAINT mirsham_visit_treatment_treatmentid_fkey;

ALTER TABLE ONLY public.mirsham_visit_treatment
    ADD CONSTRAINT mirsham_visit_treatment_visitid_fkey FOREIGN KEY (visitid) REFERENCES public.medicalvisit(visitid) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE ONLY public.mirsham_visit_treatment DROP CONSTRAINT mirsham_visit_treatment_visitid_fkey;

ALTER TABLE ONLY public.treatment_vaccination
    ADD CONSTRAINT treatment_vaccination_treatmentid_fkey FOREIGN KEY (treatmentid) REFERENCES public.treatment(treatmentid) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE ONLY public.treatment_vaccination DROP CONSTRAINT treatment_vaccination_treatmentid_fkey;

ALTER TABLE ONLY public.treatment_vaccination
    ADD CONSTRAINT treatment_vaccination_vacid_fkey FOREIGN KEY (vacid) REFERENCES public.vaccination(vacid) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE ONLY public.treatment_vaccination DROP CONSTRAINT treatment_vaccination_vacid_fkey;

