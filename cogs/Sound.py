import discord
import asyncio
from discord.ext import commands
from discord import FFmpegPCMAudio


class Sound(commands.Cog):
  def __init__(self, client):
    self.client = client
    self.queues = {}
    self.currents = {}
  
  def check_queue(self,voice,id):
    if self.queues[id] and voice:
      song = self.queues[id].pop(0)
      self.currents[id] = song
      voice.play(FFmpegPCMAudio(song), after = lambda _: self.check_queue(voice,id)) 
      #_ is the error parameter needed for after finalizer
    elif not self.queues[id] and (not voice or not voice.is_playing()):
      async def waitingForDC():
        await asyncio.sleep(3)
        if not self.queues[id] and (not voice or not voice.is_playing()):
          self.currents[id] = None
          await voice.disconnect()
      coro = waitingForDC()
      fut = asyncio.run_coroutine_threadsafe(coro, self.client.loop)
      try:
          fut.result()
      except:
          # an error happened sending the message
          pass

  async def play(self,message,song):
    if message.author.voice:
      if message.guild.voice_client:
        voice = message.guild.voice_client
      else:
        channel = message.author.voice.channel
        voice = await channel.connect()
      guild_id = message.guild.id
      if guild_id in self.queues and (voice.is_playing() or voice.is_paused()):
        self.queues[guild_id].append(song)
        #await ctx.send("added song to queue")
      elif voice.is_connected():
        self.queues[guild_id] = []
        self.currents[guild_id] = song
        voice.play(FFmpegPCMAudio(song), after = lambda _: self.check_queue(voice,guild_id))
    else:
      await message.channel.send('You have to be connected to the channel to use that command')

  @commands.command(pass_context = True, help = 'Shows queued sounds and current sound')
  async def queue(self,ctx):
    guild_id = ctx.message.guild.id
    if guild_id in self.currents and self.currents[guild_id]:
      currentSong = self.currents[guild_id]
      embed=discord.Embed(color=0xADD8E6)
      embed.add_field(name = 'Current Song', value=currentSong[7:].split('.')[0], inline=False)
      if guild_id in self.queues and self.queues[guild_id]:
        message = []
        for song in self.queues[guild_id]:
          message.append(song[7:].split('.')[0] + '\n')
        embed.add_field(name = 'Current Queue', value=''.join(message), inline=False)
      await ctx.send(embed=embed)  
    else:
      await ctx.send('There is currently nothing playing.')

  @commands.command(help = 'Skips current song')
  async def skip(self,ctx):
    if ctx.message.author.voice:
      voice = ctx.guild.voice_client
      if not voice:
        await ctx.message.channel.send('Nothing to skip')
      elif voice.is_playing():
        voice.stop()
    else:
      await ctx.message.channel.send('You have to be connected to the channel to use that command')

  @commands.Cog.listener()
  async def on_voice_state_update(self,member, before, after):
    #sound greeting when someone connects to the voice channel
    if before.channel is None and after.channel is not None and not member.bot:
      channel = after.channel
      if not channel.guild.voice_client:
        voice = await channel.connect()
        self.queues[member.guild.id] = []
        voice.play(FFmpegPCMAudio('sounds/greetings.mp3'),after = lambda _: self.check_queue(voice,member.guild.id))

def setup(client):
  client.add_cog(Sound(client))