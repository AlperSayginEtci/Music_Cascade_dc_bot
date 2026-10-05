FROM python:3.10-slim

# FFmpeg ve Node.js kurulumu (yt-dlp JS runtime gerektirir)
RUN apt-get update && apt-get install -y ffmpeg nodejs npm && apt-get clean && rm -rf /var/lib/apt/lists/*



# Çalışma dizinini ayarla
WORKDIR /app

# Gereksinimleri kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Bot dosyalarını kopyala
COPY . .

# Web sunucusu için portu dışarı aç
EXPOSE 8080

# Botu çalıştır
CMD ["python", "main.py"]
