import os

import asyncpraw
import asyncprawcore
from discord.ext import commands
from dotenv import load_dotenv

from src.RedditMenu import RedditMenu

load_dotenv()

authid = os.getenv('REDDIT_ID')
secret = os.getenv('REDDIT_SECRET')
usragent = os.getenv('REDDIT_USER_AGENT')

reddit = asyncpraw.Reddit(client_id=authid,
                          client_secret=secret,
                          user_agent=usragent)


class DiscordReddit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="It's time to c-c-c-c-cringe",
                      description="I don't know if it's dank, but it's definitely a meme")
    async def meme(self, ctx, *args):
        options = self.reddit_arg_parser(args)
        options['sub'] = 'memes'

        submissions = await self.fetch_submissions(ctx, **options)
        rmenu = RedditMenu(reddit, submissions)
        await rmenu.start(ctx)

    @commands.command(brief="Shitty reddit in discord",
                      description="Why use reddit when you can use shitty reddit?",
                      aliases=['redfetch', 'subreddit', 'sub'])
    async def reddit(self, ctx, *args):
        options = self.reddit_arg_parser(args)

        submissions = await self.fetch_submissions(ctx, **options)
        rmenu = RedditMenu(reddit, submissions)
        await rmenu.start(ctx)

    @staticmethod
    async def fetch_submissions(ctx, sub, order, *, time='day', nsfw=False):
        global reddit

        # Get subreddit
        try:
            sub = await reddit.subreddit(sub, fetch=True)
        except Exception as e:
            if isinstance(e, asyncprawcore.Forbidden):
                return await ctx.send("Subreddit is either private or quarantined 😃")
            elif isinstance(e, asyncprawcore.NotFound) or isinstance(e, asyncprawcore.Redirect):
                return await ctx.send("Subreddit could not be found 😭")

        # NSFW check for subreddit
        if not nsfw and sub.over18:
            return await ctx.send("You're attempting to fetch an NSFW sub in a non-NSFW channel -_-")

        # Order the result based on user input
        try:
            limit = 50
            sort_method = getattr(sub, order)
            if sort_method.__name__ == 'top':
                submission_gen = sort_method(time, limit=limit)
            else:
                submission_gen = sort_method(limit=limit)
        except AttributeError:
            return await ctx.send(f"Could not find a {order} order method!")

        # List of submissions with NSFW filter
        submissions = []
        async for p in submission_gen:
            if not p.over_18 or nsfw:
                submissions.append(p)

        return submissions

    @staticmethod
    def reddit_arg_parser(args):
        defaults = {
            "sub": "UIUC",
            "order": "hot",
        }

        for option in args:
            if option == 'random':
                option = 'random_rising'

            if option.startswith(('/r/', 'r/')):
                defaults['sub'] = option.split('r/')[-1]
            elif option in ['controversial', 'hot', 'new', 'top', 'random_rising', 'random', 'rising']:
                defaults['order'] = option
            elif option in ['hour', 'today', 'week', 'month', 'year', 'all']:
                defaults['time'] = option

        return defaults


def setup(bot):
    bot.add_cog(DiscordReddit(bot))
