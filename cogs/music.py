import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import asyncio

ytdl_format_options = {
    'format': '140/251/250/249/139/bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'cookiefile': 'cookies.txt'
}


ffmpeg_options = {
    'options': '-vn',
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
}

# Debug için ayrı bir ytdl instance (format listesi görmek için)
ytdl_debug = yt_dlp.YoutubeDL({**ytdl_format_options, 'quiet': False, 'no_warnings': False})
ytdl = yt_dlp.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()

        # Debug: Mevcut formatları logla
        def extract_with_debug():
            try:
                info = ytdl_debug.extract_info(url, download=False, process=False)
                if info and 'formats' in info:
                    fmts = info['formats']
                    print(f"[DEBUG] {len(fmts)} format mevcut. Ses formatları:")
                    for f in fmts:
                        if f.get('acodec') != 'none' or f.get('vcodec') == 'none':
                            print(f"  ID={f.get('format_id')} ext={f.get('ext')} proto={f.get('protocol')} abr={f.get('abr')}")
                elif info is None:
                    print("[DEBUG] info=None geldi, video bulunamadı veya cookie hatası")
                else:
                    print("[DEBUG] 'formats' anahtarı yok")
            except Exception as e:
                print(f"[DEBUG] Format listesi alınamadı: {e}")
            return ytdl.extract_info(url, download=not stream)

        data = await loop.run_in_executor(None, extract_with_debug)

        if data is None:
            raise Exception('Could not retrieve video data from YouTube.')

        if 'entries' in data:
            data = data['entries'][0]

        if stream:
            # m3u8 manifest URL veya direkt URL'yi al
            filename = data.get('url') or data.get('manifest_url')
            if not filename:
                raise Exception('No streamable URL found for this video.')
        else:
            filename = ytdl.prepare_filename(data)

        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}
        self.current_song = {}

    def get_queue(self, guild_id):
        if guild_id not in self.queues:
            self.queues[guild_id] = []
        return self.queues[guild_id]

    def play_next(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        if self.queues.get(guild_id):
            source = self.queues[guild_id].pop(0)
            self.current_song[guild_id] = source.title
            interaction.guild.voice_client.play(source, after=lambda e: self.play_next(interaction))
        else:
            self.current_song[guild_id] = None

    @app_commands.command(name="play", description="Plays a song from YouTube (Search or Link)")
    async def play(self, interaction: discord.Interaction, search: str):
        await interaction.response.defer()

        if not interaction.user.voice:
            await interaction.followup.send("You need to join a voice channel first!")
            return

        channel = interaction.user.voice.channel
        voice_client = interaction.guild.voice_client

        if not voice_client:
            try:
                voice_client = await asyncio.wait_for(
                    channel.connect(self_deaf=True),
                    timeout=30.0
                )
            except asyncio.TimeoutError:
                await interaction.followup.send("❌ Ses kanalına bağlanılamadı (zaman aşımı). Lütfen tekrar deneyin.")
                return
            except Exception as e:
                await interaction.followup.send(f"❌ Ses kanalına bağlanılamadı: {e}")
                return
        elif voice_client.channel != channel:
            await voice_client.move_to(channel)


        try:
            source = await YTDLSource.from_url(search, loop=self.bot.loop, stream=True)
            queue = self.get_queue(interaction.guild_id)
            
            if not voice_client.is_playing() and not voice_client.is_paused():
                self.current_song[interaction.guild_id] = source.title
                voice_client.play(source, after=lambda e: self.play_next(interaction))
                await interaction.followup.send(f'🎶 Now playing: **{source.title}**')
            else:
                queue.append(source)
                await interaction.followup.send(f'📝 Added to queue: **{source.title}**')
        except Exception as e:
            await interaction.followup.send(f"An error occurred while trying to play the video:\n```{e}```")
            print(f"Playback error: {e}")

    @app_commands.command(name="pause", description="Pauses the currently playing song")
    async def pause(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await interaction.response.send_message("⏸️ Song paused.")
        else:
            await interaction.response.send_message("There is no song currently playing.")

    @app_commands.command(name="resume", description="Resumes the paused song")
    async def resume(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            await interaction.response.send_message("▶️ Song resumed.")
        else:
            await interaction.response.send_message("There is no paused song.")

    @app_commands.command(name="skip", description="Skips the current song")
    async def skip(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client and (voice_client.is_playing() or voice_client.is_paused()):
            voice_client.stop()
            await interaction.response.send_message("⏭️ Song skipped.")
        else:
            await interaction.response.send_message("There is no song currently playing.")

    @app_commands.command(name="stop", description="Stops the music and disconnects the bot")
    async def stop(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client:
            self.queues[interaction.guild_id] = []
            self.current_song[interaction.guild_id] = None
            await voice_client.disconnect()
            await interaction.response.send_message("⏹️ Music stopped and disconnected.")
        else:
            await interaction.response.send_message("The bot is not in a voice channel.")

    @app_commands.command(name="queue", description="Shows the current song queue")
    async def queue(self, interaction: discord.Interaction):
        queue = self.get_queue(interaction.guild_id)
        current = self.current_song.get(interaction.guild_id)

        if not current and not queue:
            await interaction.response.send_message("The queue is currently empty.")
            return

        msg = f"**Now Playing:** {current}\n\n**Queue:**\n"
        if queue:
            for i, song in enumerate(queue):
                msg += f"{i+1}. {song.title}\n"
        else:
            msg += "No songs waiting in the queue."

        await interaction.response.send_message(msg)

    @app_commands.command(name="help", description="Shows how to use the bot and its commands")
    async def help_cmd(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎶 Music Cascade - Help Menu",
            description="Below are all the supported commands. Just type the command and press enter.",
            color=discord.Color.blue()
        )
        embed.add_field(name="▶️ /play <song name or link>", value="Searches YouTube or plays the direct link. The bot will join automatically.", inline=False)
        embed.add_field(name="⏸️ /pause", value="Pauses the currently playing song.", inline=False)
        embed.add_field(name="▶️ /resume", value="Resumes the paused song.", inline=False)
        embed.add_field(name="⏭️ /skip", value="Skips the current song and plays the next one in the queue.", inline=False)
        embed.add_field(name="⏹️ /stop", value="Stops the music completely, clears the queue, and leaves the channel.", inline=False)
        embed.add_field(name="📋 /queue", value="Shows the currently playing song and the queue list.", inline=False)
        embed.add_field(name="❓ /help", value="Shows this help menu.", inline=False)
        
        embed.set_footer(text="Music Cascade Bot - Your server's DJ!")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Music(bot))
