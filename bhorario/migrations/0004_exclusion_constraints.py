from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bhorario', '0003_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE EXTENSION IF NOT EXISTS btree_gist;

                ALTER TABLE bhorario_bloquehorario
                ADD CONSTRAINT no_conflicto_docente
                EXCLUDE USING gist (
                    docente_id WITH =,
                    dia_semana WITH =,
                    tsrange(
                        timestamp '2000-01-01 00:00' + hora_inicio,
                        timestamp '2000-01-01 00:00' + hora_fin
                    ) WITH &&
                ) WHERE (docente_id IS NOT NULL);

                ALTER TABLE bhorario_bloquehorario
                ADD CONSTRAINT no_conflicto_aula
                EXCLUDE USING gist (
                    aula_id WITH =,
                    dia_semana WITH =,
                    tsrange(
                        timestamp '2000-01-01 00:00' + hora_inicio,
                        timestamp '2000-01-01 00:00' + hora_fin
                    ) WITH &&
                ) WHERE (aula_id IS NOT NULL);

                ALTER TABLE bhorario_bloquehorario
                ADD CONSTRAINT no_conflicto_ficha
                EXCLUDE USING gist (
                    ficha_id WITH =,
                    dia_semana WITH =,
                    tsrange(
                        timestamp '2000-01-01 00:00' + hora_inicio,
                        timestamp '2000-01-01 00:00' + hora_fin
                    ) WITH &&
                ) WHERE (ficha_id IS NOT NULL);
            """,
            reverse_sql="""
                ALTER TABLE bhorario_bloquehorario
                DROP CONSTRAINT IF EXISTS no_conflicto_docente;
                ALTER TABLE bhorario_bloquehorario
                DROP CONSTRAINT IF EXISTS no_conflicto_aula;
                ALTER TABLE bhorario_bloquehorario
                DROP CONSTRAINT IF EXISTS no_conflicto_ficha;
            """,
        ),
    ]