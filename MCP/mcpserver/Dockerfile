FROM python:3.11-slim

WORKDIR /demo

# Copy requirements file
COPY requirements.txt .

# Install dependencies using uv
RUN pip install uv
RUN uv venv
RUN uv pip install -r requirements.txt

# Copy application code
COPY server.py .
COPY client-sse.py .

# Expose the port the server runs on
EXPOSE 8000

# Command to run the server
CMD ["uv", "run", "server.py"] 