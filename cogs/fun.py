import random
import re

from discord.ext import commands

from src.help_descriptions import _8ball_help

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['8ball'], **_8ball_help)
    async def _8ball(self, ctx, *, question):
        san_question = sanitize_mentions(question)
        responses = ['It is certain', 'It is decidedly so', 'Without a doubt', 'Yes – definitely', 'You may rely on it',
                     'As I see it, yes', 'Most likely', 'Outlook good', 'Signs point to yes', 'Reply hazy',
                     'Try again',
                     'Ask again later', 'Better not tell you now', 'Cannot predict now', 'Concentrate and ask again',
                     'Don\'t count on it', 'My reply is no', 'My sources say no', 'Outlook not so good',
                     'Very doubtful']
        await ctx.send(f'Question: {san_question} \nAnswer: {random.choice(responses)}')

    @_8ball.error
    async def _8ball_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Please provide a question for me to answer!')

def sanitize_mentions(text):
    return re.sub("<@.*?>", "", text)

def setup(bot):
    bot.add_cog(Fun(bot))

