FROM python:3.10-slim

WORKDIR /RESUME_CV_AGENT

COPY requirements.txt /RESUME_CV_AGENT/
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# RUN pip install 
# RUN pip install langchain
# Copy your code
COPY . .

# Expose port (Cloud Run uses 8080)
ENV PORT=8080

# Start server
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]