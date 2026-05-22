FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD sh -c "sleep 10 && \
           python manage.py migrate && \
           python manage.py createsuperuser --noinput || true && \
           python manage.py seed_data && \
           python manage.py collectstatic --noinput && \
           gunicorn wsgi:application --bind 0.0.0.0:8000"