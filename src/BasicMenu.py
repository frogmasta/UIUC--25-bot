import math

import discord
from discord.ext import menus


class RoleMenu(menus.Menu):
    def __init__(self, title, data, page=1, *, is_leaderboard=False, footer_message=None):
        super().__init__()

        self.title = title
        self.data = data
        self.is_leaderboard = is_leaderboard
        self.footer_message = footer_message

        self._embed = None

        if len(self.data) <= 0:
            raise ValueError("No data found!")
        self._maxPages = math.ceil(len(self.data) / 10)

        if page < 1 or page > self._maxPages:
            raise IndexError("Number out of bounds!")
        self._page = page

    async def send_initial_message(self, ctx, channel):
        self.generate_embed(ctx.message.author.avatar_url)
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
            self.generate_embed(self._embed.footer.icon_url)
            await self.message.edit(embed=self._embed)

    def generate_embed(self, icon):
        data_list = self.generate_data_list()

        embed = discord.Embed(title=self.title, description=data_list, color=0xFF4500)
        if self.footer_message:
            embed.set_footer(text=f"Page {self._page}/{self._maxPages} | {self.footer_message}", icon_url=icon)
        else:
            embed.set_footer(text=f"Page {self._page}/{self._maxPages}", icon_url=icon)

        self._embed = embed

    def generate_data_list(self):
        data_list = ""

        start_idx = (self._page - 1) * 10
        for idx in range(start_idx, start_idx + 10):
            row = ''

            if self.is_leaderboard:
                place = idx + 1

                if 1 <= place <= 3:
                    row += ['👑', '🥈', '🥉'][place-1] + " - "
                else:
                    row += f"#{place} - "

            try:
                if isinstance(self.data, list):
                    row += f"{self.data[idx]} \n\n"
                elif isinstance(self.data, dict):
                    keys = sorted(list(self.data.keys()), key=lambda k: self.data[k], reverse=True)
                    row += f"{keys[idx]}: {self.data[keys[idx]]} \n\n"
            except IndexError:
                break

            data_list += row

        return data_list
