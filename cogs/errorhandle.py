import traceback
from typing import Literal, Optional

import discord
from discord.ext import commands
from utils import error, template


class Error(commands.Cog):
    """Handles errors related to the bot."""

    def __init__(self, bot):
        self.bot = bot

    # NOTE: By moving most of discord_templates here, whenever a custom error is raised,
    # you can just return the embed in the context that the error was raised in. 

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, e: Exception):
        match e:
            case discord.NotFound:
                return await ctx.send('Given message does not exist in this channel.')
            case (discord.Forbidden, commands.CommandNotFound):
                return
            # Another benefit of subclassing your own exception type:
            # Since all your commands subclasses CommandException,
            # They can be handled by this match case statement
            case error.CommandException:
                # TODO: Write error message + jump link
                # return await ctx.send(embed=e.to_embed())
                pass
            case _:
                tb = traceback.format_exception(type(error), error, error.__traceback__)
                tb_str = ''.join(tb[:-1]) + f'\n{tb[-1]}'
                message = await ctx.bot.owner.send(embed=self.to_embed("error", f'```{tb_str}```', ctx.message.jump_url))
                await ctx.channel.send(embed=template.error('```Internal Error, report submitted.```', message.jump_url))


async def setup(bot):
    await bot.add_cog(Error(bot))
