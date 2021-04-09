# Environment configuration dependencies
import os

# discord.py dependencies
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load in environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Create bot client
bot = commands.Bot(command_prefix='*')


@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.idle, activity=discord.Game('Season 2 WYA??'))
    print('Goku is ready!')


# Load extensions/cogs
for cog in os.listdir('./cogs'):
    if cog.endswith('.py'):
        try:
            bot.load_extension('cogs.' + cog.removesuffix('.py'))
        except Exception as e:
            print("There has been an error loading a cog")
            raise e

bot.run(TOKEN)
