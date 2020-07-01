# Generated by Django 2.2.4 on 2020-07-01 10:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0095_auto_20200626_1149'),
    ]

    operations = [
        migrations.RunSQL("""
        create or replace view api_collapsed_associations as
              select
                -- this is kind of a hack, but we at least know aa.ids are unique and django requires an id for each model instance
                min(aa.id) as id,
                aa.variant_in_source_id,

                ap.term as disease,
                case when count(distinct aa.id) = 1 then min(aa.source_link) else null end as evidence_url,
                aa.evidence_type,
                aa.evidence_direction,
                aa.clinical_significance,
                aa.drug_labels,
                string_agg(distinct ae.description, '; ') as contexts,
                string_agg(distinct aa.evidence_level, ', ') as evidence_levels,
                array_agg(distinct pubs_tbl) as publications,
                jsonb_agg(distinct jsonb_build_object(
                  'id', aa.id, 'url', aa.source_link, 'evidence_level', aa.evidence_level,
                  'publications', (
                    select array_agg(pubs) from api_evidence, unnest(api_evidence.publications) as pubs
                    where api_evidence.association_id=aa.id)
                )) as children,
                count(distinct aa.id) as collapsed_count

              from api_association aa
              inner join api_phenotype ap on aa.id = ap.association_id
              left join api_environmentalcontext ae on aa.id = ae.association_id
              inner join api_evidence aev on aa.id = aev.association_id, unnest(aev.publications) pubs_tbl
              group by
                aa.variant_in_source_id,
                ap.term,
                aa.evidence_type,
                aa.evidence_direction,
                aa.clinical_significance,
                aa.drug_labels
        """, reverse_sql="""
        create or replace view api_collapsed_associations as
              select
                -- this is kind of a hack, but we at least know aa.ids are unique and django requires an id for each model instance
                min(aa.id) as id,
                aa.variant_in_source_id,

                ap.term as disease,
                case when count(distinct aa.id) = 1 then min(aa.source_link) else null end as evidence_url,
                aa.evidence_type,
                aa.evidence_direction,
                aa.clinical_significance,
                aa.drug_labels,
                string_agg(distinct ae.description, '; ') as contexts,
                string_agg(distinct aa.evidence_level, ', ') as evidence_levels,
                array_agg(distinct pubs_tbl) as publications,
                jsonb_agg(distinct jsonb_build_object(
                  'id', aa.id, 'url', aa.source_link, 'evidence_level', aa.evidence_level,
                  'publications', (
                    select array_agg(pubs) from api_evidence, unnest(api_evidence.publications) as pubs
                    where api_evidence.association_id=aa.id)
                )) as children,
                count(distinct aa.id) as collapsed_count

              from api_association aa
              inner join api_phenotype ap on aa.id = ap.association_id
              inner join api_environmentalcontext ae on aa.id = ae.association_id
              inner join api_evidence aev on aa.id = aev.association_id, unnest(aev.publications) pubs_tbl
              group by
                aa.variant_in_source_id,
                ap.term,
                aa.evidence_type,
                aa.evidence_direction,
                aa.clinical_significance,
                aa.drug_labels
        """)
    ]