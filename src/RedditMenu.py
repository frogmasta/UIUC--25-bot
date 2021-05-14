import discord
from discord.ext import menus


class RedditMenu(menus.Menu):
    def __init__(self, reddit, submissions, page=1):
        super().__init__()

        self.reddit = reddit
        self.submissions = submissions

        self._embed = None

        self._maxPages = len(self.submissions)
        if self._maxPages <= 0:
            raise ValueError("No data found!")

        if page < 1 or page > self._maxPages:
            raise IndexError("Number out of bounds!")
        self._page = page

    async def send_initial_message(self, ctx, channel):
        await self.generate_embed()
        return await ctx.send(embed=self._embed)

    @menus.button('⬅️')
    async def on_arrow_left(self, payload):
        await self.move_page(-1)

    @menus.button("➡️")
    async def on_arrow_right(self, payload):
        await self.move_page(1)

    async def move_page(self, increment):
        if 1 <= self._page + increment <= self._maxPages:
            self._page += increment
            await self.generate_embed()
            await self.message.edit(embed=self._embed)

    async def generate_embed(self):
        post = self.submissions[self._page - 1]

        if post.author:
            await post.author.load()
            author_name = post.author.name
            author_icon = post.author.icon_img
        else:
            author_name = '[deleted]'
            author_icon = 'https://www.redditstatic.com/avatars/avatar_default_02_FF4500.png'

        sub = post.subreddit
        await sub.load()

        desc = f'Score: {post.score} | Upvote Ratio: {int(post.upvote_ratio * 100)}%\n'

        embed = discord.Embed(title=post.title, description=desc, color=0xFF4500,
                              url="https://reddit.com" + post.permalink)

        # Distinguish between text, image, and cross posts
        if post.is_self:
            embed.description += f'\n{post.selftext}'
            if len(embed.description) > 2000:
                embed.description = embed.description[0:1997] + "..."
        elif hasattr(post, "crosspost_parent"):
            crosspost = await self.reddit.submission(id=post.crosspost_parent.split("_")[1])
            embed.description += '\nCrosspost from:\n\nhttps://reddit.com' + crosspost.permalink
        else:
            embed.set_image(url=post.url)

        embed.set_author(name=author_name, icon_url=author_icon, url=f"https://reddit.com/user/{author_name}")
        embed.set_footer(text=f'Fresh from r/{sub} | Page {self._page}/{self._maxPages}', icon_url=sub.community_icon)

        self._embed = embed
