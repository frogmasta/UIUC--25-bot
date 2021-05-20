import os

import asyncpraw
import asyncprawcore
from discord.ext import commands
from dotenv import load_dotenv

from src.RedditMenu import RedditMenu
from src.help_descriptions import reddit_help, meme_help

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

    @commands.command(**meme_help)
    async def meme(self, ctx, *args):
        await self.reddit_command(ctx, args, sub='memes')

    @commands.command(aliases=['redfetch', 'subreddit', 'sub'], **reddit_help)
    async def reddit(self, ctx, *args):
        await self.reddit_command(ctx, args)

    async def reddit_command(self, ctx, args, **defaults):
        options = await self.reddit_arg_parser(ctx, args)
        for option_name in defaults:
            options[option_name] = defaults[option_name]

        try:
            submissions, sub = await self.fetch_submissions(**options)
        except ValueError as err:
            return await ctx.send(err)
        rmenu = RedditMenu(reddit, submissions, sub)
        await rmenu.start(ctx)

    @staticmethod
    async def fetch_submissions(sub, order, *, time='day', nsfw=False):
        global reddit

        # Get subreddit
        try:
            sub = await reddit.subreddit(sub, fetch=True)
        except Exception as e:
            if isinstance(e, asyncprawcore.Forbidden):
                raise ValueError(f"Subreddit **r/{sub}** is either private or quarantined 😃")
            elif isinstance(e, asyncprawcore.NotFound) or isinstance(e, asyncprawcore.Redirect):
                raise ValueError(f"Subreddit **r/{sub}** could not be found 😭")

        # NSFW check for subreddit
        if not nsfw and sub.over18:
            raise ValueError("You're attempting to fetch an NSFW sub in a non-NSFW channel -_-")

        # Order the result based on user input
        try:
            limit = 20
            sort_method = getattr(sub, order)
        except AttributeError:
            raise ValueError(f"Could not find a **{order}** order method!")

        if sort_method.__name__ == 'top':
            try:
                submission_gen = sort_method(time, limit=limit)
            except ValueError:
                raise ValueError(f"Could not find a way to filter top by **{time}** 😐")
        else:
            submission_gen = sort_method(limit=limit)

        # List of submissions with NSFW filter
        submissions = []
        async for p in submission_gen:
            if not p.over_18 or nsfw:
                submissions.append(p)

        return submissions, sub

    @staticmethod
    async def reddit_arg_parser(ctx, args):
        defaults = {
            "sub": "UIUC",
            "order": "hot",
        }

        for option in args:
            option = str(await commands.clean_content().convert(ctx, option))
            if option == 'random':
                option = 'random_rising'

            if option.startswith(('/r/', 'r/')):
                defaults['sub'] = option.split('r/')[-1]
            elif option in ['controversial', 'hot', 'new', 'top', 'random_rising', 'random', 'rising']:
                defaults['order'] = option
            else:
                defaults['time'] = option

        return defaults


def setup(bot):
    bot.add_cog(DiscordReddit(bot))
