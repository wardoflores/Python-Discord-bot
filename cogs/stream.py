import random 
import os 
from os import system
import shutil
import asyncio
import youtube_dl
import discord
from discord.ext import commands
from discord.utils import get 

client = commands.Bot(command_prefix = '.') 

ydl_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}   

ffmpeg_options = {
'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ydl_opts)

youtube_dl.utils.bug_reports_message = lambda: ''

class stream(commands.Cog):
    def __init__(self, client):
        self.client = client

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

    @commands.Cog.listener() 
    async def on_ready(self): 
        print('Bot cog is ready.')

    @commands.command()
    async def stream(self, ctx, *, url):
        """Streams from a url (same as yt, but doesn't predownload)"""
        player = await stream.from_url(url, loop=client.loop, stream=True)
        ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
        await ctx.send('Now playing: {}'.format(player.title))

def setup(client):
    client.add_cog(stream(client))