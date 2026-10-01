FROM python:3.12-slim

# Set working directory di dalam container
WORKDIR /app

# Install system dependencies (opsional, berjaga-jaga jika ada library C/C++ dari Pandas/Numpy yang butuh build)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt lebih dulu untuk memanfaatkan Docker cache
COPY requirements.txt .

# Install dependensi Python (menggunakan --no-cache-dir agar image lebih ringan)
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh kode aplikasi ke dalam container
COPY . .

# Expose port 8000 untuk FastAPI
EXPOSE 8000

# Perintah untuk menjalankan Uvicorn server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
