from discord.ext import commands

from src.help_descriptions import info_help, cup_help


class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(**info_help)
    async def info(self, ctx):
        await ctx.send("This is the bot for the UIUC '25 discord server. Any suggestions or bug reports can be sent to "
                       "<@568118705553408040>. If you want to make your own improvement or raise an issue, head over "
                       "to the public repository for the project at https://github.com/frogmasta/UIUC--25-bot")

    @commands.command(**cup_help)
    async def cup(self, ctx):
        await ctx.send("Go back to middle school 🤣")


def setup(bot):
    bot.add_cog(Information(bot))
