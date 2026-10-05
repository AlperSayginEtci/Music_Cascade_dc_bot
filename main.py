import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio

from keep_alive import keep_alive

# Ortam değişkenlerini yükle
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

import base64
import subprocess

# yt-dlp'yi başlangıçta güncelle
try:
    subprocess.run(['pip', 'install', '-U', 'yt-dlp', 'yt-dlp-get-pot', '-q'], check=True)
    print("yt-dlp ve yt-dlp-get-pot güncellendi.")
except Exception as e:
    print(f"yt-dlp güncelleme hatası: {e}")

# YouTube Çerezlerini dosyaya yaz
youtube_cookies_b64 = os.getenv('YOUTUBE_COOKIES_B64')
youtube_cookies = os.getenv('YOUTUBE_COOKIES')

if youtube_cookies_b64:
    try:
        decoded = base64.b64decode(youtube_cookies_b64, validate=False).decode('utf-8')
        # CRLF -> LF dönüşümü (yt-dlp Netscape formatı için gerekli)
        decoded = decoded.replace('\r\n', '\n').replace('\r', '\n')
        with open('cookies.txt', 'w', encoding='utf-8', newline='\n') as f:
            f.write(decoded)
        lines = [l for l in decoded.splitlines() if l.strip() and not l.startswith('#')]
        print(f"YouTube çerezleri başarıyla yazıldı. ({len(lines)} çerez satırı)")
    except Exception as e:
        print(f"Base64 çerez çözme hatası: {e}")
elif youtube_cookies:
    text = youtube_cookies.replace('\r\n', '\n').replace('\r', '\n')
    with open('cookies.txt', 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    print("YouTube çerezleri (Düz Metin) oluşturuldu.")
else:
    print("UYARI: YOUTUBE_COOKIES_B64 veya YOUTUBE_COOKIES ortam değişkeni bulunamadı!")




class MusicBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        # Müzik cog'unu yükle
        await self.load_extension('cogs.music')
        # Slash komutlarını senkronize et
        await self.tree.sync()
        print("Komutlar senkronize edildi.")

    async def on_ready(self):
        print(f'{self.user} olarak giriş yapıldı!')
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="/help"))

bot = MusicBot()

if __name__ == '__main__':
    if not TOKEN or TOKEN == "buraya_botunuzun_tokenini_yazin":
        print("HATA: Lütfen .env dosyasına DISCORD_TOKEN girin!")
    else:
        # Web sunucusunu başlat (Botun uyumamasını sağlar)
        keep_alive()
        bot.run(TOKEN)
