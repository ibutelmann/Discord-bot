import discord
import os
import random
from discord.ext import commands

folders = {'friend1','friend2','friend3'}
phrases = {'hello':'hello'}
fotos = [] #so that every picture has the same probability
dirname = os.path.dirname(__file__)
picturePath = os.path.join(dirname, '../fotos')
soundPath = os.path.join(dirname, '../sounds')
for folder in os.listdir(picturePath):
  for foto in os.listdir(picturePath + "/"  + folder):
    fotos.append(f'{picturePath}/{folder}/{foto}')
soundsFiles = {i.split(".")[0]:i.split(".")[1] for i in os.listdir(soundPath)}

class Misc(commands.Cog):
  def __init__(self,client):
    self.client = client

  @commands.Cog.listener()
  async def on_message(self,message):
    if message.author.bot:
      return
    for frase in phrases:
      if frase in message.content.lower():
        await message.channel.send(phrases[frase])
        return
    if message.content.lower() == 'picPls':
      randomPic = random.choice(fotos)
      await message.channel.send(file=discord.File(randomPic))
    elif message.content.lower() in soundsFiles:
      bot = self.client.get_cog('Sound')
      await bot.play(message,'sounds/' + message.content.lower() + "." + soundsFiles[message.content.lower()])
    elif message.content.lower() == 'soundPls':
      bot = self.client.get_cog('Sound')
      sound = random.choice(os.listdir('sounds/'))
      await bot.play(message,'sounds/' + sound)
    elif message.content.lower() in folders:
      directory = f'fotos/{message.content.lower()}/'
      await message.channel.send(file=discord.File(directory + random.choice(os.listdir(directory))))

  @commands.command(pass_context = True, help='Sends names of sounds')
  async def sounds(self,ctx):
    embed=discord.Embed(color=0x00ff00)
    valueSounds = []
    for sound in soundsFiles:
      valueSounds.append(sound + '\n')
    embed.add_field(name = 'Sounds', value=''.join(valueSounds), inline=False)
    await ctx.send(embed=embed)

  @commands.command(pass_context = True, help ='Sends audit of last actions')
  async def audit(self,ctx,limit = 5):
    guild = ctx.guild
    message = []
    async for entry in guild.audit_logs(limit=limit):
      if entry.action == discord.AuditLogAction.member_update:
        for attrAfter,valueAfter in entry.after:
          if attrAfter == 'mute':
            if valueAfter:
              message.append(f'{entry.user} muted {entry.target}' + '\n')
            else:
              message.append(f'{entry.user} unmuted {entry.target}' + '\n')
          elif attrAfter == 'deaf':
            if valueAfter:
              message.append(f'{entry.user} deafened {entry.target}' + '\n')
            else:
              message.append(f'{entry.user} undeafened {entry.target}' + '\n')
          else:
            message.append(f'{entry.user} changed nick of {entry.target} for {valueAfter}' + '\n')
      elif entry.action == discord.AuditLogAction.member_disconnect:
        message.append(f'{entry.user} kicked someone' + '\n')
        #there is no entry.target when someone gets kicked, discord doesnt give that info
      else:
        message.append(f'{entry.user} did {entry.action} to {entry.target}' + '\n')
    embed=discord.Embed(color=0xFF0000)
    embed.add_field(name = f'Last {limit} Audits', value=''.join(message), inline=False)
    await ctx.send(embed=embed)

  @commands.Cog.listener()
  async def on_command_error(self,ctx, error):
      if isinstance(error, commands.errors.CommandNotFound):
          await ctx.send('I dont have that command')
      raise error

def setup(client):
  client.add_cog(Misc(client))