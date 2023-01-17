#!/bin/bash
redis-server &
celery -A app.celery worker --loglevel=info &
flask run --host 0.0.0.0
