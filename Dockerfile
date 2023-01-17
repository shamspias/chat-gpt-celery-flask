FROM python:3.8
COPY . /app
WORKDIR /app

# Install the dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 5000
# Start Redis
RUN apt-get update && apt-get install -y redis-server

# Start celery worker
CMD ["bash", "./start.sh"]