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

    @staticmethod
    def to_embed(
        type: Literal["error", "warning", "info"], 
        message: str, jump_url: Optional[str] = ''
    ) -> discord.Embed:
        """Formats exceptions into Discord-style embeds."""
        if jump_url:
            jump_url = f'\n[Jump]({jump_url})'
        embed_type = {
            "error": discord.Colour.red(), 
            "warning": discord.Colour.yellow(), 
            "info": discord.Colour.light_grey()
        }
        return discord.Embed(
            title=type.capitalize(),
            description=message+jump_url,
            colour=embed_type[type]
        )

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, (discord.errors.Forbidden, commands.errors.CommandNotFound)):
            return
        tb = traceback.format_exception(type(error), error, error.__traceback__)
        tb_str = ''.join(tb[:-1]) + f'\n{tb[-1]}'
        message = await ctx.bot.owner.send(embed=self.to_embed("error", f'```{tb_str}```', ctx.message.jump_url))
        await ctx.channel.send(embed=template.error('```Internal Error, report submitted.```', message.jump_url))


async def setup(bot):
    await bot.add_cog(Error(bot))
