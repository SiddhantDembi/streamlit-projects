# Use Python official image for the backend
FROM python:3.9-slim

# Set the working directory for the backend
WORKDIR /app

# Copy the backend requirements file
COPY requirements.txt ./

# Install backend dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend source code
COPY . .

# Expose the port on which the backend will run
EXPOSE 8501

# Start the Streamlit application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
