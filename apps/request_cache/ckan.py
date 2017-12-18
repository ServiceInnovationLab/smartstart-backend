# -*- coding: utf-8 -*-
from django.conf import settings


RESULT_COLUMNS = """
    "FSD_ID",
    "PROVIDER_NAME",
    "ORGANISATION_PURPOSE",
    "SERVICE_NAME",
    "SERVICE_DETAIL",
    "PHYSICAL_ADDRESS",
    "LATITUDE",
    "LONGITUDE",
    "PROVIDER_WEBSITE_1",
    "PUBLISHED_CONTACT_EMAIL_1",
    "PUBLISHED_PHONE_1",
    "PROVIDER_CONTACT_AVAILABILITY"
"""

SKIP_NULL_RESULTS = """
  "LATITUDE" IS NOT NULL
    AND
  "LONGITUDE" IS NOT NULL
    AND
  "LATITUDE" != '0'
    AND
  "LONGITUDE" != '0'
"""

ORDER_BY = 'ORDER BY "LONGITUDE", "FSD_ID"'

SQL_SUBST = {
    'fields': RESULT_COLUMNS,
    'dataset': settings.LBS_DATASET,
    'skip_null_results': SKIP_NULL_RESULTS,
    'orderby': ORDER_BY,
}

# Using SELECT DISTINCT (and not trying to return catergory data) means that
# duplicate entries (across returned values) will be dropped.

SQL_QUERIES = {
    'lbs_parenting_support': """
        SELECT DISTINCT {fields}
        FROM {dataset}
        WHERE {skip_null_results} AND
        (
            "LEVEL_2_CATEGORY" LIKE '%Babies and Toddlers 0-5%'
          OR
            "LEVEL_2_CATEGORY" LIKE '%Family / Whanau Support%'
          OR
            "LEVEL_2_CATEGORY" LIKE '%Parenting - Skills and Support%'
          OR
            "LEVEL_2_CATEGORY" LIKE '%Helplines - Parenting%'
          OR
            "LEVEL_2_CATEGORY" LIKE '%Support Groups - Parents%'
        ) AND (
            LOWER("SERVICE_DETAIL") NOT LIKE '%child%care%'
          AND
            LOWER("SERVICE_DETAIL") NOT LIKE '%toys%'
          AND
            LOWER("SERVICE_DETAIL") NOT LIKE '%kindergarten%'
          AND
            LOWER("SERVICE_DETAIL") NOT LIKE '%play%group%'
          AND
            LOWER("SERVICE_DETAIL") NOT LIKE '%students%'
          AND
            LOWER("SERVICE_DETAIL") NOT LIKE '%social%work%'
          AND
            LOWER("SERVICE_DETAIL") NOT LIKE '%older people%'
          AND
            LOWER("SERVICE_DETAIL") NOT LIKE '%adolescen%'
          AND
            LOWER("SERVICE_DETAIL") NOT LIKE '%counselling%'
          AND
            LOWER("SERVICE_DETAIL") NOT LIKE '%therap%'
          AND
            LOWER("SERVICE_DETAIL") NOT LIKE '%mediat%'
          AND
            LOWER("SERVICE_DETAIL") NOT LIKE '%legal%'
          AND
            LOWER("SERVICE_DETAIL") NOT LIKE '%school%'
          AND
            LOWER("SERVICE_DETAIL") NOT LIKE '%budget%'
          AND
            LOWER("SERVICE_DETAIL") NOT LIKE '%mental health%'
          AND
            LOWER("SERVICE_NAME") NOT LIKE '%teen%'
          AND
            LOWER("SERVICE_NAME") NOT LIKE '%play%'
        ) AND (
            LOWER("SERVICE_DETAIL") LIKE '%parent%'
          OR
            LOWER("ORGANISATION_PURPOSE") LIKE '%parent%'
        )
        {orderby}
    """,

    "lbs_early_education": """
        SELECT DISTINCT {fields}
        FROM {dataset}
        WHERE {skip_null_results} AND
        (
            LOWER("SERVICE_DETAIL") NOT LIKE '%after%school%'
          AND
            LOWER("ORGANISATION_PURPOSE") NOT LIKE '%after%school%'
        ) AND (
          "LEVEL_2_CATEGORY" LIKE '%Preschool / Early Childhood Education%'
        )
        {orderby}
    """,

    "lbs_breastfeeding": """
        SELECT DISTINCT {fields}
        FROM {dataset}
        WHERE {skip_null_results} AND
        (
            LOWER("SERVICE_DETAIL") LIKE '%breast%fe%'
          OR
            LOWER("ORGANISATION_PURPOSE") LIKE '%breast%fe%'
          OR
            LOWER("SERVICE_DETAIL") LIKE '%lactation%'
          OR
            "LEVEL_2_CATEGORY" LIKE '%Breast Feeding Support%'
        )
        {orderby}
    """,

    "lbs_antenatal": """
        SELECT DISTINCT {fields}
        FROM {dataset}
        WHERE {skip_null_results} AND
        (
            LOWER("SERVICE_DETAIL") LIKE '%ante%natal%'
          OR
            LOWER("ORGANISATION_PURPOSE") LIKE '%ante%natal%'
        ) AND (
            LOWER("PROVIDER_NAME") NOT LIKE '%postnatal%'
        ) AND (
            "LEVEL_2_CATEGORY" LIKE '%Pregnancy and Childbirth%'
          OR
            "LEVEL_2_CATEGORY" LIKE '%Well Child Health (Tamariki Ora)%'
          OR
            LOWER("PROVIDER_NAME") LIKE '%plunket%'
        )
        {orderby}
    """,

    "lbs_mental_health": """
        SELECT DISTINCT {fields}
        FROM {dataset}
        WHERE {skip_null_results} AND
        (
            LOWER("SERVICE_DETAIL") NOT LIKE '%eating%'
          AND
            LOWER("ORGANISATION_PURPOSE") NOT LIKE '%eating%'
          AND
            LOWER("SERVICE_DETAIL") NOT LIKE '%sexual%'
          AND
            LOWER("ORGANISATION_PURPOSE") NOT LIKE '%sexual%'
          AND
            LOWER("SERVICE_DETAIL") NOT LIKE '%youth%'
          AND
            LOWER("ORGANISATION_PURPOSE") NOT LIKE '%youth%'
          AND
            LOWER("SERVICE_DETAIL") NOT LIKE '%teen%'
          AND
            LOWER("ORGANISATION_PURPOSE") NOT LIKE '%teen%'
          AND
            LOWER("SERVICE_DETAIL") NOT LIKE '%workplace%'
          AND
            LOWER("ORGANISATION_PURPOSE") NOT LIKE '%workplace%'
          AND
            LOWER("SERVICE_DETAIL") NOT LIKE '%gender%'
          AND
            LOWER("ORGANISATION_PURPOSE") NOT LIKE '%gender%'
          AND
            LOWER("SERVICE_DETAIL") NOT LIKE '%course%'
          AND
            LOWER("ORGANISATION_PURPOSE") NOT LIKE '%course%'
          AND
            LOWER("SERVICE_DETAIL") NOT LIKE '%budget%'
          AND
            LOWER("ORGANISATION_PURPOSE") NOT LIKE '%budget%'
          AND
            LOWER("SERVICE_DETAIL") NOT LIKE '%work and income%'
          AND
            LOWER("ORGANISATION_PURPOSE") NOT LIKE '%work and income%'
        ) AND (
            LOWER("SERVICE_DETAIL") LIKE '%mental%'
          OR
            LOWER("ORGANISATION_PURPOSE") LIKE '%mental%'
          OR
            LOWER("SERVICE_DETAIL") LIKE '%depression%'
          OR
            LOWER("ORGANISATION_PURPOSE") LIKE '%depression%'
          OR
            LOWER("SERVICE_DETAIL") LIKE '%distress%'
          OR
            LOWER("ORGANISATION_PURPOSE") LIKE '%distress%'
        ) AND (
            "LEVEL_2_CATEGORY" LIKE '%Counselling%'
          OR
            "LEVEL_2_CATEGORY" LIKE '%Depression%'
          OR
            "LEVEL_2_CATEGORY" LIKE '%Anxiety Problems%'
        )
        {orderby}
    """,

    "lbs_budgeting": """
        SELECT DISTINCT {fields}
        FROM {dataset}
        WHERE {skip_null_results} AND
        (
            "LEVEL_2_CATEGORY" LIKE '%Other budgeting services%'
          OR
            "LEVEL_2_CATEGORY" LIKE '%Financial Assistance%'
          OR
            "LEVEL_2_CATEGORY" LIKE '%Financial mentors%'
          OR
            "LEVEL_2_CATEGORY" LIKE '%MoneyMates%'
        ) AND (
            LOWER("SERVICE_DETAIL") NOT LIKE '%student%'
          AND
            LOWER("ORGANISATION_PURPOSE") NOT LIKE '%student%'
          AND
            LOWER("SERVICE_DETAIL") NOT LIKE '%education%'
          AND
            LOWER("ORGANISATION_PURPOSE") NOT LIKE '%education%'
          AND
            LOWER("SERVICE_DETAIL") NOT LIKE '%job%'
          AND
            LOWER("ORGANISATION_PURPOSE") NOT LIKE '%job%'
          AND
            LOWER("SERVICE_DETAIL") NOT LIKE '%older people%'
          AND
            LOWER("ORGANISATION_PURPOSE") NOT LIKE '%older people%'
          AND
            LOWER("SERVICE_DETAIL") NOT LIKE '%awards%'
          AND
            LOWER("ORGANISATION_PURPOSE") NOT LIKE '%awards%'
          AND
            LOWER("SERVICE_DETAIL") NOT LIKE '%superannuation%'
          AND
            LOWER("ORGANISATION_PURPOSE") NOT LIKE '%superannuation%'
          AND
            LOWER("SERVICE_DETAIL") NOT LIKE '%supergold%'
          AND
            LOWER("ORGANISATION_PURPOSE") NOT LIKE '%supergold%'
          AND
            LOWER("SERVICE_DETAIL") NOT LIKE '%retirement%'
          AND
            LOWER("ORGANISATION_PURPOSE") NOT LIKE '%retirement%'
          AND
            LOWER("SERVICE_DETAIL") NOT LIKE '%pension%'
          AND
            LOWER("ORGANISATION_PURPOSE") NOT LIKE '%pension%'
          AND
            LOWER("PROVIDER_NAME") NOT LIKE 'work and income%'
        )
        {orderby}
    """,

    "lbs_well_child": """
        SELECT DISTINCT {fields}
        FROM {dataset}
        WHERE {skip_null_results} AND
        (
            "LEVEL_2_CATEGORY" LIKE '%Well Child Health (Tamariki Ora)%'
        )
        {orderby}
    """,

}
