# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variables for API keys
# The client will need to replace these placeholder values with their own keys
ENV OPENAI_API_KEY="OPENAIAPI"
ENV SEC_API_KEY="SECAPI"
ENV POLYGON_API_KEY="POLYGONAPI"

# Expose the Streamlit port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.enableCORS=false", "--server.headless=true"]
