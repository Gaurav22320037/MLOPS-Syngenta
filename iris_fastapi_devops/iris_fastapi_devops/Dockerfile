# Stage 1: Build the FastAPI app
FROM python:3.9-slim as build

WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt && pip list

# Copy the FastAPI app code
COPY . .

# Stage 2: Production image
FROM python:3.9-slim

WORKDIR /app

# Copy the requirements file to the production image
COPY requirements.txt .

# Install dependencies again
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app from the build stage
COPY --from=build /app /app

EXPOSE 8000

# Use the full path for uvicorn
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
