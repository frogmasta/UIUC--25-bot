import math

import discord
from discord.ext import menus

from src.role_list import roles


class RoleMenu(menus.Menu):
    def __init__(self):
        super().__init__()

        self.title = "Roles List"
        self.data = roles

        self._embed = None
        self._page = 1
        self._maxPages = math.ceil(len(self.data) / 10)

    async def send_initial_message(self, ctx, channel):
        icon = ctx.message.author.avatar_url
        role_list = self.generate_role_list()

        embed = discord.Embed(title=self.title, description=role_list, color=0xFF4500)
        embed.set_footer(text=f"Page {self._page}/{self._maxPages}", icon_url=icon)

        self._embed = embed
        return await ctx.send(embed=embed)

    @menus.button('⬅️')
    async def on_arrow_left(self, payload):
        await self.move_page(-1)

    @menus.button("➡️")
    async def on_arrow_right(self, payload):
        await self.move_page(1)

    async def move_page(self, increment):
        icon = self._embed.footer.icon_url

        if 1 <= self._page + increment <= self._maxPages:
            self._page += increment
            role_list = self.generate_role_list()

            embed = discord.Embed(title=self.title, description=role_list, color=0xFF4500)
            embed.set_footer(text=f"Page {self._page}/{self._maxPages}", icon_url=icon)

            self._embed = embed
            await self.message.edit(embed=self._embed)

    def generate_role_list(self):
        role_list = ""

        start_idx = (self._page - 1) * 10
        for idx in range(start_idx, start_idx + 10):
            try:
                role_list += f"{roles[idx]} \n\n"
            except IndexError:
                break

        return role_list
