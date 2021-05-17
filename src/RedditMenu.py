import pathlib
import re
from math import floor
from statistics import mean

import discord
import requests
from PIL import Image
from discord.ext import menus

from src.aws import upload_to_aws

DEFAULT_ICON = 'https://www.redditstatic.com/avatars/avatar_default_02_FF4500.png'


class RedditMenu(menus.Menu):
    def __init__(self, reddit, submissions, sub, page=1):
        super().__init__()

        self.reddit = reddit
        self.submissions = submissions
        self.sub = sub

        self._embed = None

        self._maxPages = len(self.submissions)
        if self._maxPages <= 0:
            raise ValueError("No data found!")

        if page < 1 or page > self._maxPages:
            raise IndexError("Number out of bounds!")
        self._page = page

    async def send_initial_message(self, ctx, channel):
        msg = await self.generate_embed()
        if msg:
            await msg.edit(embed=self._embed)
            return msg
        else:
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
        msg = None
        post = self.submissions[self._page - 1]

        if post.author:
            await post.author.load()
            author_name = post.author.name
            if hasattr(post.author, 'is_suspended') and post.author.is_suspended:
                author_icon = DEFAULT_ICON
            else:
                author_icon = post.author.icon_img
        else:
            author_name = '[deleted]'
            author_icon = DEFAULT_ICON

        title = post.title
        desc = f'Score: {post.score} | Comments: {post.num_comments} | Upvote Ratio: {int(post.upvote_ratio * 100)}%\n'

        # Distinguish between text, image, and cross posts
        post_hint = post.__dict__.get('post_hint', '')
        urllist = self.urls_in_selftext(post.selftext)
        iurl = None
        if post.domain == 'v.redd.it' or 'video' in post_hint:
            if self.message is not None:
                await self.message.edit(embed=self.loading_embed())
            else:
                msg = await self.ctx.send(embed=self.loading_embed())

            iurl = await self.preview_image_url(post, f"{post.id}.png")
            title += " [VIDEO]"
        elif post.domain == 'i.redd.it' or 'image' in post_hint or len(urllist) > 0:
            if len(urllist):
                iurl = urllist[0]
            else:
                iurl = post.url
        elif post.is_self:
            desc += f'\n{post.selftext}'
        elif hasattr(post, "crosspost_parent"):
            crosspost = await self.reddit.submission(id=post.crosspost_parent.split("_")[1])
            desc += '\nCrosspost from:\nhttps://reddit.com' + crosspost.permalink
        elif hasattr(post, "gallery_data"):
            if 'caption' in post.gallery_data['items'][0]:
                desc += post.gallery_data['items'][0]['caption']

            iurl = post.media_metadata[post.gallery_data['items'][0]['media_id']]['s']['u']
            title += " [GALLERY]"
        elif 'link' in post_hint:
            desc += f"\n{post.url_overridden_by_dest}"

        if len(title) > 120:
            title = title[:117] + '...'
        if len(desc) > 2000:
            desc = desc[0:1997] + "..."

        embed = discord.Embed(title=title, description=desc, color=0xFF4500,
                              url="https://reddit.com" + post.permalink)
        embed.set_author(name=author_name, icon_url=author_icon, url=f"https://reddit.com/user/{author_name}")
        embed.set_footer(text=f'Fresh from r/{self.sub} | Page {self._page}/{self._maxPages}',
                         icon_url=self.sub.community_icon)
        if iurl is not None:
            embed.set_image(url=iurl)

        self._embed = embed
        return msg

    @staticmethod
    def loading_embed():
        lgif = 'https://i.ibb.co/qJCSkf2/lgif.gif'
        embed = discord.Embed(title='Loading...', color=0xFF4500)
        embed.set_image(url=lgif)
        return embed

    @staticmethod
    async def preview_image_url(post, name_of_file):
        try:
            p_url = post.preview['images'][0]['source']['url']
        except AttributeError:
            await post.load()
            p_url = post.preview['images'][0]['source']['url']

        bimg_path = pathlib.Path(__file__).parent / "play_button.png"

        play_button = Image.open(bimg_path).convert('RGBA')
        preview = Image.open(requests.get(p_url, stream=True).raw).convert('RGBA')

        ratio = mean([preview.size[0] / play_button.size[0], preview.size[1] / play_button.size[1]]) / 6
        play_button = play_button.resize((floor(play_button.size[0] * ratio),
                                          floor(play_button.size[1] * ratio)))

        pre_w, pre_h = preview.size
        pb_w, pb_h = play_button.size
        offset = ((pre_w - pb_w) // 2, (pre_h - pb_h) // 2)

        final = Image.new('RGBA', preview.size)
        final.paste(preview, (0, 0), preview)
        final.paste(play_button, offset, play_button)

        temp_fpath = pathlib.Path(__file__).parent / "temp.png"
        final.save(temp_fpath)
        upload_to_aws(str(temp_fpath), name_of_file)

        return 'https://rpreview-images.s3.us-east-2.amazonaws.com/' + name_of_file

    @staticmethod
    def urls_in_selftext(text):
        urllist = re.findall(r'(https?://preview.redd.it[^\s]+)', text)
        return urllist
