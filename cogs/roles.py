import asyncio
import difflib

import discord
from discord import utils
from discord.ext import commands

from src.BasicMenu import RoleMenu
from src.role_list import role_names


class RoleManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['add'])
    @commands.has_any_role("Kingfishers", "Big Fish")
    async def assign(self, ctx, *, role: discord.Role):
        if role.name not in role_names:
            return await ctx.send("I cannot assign this role!")
        elif role in ctx.message.author.roles:
            return await ctx.send("You already have that role!")

        try:
            await ctx.message.author.add_roles(role)
        except discord.Forbidden:
            return await ctx.send("I do not have the permission to add that role!")

        await ctx.send("Role change successful!")

    @commands.command(aliases=['remove'])
    @commands.has_any_role("Kingfishers", "Big Fish")
    async def unassign(self, ctx, *, role: discord.Role):
        if role.name not in role_names:
            return await ctx.send("I cannot remove this role!")
        elif role not in ctx.message.author.roles:
            return await ctx.send("You do not have that role!")

        try:
            await ctx.message.author.remove_roles(role)
        except discord.Forbidden:
            return await ctx.send("I do not have the permission to remove that role!")

        await ctx.send("Role removal successful!")

    @commands.command()
    async def students(self, ctx, *, role: discord.Role):
        people = list(filter(lambda member: role in member.roles, ctx.guild.members))
        people = [f"{person.mention} {person}" for person in people]

        try:
            menu = RoleMenu(f"{role.name}", people, footer_message="Some user mentions may not work!")
            await menu.start(ctx)
        except Exception as err:
            if isinstance(err, ValueError):
                await ctx.send('There is nobody with this major in the server!')

    @commands.command(aliases=['roles'])
    async def majors(self, ctx, page=1):
        try:
            menu = RoleMenu("Majors", role_names, page)
            await menu.start(ctx)
        except IndexError:
            await ctx.send("The page number you specified is out of bounds!")

    @commands.command()
    async def stats(self, ctx, page=1):
        role_count = get_role_count(ctx)
        try:
            menu = RoleMenu("Major Statistics", role_count, page, is_leaderboard=True)
            await menu.start(ctx)
        except Exception as err:
            if isinstance(err, IndexError):
                await ctx.send("The page number you specified is out of bounds!")
            elif isinstance(err, ValueError):
                await ctx.send("This server has no major roles to display stats for!")

    async def find_closest_match(self, ctx, role_name):
        close_matches = difflib.get_close_matches(role_name, role_names)

        def checkmsg(m):
            if m.content.lower() in ["stop", "s", "no", "n", "yes", "y"] and m.author == ctx.message.author:
                return True

            return False

        for match_idx in range(0, 3):
            if match_idx >= len(close_matches):
                break

            await ctx.send(f"Did you mean {close_matches[match_idx]}? (Y/N/Stop)")
            try:
                msg = await self.bot.wait_for("message", check=checkmsg, timeout=30)
            except asyncio.TimeoutError:
                return f"Response timed-out for {ctx.message.author.mention}"

            if msg.content.lower() in ["yes", "y"]:
                return utils.get(ctx.guild.roles, name=close_matches[match_idx])
            elif msg.content.lower() in ["no", "n"]:
                continue
            elif msg.content.lower() in ["stop", "s"]:
                return "Stopped looking for major!"

        return "Could not find specified major. Please try again."

    @assign.error
    @unassign.error
    @students.error
    async def role_not_found_error(self, ctx, error):
        if isinstance(error, commands.RoleNotFound):
            response = await self.find_closest_match(ctx, error.argument)

            if not isinstance(response, discord.Role):
                return await ctx.send(response)

            await ctx.invoke(ctx.command, role=response)

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            return await ctx.send("Please specify a role!")
        elif isinstance(error, commands.errors.MissingAnyRole):
            return await ctx.send("You need the Kingfishers or Big Fish role to use major role commands!")
        elif isinstance(error, commands.RoleNotFound):
            return

        raise error


def get_role_count(ctx):
    role_count = {}

    for member in ctx.guild.members:
        for role in member.roles:
            if role.name in role_names and role in role_count:
                role_count[role] += 1
            elif role.name in role_names:
                role_count[role] = 1

    return role_count


def setup(bot):
    bot.add_cog(RoleManager(bot))
