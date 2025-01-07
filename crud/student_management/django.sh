#!/bin/sh
echo "Waiting for the database to be ready..."
until python3 -c "import psycopg2; psycopg2.connect(dbname='student_management', user='postgres', password='postgres', host='db')" 2>/dev/null; do
  sleep 1
done

echo "Database is ready. Applying migrations and starting the server..."
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
