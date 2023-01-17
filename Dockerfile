FROM python:3.8
COPY . /app
WORKDIR /app

# Install the dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 5000
# Start the celery worker and beat
CMD celery -A app.celery worker --loglevel=info --concurrency=4 --beat
# Start the Flask app
CMD ["python", "app.py"]
