"""Table definitions: columns, primary keys, foreign keys, display labels."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


FieldType = Literal["text", "int", "float", "date", "fk", "readonly"]


@dataclass
class ForeignKey:
    column: str
    ref_table: str
    ref_pk: str
    display_sql: str
    grid_alias: str
    grid_label: str


@dataclass
class ColumnDef:
    name: str
    label: str
    field_type: FieldType = "text"
    choices: list[str] | None = None


@dataclass
class TableDef:
    key: str
    table: str
    display_name: str
    pk: list[str]
    columns: list[ColumnDef]
    foreign_keys: list[ForeignKey] = field(default_factory=list)
    read_only: bool = False


def _fk(column, ref_table, ref_pk, display_sql, grid_alias, grid_label):
    return ForeignKey(column, ref_table, ref_pk, display_sql, grid_alias, grid_label)


TABLES: dict[str, TableDef] = {
    "HABITAT": TableDef(
        "HABITAT", "habitat", "בתי גידול (Habitat)", ["habitatid"],
        [
            ColumnDef("habitatname", "שם בית גידול"),
            ColumnDef("climatetype", "סוג אקלים"),
            ColumnDef("maxcapacity", "קיבולת מקסימלית", "int"),
        ],
    ),
    "SPECIES": TableDef(
        "SPECIES", "species", "מינים (Species)", ["speciesid"],
        [
            ColumnDef("commonname", "שם נפוץ"),
            ColumnDef("scientificname", "שם מדעי"),
            ColumnDef("conservationstatus", "סטטוס שימור"),
        ],
    ),
    "DIETPLAN": TableDef(
        "DIETPLAN", "dietplan", "תוכניות תזונה (Diet Plan)", ["dietplanid"],
        [
            ColumnDef("planname", "שם תוכנית"),
            ColumnDef("dailycost", "עלות יומית", "float"),
        ],
    ),
    "ANIMAL": TableDef(
        "ANIMAL", "animal", "חיות (Animal)", ["animalid"],
        [
            ColumnDef("name", "שם החיה"),
            ColumnDef("dateofbirth", "תאריך לידה", "date"),
            ColumnDef("gender", "מין"),
        ],
        [
            _fk("habitatid", "habitat", "habitatid", "habitatname", "habitat_name", "בית גידול"),
            _fk("speciesid", "species", "speciesid", "commonname", "species_name", "מין (Species)"),
            _fk("dietplanid", "dietplan", "dietplanid", "planname", "diet_name", "תוכנית תזונה"),
        ],
    ),
    "HEALTHRECORD": TableDef(
        "HEALTHRECORD", "healthrecord", "רשומות בריאות", ["recordid"],
        [
            ColumnDef("checkupdate", "תאריך בדיקה", "date"),
            ColumnDef("weight", "משקל (ק\"ג)", "float"),
            ColumnDef(
                "healthstatus", "סטטוס בריאות", "text",
                ["Healthy", "Sick", "Recovering", "Critical", "Deceased"],
            ),
        ],
        [_fk("animalid", "animal", "animalid", "name", "animal_name", "שם החיה")],
    ),
    "DAILYFEEDING": TableDef(
        "DAILYFEEDING", "dailyfeeding", "האכלה יומית", ["feedingid"],
        [
            ColumnDef("feedingdate", "תאריך האכלה", "date"),
            ColumnDef("foodconsumedqty", "כמות מזון", "float"),
        ],
        [_fk("animalid", "animal", "animalid", "name", "animal_name", "שם החיה")],
    ),
    "EMPLOYEE": TableDef(
        "EMPLOYEE", "employee", "עובדים", ["employeeid"],
        [
            ColumnDef("firstname", "שם פרטי"),
            ColumnDef("lastname", "שם משפחה"),
            ColumnDef("jobrole", "תפקיד"),
        ],
    ),
    "ACTIVITY_TYPE": TableDef(
        "ACTIVITY_TYPE", "activity_type", "סוגי פעילות", ["activitytypeid"],
        [
            ColumnDef("typename", "שם סוג"),
            ColumnDef("generaldetails", "פרטים כלליים"),
        ],
    ),
    "ACTIVITY": TableDef(
        "ACTIVITY", "activity", "פעילויות", ["activityid"],
        [
            ColumnDef("activitydate", "תאריך פעילות", "date"),
            ColumnDef("specificdetails", "פרטים"),
        ],
        [_fk("activitytypeid", "activity_type", "activitytypeid", "typename", "type_name", "סוג פעילות")],
    ),
    "ACTIVITY_EMPLOYEE": TableDef(
        "ACTIVITY_EMPLOYEE", "activity_employee", "פעילות–עובד (קשר)", ["activityid", "employeeid"],
        [],
        [
            _fk("activityid", "activity", "activityid",
                "activityid::text || ' – ' || activitydate::text", "activity_label", "פעילות"),
            _fk("employeeid", "employee", "employeeid",
                "firstname || ' ' || lastname", "employee_name", "עובד"),
        ],
    ),
    "ACTIVITY_ANIMAL": TableDef(
        "ACTIVITY_ANIMAL", "activity_animal", "פעילות–חיה (קשר)", ["activityid", "animalid"],
        [],
        [
            _fk("activityid", "activity", "activityid",
                "activityid::text || ' – ' || activitydate::text", "activity_label", "פעילות"),
            _fk("animalid", "animal", "animalid", "name", "animal_name", "חיה"),
        ],
    ),
    "VETERINARIAN": TableDef(
        "VETERINARIAN", "veterinarian", "וטרינרים", ["vetid"],
        [
            ColumnDef("firstname", "שם פרטי"),
            ColumnDef("lastname", "שם משפחה"),
            ColumnDef("licensenumber", "מספר רישיון"),
            ColumnDef("specialization", "התמחות"),
            ColumnDef("hiredate", "תאריך גיוס", "date"),
        ],
    ),
    "MEDICALVISIT": TableDef(
        "MEDICALVISIT", "medicalvisit", "ביקורי רפואה", ["visitid"],
        [
            ColumnDef("visitdate", "תאריך ביקור", "date"),
            ColumnDef("reason", "סיבת ביקור"),
            ColumnDef("summary", "סיכום"),
            ColumnDef("cost", "עלות", "float"),
        ],
        [
            _fk("animalid", "animal", "animalid", "name", "animal_name", "חיה"),
            _fk("vetid", "veterinarian", "vetid",
                "firstname || ' ' || lastname", "vet_name", "וטרינר"),
        ],
    ),
    "TREATMENT": TableDef(
        "TREATMENT", "treatment", "טיפולים", ["treatmentid"],
        [
            ColumnDef("description", "תיאור"),
            ColumnDef("duration", "משך"),
            ColumnDef("type", "סוג"),
            ColumnDef("severity", "חומרה", "text", ["Low", "Medium", "High", "Critical"]),
        ],
    ),
    "MEDICATION": TableDef(
        "MEDICATION", "medication", "תרופות", ["medid"],
        [
            ColumnDef("commercialname", "שם מסחרי"),
            ColumnDef("activeingredient", "חומר פעיל"),
            ColumnDef("dosageunit", "יחידת מינון"),
            ColumnDef("expirationdate", "תאריך תפוגה", "date"),
        ],
    ),
    "VACCINATION": TableDef(
        "VACCINATION", "vaccination", "חיסונים", ["vacid"],
        [
            ColumnDef("name", "שם חיסון"),
            ColumnDef("manufacturer", "יצרן"),
            ColumnDef("frequencymonths", "תדירות (חודשים)", "int"),
            ColumnDef("storagetemp", "טמפרטורת אחסון"),
        ],
    ),
    "MIRSHAM_VISIT_TREATMENT": TableDef(
        "MIRSHAM_VISIT_TREATMENT", "mirsham_visit_treatment",
        "ביקור–טיפול (קשר)", ["visitid", "treatmentid"],
        [],
        [
            _fk("visitid", "medicalvisit", "visitid",
                "visitid::text || ' – ' || reason", "visit_label", "ביקור רפואי"),
            _fk("treatmentid", "treatment", "treatmentid", "description", "treatment_name", "טיפול"),
        ],
    ),
    "HERGEL_TREATMENT_MEDICATION": TableDef(
        "HERGEL_TREATMENT_MEDICATION", "hergel_treatment_medication",
        "טיפול–תרופה (קשר)", ["treatmentid", "medid"],
        [],
        [
            _fk("treatmentid", "treatment", "treatmentid", "description", "treatment_name", "טיפול"),
            _fk("medid", "medication", "medid", "commercialname", "med_name", "תרופה"),
        ],
    ),
    "TREATMENT_VACCINATION": TableDef(
        "TREATMENT_VACCINATION", "treatment_vaccination",
        "טיפול–חיסון (קשר)", ["treatmentid", "vacid"],
        [],
        [
            _fk("treatmentid", "treatment", "treatmentid", "description", "treatment_name", "טיפול"),
            _fk("vacid", "vaccination", "vacid", "name", "vac_name", "חיסון"),
        ],
    ),
    "HABITAT_CAPACITY_LOG": TableDef(
        "HABITAT_CAPACITY_LOG", "habitat_capacity_log",
        "יומן שינוי קיבולת (Trigger)", ["logid"],
        [
            ColumnDef("oldcapacity", "קיבולת קודמת", "readonly"),
            ColumnDef("newcapacity", "קיבולת חדשה", "readonly"),
            ColumnDef("changedate", "תאריך שינוי", "readonly"),
        ],
        [_fk("habitatid", "habitat", "habitatid", "habitatname", "habitat_name", "בית גידול")],
        read_only=True,
    ),
}


TABLE_GROUPS = {
    "ניהול גן החיות": ["HABITAT", "SPECIES", "DIETPLAN", "ANIMAL", "HEALTHRECORD", "DAILYFEEDING"],
    "צוות ופעילויות": ["EMPLOYEE", "ACTIVITY_TYPE", "ACTIVITY", "ACTIVITY_EMPLOYEE", "ACTIVITY_ANIMAL"],
    "מחלקה וטרינרית": [
        "VETERINARIAN", "MEDICALVISIT", "TREATMENT", "MEDICATION", "VACCINATION",
        "MIRSHAM_VISIT_TREATMENT", "HERGEL_TREATMENT_MEDICATION", "TREATMENT_VACCINATION",
    ],
    "מערכת (יומנים)": ["HABITAT_CAPACITY_LOG"],
}

def _fk_label_sql(alias: str, ref_table: str) -> str:
    """Human-readable label for a FK join (PostgreSQL stores unquoted names as lowercase)."""
    ref = ref_table.lower()
    mapping = {
        "habitat": f"{alias}.habitatname",
        "species": f"{alias}.commonname",
        "dietplan": f"{alias}.planname",
        "animal": f"{alias}.name",
        "activity_type": f"{alias}.typename",
        "employee": f"({alias}.firstname || ' ' || {alias}.lastname)",
        "activity": f"({alias}.activityid::text || ' – ' || {alias}.activitydate::text)",
        "veterinarian": f"({alias}.firstname || ' ' || {alias}.lastname)",
        "medicalvisit": f"({alias}.visitid::text || ' – ' || {alias}.reason)",
        "treatment": f"{alias}.description",
        "medication": f"{alias}.commercialname",
        "vaccination": f"{alias}.name",
    }
    expr = mapping.get(ref, f"{alias}.{ref_table}")
    return expr


def build_select_sql(tdef: TableDef) -> tuple[str, list[str]]:
    """Build SELECT with JOINs; returns SQL and ordered display column names (no raw IDs)."""
    t = tdef.table.lower()
    selects: list[str] = []
    headers: list[str] = []
    joins: list[str] = []

    for col in tdef.columns:
        selects.append(f"t.{col.name}")
        headers.append(col.label)

    for i, fk in enumerate(tdef.foreign_keys):
        alias = f"fk{i}"
        ref = fk.ref_table.lower()
        label_expr = _fk_label_sql(alias, ref)
        selects.append(f"{label_expr} AS {fk.grid_alias}")
        headers.append(fk.grid_label)
        joins.append(
            f"LEFT JOIN {ref} {alias} ON t.{fk.column} = {alias}.{fk.ref_pk}"
        )

    pk_select = ", ".join(f"t.{pk}" for pk in tdef.pk)
    sql = (
        f"SELECT {pk_select}, {', '.join(selects)} FROM {t} t "
        + " ".join(joins)
        + f" ORDER BY {', '.join(f't.{pk}' for pk in tdef.pk)}"
    )
    return sql, headers


def all_editable_columns(tdef: TableDef) -> list[ColumnDef]:
    cols = list(tdef.columns)
    for fk in tdef.foreign_keys:
        cols.append(ColumnDef(fk.column, fk.grid_label, "fk"))
    return cols


def pk_labels(tdef: TableDef) -> list[str]:
    labels = {
        "habitatid": "מזהה בית גידול",
        "speciesid": "מזהה מין",
        "dietplanid": "מזהה תוכנית תזונה",
        "animalid": "מזהה חיה",
        "recordid": "מזהה רשומה",
        "feedingid": "מזהה האכלה",
        "employeeid": "מזהה עובד",
        "activitytypeid": "מזהה סוג פעילות",
        "activityid": "מזהה פעילות",
        "vetid": "מזהה וטרינר",
        "visitid": "מזהה ביקור",
        "treatmentid": "מזהה טיפול",
        "medid": "מזהה תרופה",
        "vacid": "מזהה חיסון",
        "logid": "מזהה יומן",
    }
    return [labels.get(pk, pk) for pk in tdef.pk]
