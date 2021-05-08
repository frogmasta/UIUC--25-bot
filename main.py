import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from src.copypasta import copypasta_dict

# Load in environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Create bot client
activity = discord.Activity(type=discord.ActivityType.listening, name="i~")
bot = commands.Bot(command_prefix='i~', activity=activity, status=discord.Status.online)


# Tells when bot is ready
@bot.event
async def on_ready():
    print("Ready!")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    contents = message.content.split()

    for word in contents:
        if word.lower() in copypasta_dict or word in copypasta_dict:
            try:
                return await message.channel.send(copypasta_dict[word.lower()])
            except KeyError:
                return await message.channel.send(copypasta_dict[word])

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
for cog in os.listdir('./cogs'):
    if cog.endswith('.py'):
        try:
            bot.load_extension('cogs.' + cog.removesuffix('.py'))
        except Exception as e:
            print("There has been an error loading a cog")
            raise e

# Run bot
bot.run(TOKEN)
