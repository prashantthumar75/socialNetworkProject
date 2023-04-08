FROM python:3.8.10-slim-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /code

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /code/
RUN pip install -r requirements.txt

# Copy the project code
COPY . /code/

# Run the server
CMD python manage.py runserver 0.0.0.0:8000
