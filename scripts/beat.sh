#!/bin/sh
celery -A core beat -l warning --scheduler django_celery_beat.schedulers:DatabaseScheduler