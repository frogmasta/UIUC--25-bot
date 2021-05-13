import asyncpraw
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

authid=os.getenv('REDDIT_ID')
secret=os.getenv('REDDIT_SECRET')
usragent=os.getenv('REDDIT_USER_AGENT')

reddit = asyncpraw.Reddit(client_id=authid,
                     client_secret=secret,
                     user_agent=usragent)

class Reddit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def genfetch(self, sub, ctx, nsfw=False):
        global reddit
        try:
            sub = await reddit.subreddit(sub)
            await sub.load()
        except:
            await ctx.send("Subreddit could not be found.")
            return

        if not nsfw and sub.over18:
            await ctx.send("You're attempting to fetch an NSFW sub in a non-NSFW channel -_-")
            return

        i = await sub.random()
        if not i:
            async for x in sub.random_rising():
                i = x
                break

        if not nsfw and i.over_18:
            for i in range(3):
                i = await sub.random()
                if not i:
                    async for x in sub.random_rising():
                        i = x
                        break
                if not i.over_18:
                    break
            if i.over_18:
                await ctx.send("Couldn't find SFW content :/")
                return

        title = i.title
        permalink = i.permalink
        url = i.url
        score = i.score
        ratio = i.upvote_ratio
        await i.author.load()
        author = i.author.name
        pfp = i.author.icon_img
        desc = f'Score: {score} | Upvote Ratio: {int(ratio*100)}%\n'
        embed=discord.Embed(title=title, description=desc, color=0xc6a679, url="https://reddit.com"+permalink)
        if i.selftext!='':
            embed.description+=f'\n{i.selftext}'
            if len(embed.description)>2000:
                embed.description=embed.description[0:1997]+"..."
        else:
            embed.set_image(url=url)
        embed.set_author(name=author, icon_url=(pfp), url=f"https://reddit.com/user/{author}")
        embed.set_footer(text = f'Fresh from r/{sub}')
        await ctx.send(embed=embed)

    @commands.command(brief="It's time to c-c-c-c-cringe", description="I don't know if it's dank, but it's definitely a meme")
    async def meme(self, ctx):
        await self.genfetch('memes', ctx)

    @commands.command(brief="Shitty reddit in discord.", description="Why use reddit when you can use shitty reddit?")
    async def sub(self, ctx, subred):
        await self.genfetch(subred, ctx)

def setup(bot):
    bot.add_cog(Reddit(bot))
