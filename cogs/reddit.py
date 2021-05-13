import os

import asyncpraw
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

authid = os.getenv('REDDIT_ID')
secret = os.getenv('REDDIT_SECRET')
usragent = os.getenv('REDDIT_USER_AGENT')

reddit = asyncpraw.Reddit(client_id=authid,
                          client_secret=secret,
                          user_agent=usragent)


class Reddit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def genfetch(sub, ctx, nsfw=False):
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

        post = await sub.random()
        if not post:
            async for x in sub.random_rising():
                post = x
                break

        if not nsfw and post.over_18:
            for x in range(3):
                x = await sub.random()
                if not x:
                    async for i in sub.random_rising():
                        post = x
                        break
                if not post.over_18:
                    break
            if post.over_18:
                await ctx.send("Couldn't find SFW content :/")
                return

        await post.author.load()
        author = post.author.name
        pfp = post.author.icon_img
        desc = f'Score: {post.score} | Upvote Ratio: {int(post.upvote_ratio*100)}%\n'
        embed=discord.Embed(title=post.title, description=desc, color=0xc6a679, url="https://reddit.com"+post.permalink)
        if post.selftext!='':
            embed.description+=f'\n{post.selftext}'
            if len(embed.description)>2000:
                embed.description=embed.description[0:1997]+"..."
        else:
            embed.set_image(url=post.url)
        embed.set_author(name=author, icon_url=(pfp), url=f"https://reddit.com/user/{author}")
        embed.set_footer(text = f'Fresh from r/{sub}')
        await ctx.send(embed=embed)

    @commands.command(brief="It's time to c-c-c-c-cringe",
                      description="I don't know if it's dank, but it's definitely a meme")
    async def meme(self, ctx):
        await self.genfetch('memes', ctx)

    @commands.command(brief="Shitty reddit in discord",
                      description="Why use reddit when you can use shitty reddit?",
                      aliases=['redfetch', 'subreddit', 'sub'])
    async def reddit(self, ctx, subred='UIUC'):
        if subred.startswith(('/r/', 'r/')):
            subred = subred.split('r/')[-1]

        await self.genfetch(subred, ctx)


def setup(bot):
    bot.add_cog(Reddit(bot))
