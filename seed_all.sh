#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

SCRIPTS=(
  users/seed_data.sql
  programa/seed_data.sql
  competencia/seed_data.sql
  aulas/seed_data.sql
  docentes/seed_data.sql
  ficha/seed_data.sql
  bhorario/seed_data.sql
  planificacion/seed_data.sql
  alertas/seed_data.sql
  notificaciones/seed_data.sql
  exportacion/seed_data.sql
  reportes/seed_data.sql
  analitica/seed_data.sql
)

for script in "${SCRIPTS[@]}"; do
  echo "Applying $script"
  python3 manage.py dbshell < "$script"
  echo "Finished $script"
  echo
 done
