import os
import pathlib

import discord
from discord.ext import commands
from dotenv import load_dotenv

from src.copypasta import copypasta_dict

# Load in environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Create bot client
intents = discord.Intents.all()
activity = discord.Activity(type=discord.ActivityType.listening, name="i-")
bot = commands.Bot(command_prefix='i-', activity=activity, status=discord.Status.online, intents=intents)


# Tells when bot is ready
@bot.event
async def on_ready():
    print("Ready!")


# Calls every message
@bot.event
async def on_message(message):
    # Don't call if message written by a bot
    if message.author.bot:
        return

    # Copypasta handler
    contents = message.content.split()
    for word in contents:
        if word.lower() in copypasta_dict or word in copypasta_dict:
            try:
                msg_parts = copypasta_dict[word.lower()].split('\n')
            except KeyError:
                msg_parts = copypasta_dict[word].split('\n')

            for part in msg_parts:
                await message.channel.send(part)

            break

    # Process other commands if applicable
    await bot.process_commands(message)


# Command error handler
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("That is not a command!")
        return

    if ctx.command.has_error_handler() or ctx.cog.has_error_handler():
        return

    raise error


# Load extensions/cogs
path = pathlib.Path(__file__).parent
for cog in os.listdir(path / "cogs"):
    if cog.endswith('.py'):
        try:
            bot.load_extension('cogs.' + cog.removesuffix('.py'))
        except Exception as e:
            print("There has been an error loading a cog")
            raise e

# Run bot
bot.run(TOKEN)
