FROM python:3.13-slim

WORKDIR /app

# Install Dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# COPY . /app/

EXPOSE 8001

# This should be changed with gunicorn
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
