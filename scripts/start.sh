#!/bin/sh
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py create_super_admin
python manage.py shell -c 'from chatbot.tasks.indexer_task import reindexar_datos_sistema; reindexar_datos_sistema()'
daphne -b 0.0.0.0 -p 8000 core.asgi:application