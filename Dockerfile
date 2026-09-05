FROM python:3.10-slim

# FFmpeg kurulumu
RUN apt-get update && apt-get install -y ffmpeg

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
