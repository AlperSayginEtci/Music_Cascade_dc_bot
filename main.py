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

# YouTube Çerezlerini dosyaya yaz
youtube_cookies_b64 = os.getenv('YOUTUBE_COOKIES_B64')
youtube_cookies = os.getenv('YOUTUBE_COOKIES')

if youtube_cookies_b64:
    try:
        decoded = base64.b64decode(youtube_cookies_b64).decode('utf-8')
        with open('cookies.txt', 'w', encoding='utf-8') as f:
            f.write(decoded)
        print("YouTube çerezleri (Base64'ten) başarıyla oluşturuldu.")
    except Exception as e:
        print(f"Base64 çerez çözme hatası: {e}")
elif youtube_cookies:
    with open('cookies.txt', 'w', encoding='utf-8') as f:
        f.write(youtube_cookies)
    print("YouTube çerezleri (Düz Metin) oluşturuldu.")



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
