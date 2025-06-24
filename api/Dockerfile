FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and data into container
COPY ./app ./app
COPY ./data ./data

# Expose FastAPI port
EXPOSE 8000

# Launch the FastAPI app using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
