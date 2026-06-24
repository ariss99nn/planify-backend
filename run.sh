#!/bin/bash
cd /home/ronin99/Documentos/Planify_Sena/back
source .venv/bin/activate
DJANGO_SETTINGS_MODULE=core.settings daphne -b 0.0.0.0 -p 8000 core.asgi:application