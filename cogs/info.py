from discord.ext import commands


class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def info(self, ctx):
        await ctx.send("This is the bot for the UIUC '25 discord server. Any suggestions or bug reports can be sent to "
                       "<568118705553408040> or raised as an issue at https://github.com/frogmasta/UIUC--25-bot")

    @commands.command()
    async def cup(self, ctx):
        await ctx.send("Go back to middle school 🤣")


def setup(bot):
    bot.add_cog(Information(bot))
