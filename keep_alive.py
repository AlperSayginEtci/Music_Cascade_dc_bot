from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Music Cascade Bot is alive and running!"

def run():
    # Render, Koyeb vb. platformlarda genellikle port 8080 veya 10000 kullanılır
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
