# 🎶 Music Cascade — Discord Music Bot

A self-hostable Discord music bot that streams audio from YouTube into voice channels using **slash commands**, with a per-server song queue. Built with `discord.py` and `yt-dlp` and containerized with Docker for cloud hosts such as Render.

## Features

- **Slash commands:** `/play`, `/pause`, `/resume`, `/skip`, `/stop`, `/queue`, `/help`
- **Search or link:** play by song name (YouTube search) or a direct URL
- **Per-guild queues:** each server has its own independent queue and "now playing" state
- **Streaming playback:** audio is streamed through FFmpeg, nothing is downloaded to disk
- **Cloud-ready:** Dockerfile and a small Flask keep-alive endpoint for platforms such as Render or Koyeb
- **Resilient connection:** voice connection timeout handling and FFmpeg auto-reconnect for unstable streams

## Tech Stack

| Area | Tools |
|---|---|
| Language | Python 3.10 |
| Discord API | discord.py 2.x (app commands, cogs) |
| Media | yt-dlp, FFmpeg, PyNaCl |
| Deployment | Docker, Flask (health endpoint), Render |

## Architecture

```
main.py            → bot setup, intents, slash-command sync, keep-alive server
cogs/music.py      → Music cog: YTDLSource (yt-dlp → FFmpeg audio), queue logic, commands
keep_alive.py      → minimal Flask server on :8080 for cloud health checks
Dockerfile         → python:3.10-slim + ffmpeg + nodejs (needed by yt-dlp)
```

Playback is asynchronous: `yt-dlp` metadata extraction runs in a thread executor so the bot's event loop never blocks. When a track finishes, the `after` callback pops the next item from that server's queue.

## Getting Started

### Prerequisites
- Python 3.10+
- [FFmpeg](https://ffmpeg.org/) available on your `PATH`
- A Discord bot token from the [Discord Developer Portal](https://discord.com/developers/applications) with the **Message Content Intent** enabled

### Run locally
```bash
git clone https://github.com/AlperSayginEtci/Music_Cascade_dc_bot.git
cd Music_Cascade_dc_bot
pip install -r requirements.txt
cp .env.example .env        # then put your token in DISCORD_TOKEN
python main.py
```

### Run with Docker
```bash
docker build -t music-cascade .
docker run -e DISCORD_TOKEN=your_token music-cascade
```

Once you see `Komutlar senkronize edildi` ("commands synced") in the console, type `/play <song name>` in any server the bot has joined.

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `DISCORD_TOKEN` | ✅ | Bot token |
| `YOUTUBE_COOKIES_B64` / `YOUTUBE_COOKIES` | optional | YouTube cookies (Netscape format) for hosts whose IPs are rate-limited by YouTube |

## What I Learned

Getting audio streaming to work on a datacenter IP was the main challenge. YouTube blocks or throttles many cloud IPs, so I iterated through several approaches: different `yt-dlp` player clients, cookie injection via environment variables (base64-encoded to survive the host's newline stripping), and the PO-token plugin. The commit history documents this debugging process.

## License

This project is for educational purposes. Make sure your use complies with YouTube's and Discord's Terms of Service.
