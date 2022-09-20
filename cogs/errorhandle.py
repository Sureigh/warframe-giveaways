from discord.ext import commands
import discord
import traceback

from utils import template


class Error(commands.Cog):
    """Handles errors related to the bot."""

    def __init__(self, bot):
        self.bot = bot

    # NOTE: By moving most of discord_templates here, whenever a custom error is raised,
    # you can just return the embed in the context that the error was raised in.

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            return await ctx.send(
                embed=template.error('You don\'t have permission to use this command'),
                reference=ctx.message
            )
        if isinstance(error, (discord.ext.commands.errors.CommandNotFound, discord.errors.Forbidden)):
            return
        tb = traceback.format_exception(type(error), error, error.__traceback__)
        tb_str = ''.join(tb[:-1]) + f'\n{tb[-1]}'
        message = await self.bot.owner.send(embed=template.error(f'```{tb_str}```', ctx.message.jump_url))
        await ctx.channel.send(embed=template.error('Internal Error, report submitted.', message.jump_url))


async def setup(bot):
    await bot.add_cog(Error(bot))
