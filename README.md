# Music Cascade Bot

Bu, Discord için YouTube üzerinden ses çalan açık kaynaklı bir müzik botudur. API sorunlarını aşmak için `yt-dlp` kullanır.

## Özellikler
* `yt-dlp` ile YouTube üzerinden doğrudan müzik arama ve oynatma.
* Gelişmiş slash komutları (`/play`, `/skip`, `/stop`, `/pause`, `/resume`, `/queue`).
* Kuyruk sistemi.

## Kurulum ve Çalıştırma (Kendi Bilgisayarınızda veya Sunucuda)

7/24 çalışmasını istiyorsanız bu botu açık tutacağınız bir sunucuya (VDS/VPS) kurabilirsiniz. Botu sadece arkadaşlarınızla oynarken kullanmak istiyorsanız kendi bilgisayarınızda çalıştırabilirsiniz.

### 1. Gereksinimleri Yükleyin
Bu projenin çalışması için bilgisayarınızda (veya sunucuda) şunların kurulu olması gerekir:
* **Python 3.10+**
* **FFmpeg:** Ses işleme için gereklidir.
  * *Windows:* FFmpeg indirip sistem ortam değişkenlerine eklemelisiniz. Veya `choco install ffmpeg` komutunu kullanabilirsiniz.
  * *Linux/Ubuntu:* `sudo apt update && sudo apt install ffmpeg` komutu ile kurabilirsiniz.

### 2. Projeyi Hazırlayın
Projeyi indirdikten sonra klasörde bir terminal (komut istemi) açın ve kütüphaneleri yükleyin:
```bash
pip install -r requirements.txt
```

### 3. Bot Token Ayarları
Discord Developer Portal üzerinden bir bot oluşturun ve "Bot" sekmesinden **TOKEN** alın. 
Ayrıca Bot ayarlarından "Message Content Intent" seçeneğini açmayı unutmayın!

Klasördeki `.env.example` dosyasının adını sadece `.env` olacak şekilde değiştirin, içine girip Token'ınızı yapıştırın:
```
DISCORD_TOKEN=sizin_gizli_tokeniniz_buraya
```

### 4. Çalıştırın
Her şey hazır olduğunda botu başlatın:
```bash
python main.py
```
Konsolda "Komutlar senkronize edildi" mesajını gördükten sonra Discord'dan `/play şarkı ismi` yazarak müzik dinlemeye başlayabilirsiniz!
