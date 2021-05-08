import difflib

import discord
from discord import utils
from discord.ext import commands

from src.role_list import roles
from src.role_menu import RoleMenu


class RoleManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_any_role("Kingfishers", "Big Fish")
    async def assign(self, ctx, *, role_name):
        role = utils.get(ctx.guild.roles, name=role_name)

        if role and role.name not in roles:
            return await ctx.send("I cannot assign this role!")
        if not role:
            role = await self.find_closest_match(ctx, role_name)

        if not role:
            return await ctx.send("Could not find a close match. Please try again.")
        elif role in ctx.message.author.roles:
            return await ctx.send("You already have that role!")

        try:
            await ctx.message.author.add_roles(role)
        except discord.Forbidden:
            return await ctx.send("I do not have the permission to add that role!")

        await ctx.send("Role change successful.")

    @commands.command()
    @commands.has_any_role("Kingfishers", "Big Fish")
    async def remove(self, ctx, *, role_name):
        role = utils.get(ctx.guild.roles, name=role_name)

        if role and role.name not in roles:
            return await ctx.send("I cannot remove this role!")
        if not role:
            role = await self.find_closest_match(ctx, role_name)

        if not role:
            return await ctx.send("Could not find a close match. Please try again.")
        elif role not in ctx.message.author.roles:
            return await ctx.send("You do not have that role!")

        try:
            await ctx.message.author.remove_roles(role)
        except discord.Forbidden:
            return await ctx.send("I do not have the permission to remove that role!")

        await ctx.send("Role removal successful!")

    @commands.command()
    async def roles(self, ctx):
        menu = RoleMenu()
        await menu.start(ctx)

    async def find_closest_match(self, ctx, role_name):
        close_matches = difflib.get_close_matches(role_name, roles)

        def checkmsg(m):
            if m.content.lower() in ["stop", "s", "no", "n", "yes", "y"] and m.author == ctx.message.author:
                return True

            return False

        for match_idx in range(0, 3):
            if match_idx >= len(close_matches):
                break

            await ctx.send(f"Did you mean {close_matches[match_idx]}? (Y/N/Stop)")
            msg = await self.bot.wait_for("message", check=checkmsg)

            if msg.content.lower() in ["yes", "y"]:
                return utils.get(ctx.guild.roles, name=close_matches[match_idx])
            elif msg.content.lower() in ["no", "n"]:
                continue
            elif msg.content.lower() in ["stop", "s"]:
                break

        return None

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            return await ctx.send("Please specify a role!")
        elif isinstance(error, commands.errors.MissingAnyRole):
            return await ctx.send("You need the Kingfishers or Big Fish role to use major role commands!")

        raise error


def setup(bot):
    bot.add_cog(RoleManager(bot))
