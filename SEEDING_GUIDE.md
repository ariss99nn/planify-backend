# DB Seed Guide

Estos scripts insertan datos de ejemplo en los principales modelos del backend.

## Archivos generados
- `users/seed_data.sql`
- `programa/seed_data.sql`
- `competencia/seed_data.sql`
- `aulas/seed_data.sql`
- `docentes/seed_data.sql`
- `ficha/seed_data.sql`
- `bhorario/seed_data.sql`
- `planificacion/seed_data.sql`
- `alertas/seed_data.sql`
- `notificaciones/seed_data.sql`
- `exportacion/seed_data.sql`
- `reportes/seed_data.sql`
- `analitica/seed_data.sql`
- `seed_all.sh`

## Orden de ejecución recomendado
1. Ejecuta las migraciones:
   ```bash
   .venv/bin/python3 manage.py migrate
   ```
2. Corre el script global desde la carpeta `back`:
   ```bash
   cd /home/ronin99/Documentos/Planify_Sena/back
   chmod +x seed_all.sh
   ./seed_all.sh
   ```

## Ejecución manual por archivo
Si quieres ejecutar solo un script específico:
```bash
cd /home/ronin99/Documentos/Planify_Sena/back
python3 manage.py dbshell < users/seed_data.sql
```

## Notas importantes
- `users/seed_data.sql` debe ejecutarse primero.
- El resto de los scripts está ordenado para satisfacer FK jerárquicos.
- Si tu base de datos cambia de esquema, revisa el script antes de ejecutarlo.
