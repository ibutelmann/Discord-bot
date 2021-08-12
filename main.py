import discord
import os
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix = '~', intents = intents)

@client.event
async def on_ready():
    await client.change_presence(activity = discord.Game('A Game'))
    print('We have logged in as {0.user}'.format(client))

if __name__ == '__main__':
  client.load_extension('cogs.Misc')
  client.load_extension('cogs.Sound')

client.run(os.getenv('TOKEN'))