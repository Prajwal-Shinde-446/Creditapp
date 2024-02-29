# Use an official Python runtime as a parent image
FROM python:3.11

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir Django
RUN pip install psycopg2-binary
# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable for Django
ENV DJANGO_SETTINGS_MODULE=credit_approval_system.settings

# Run app.py when the container launches
CMD ["gunicorn", "credit_approval_system.wsgi:application", "--bind", "0.0.0.0:8000"]
