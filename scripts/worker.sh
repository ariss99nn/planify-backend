#!/bin/sh
celery -A core worker -l warning --concurrency=2