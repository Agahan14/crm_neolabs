#!/usr/bin/env bash
python manage.py migrate --noinput
sudo systemctl restart gunicorn
