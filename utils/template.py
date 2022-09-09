import re
import traceback
from typing import Dict, Iterable, List, Tuple, Union

import discord
from discord.ext import commands

from utils.error import NotUser


def running_giveaway(
        unix: int,
        winners: int,
        description: str,
        holder: Holder,
        display_title: bool = False,
        prize: str = None
    ) -> discord.Embed:

    if not display_title:
        prize = None

    embed = discord.Embed(
        title=prize,
        description=description,
        colour=discord.Colour.green()
    )

    embed.add_field(**__contact_type__(holder))
    embed.add_field(name='Ending:', value=f'<t:{unix}:R> (<t:{unix}>)')

    footer_text = f'{winners} winner'
    if winners > 1:
        footer_text += 's'
    if holder.tag:  # Mentions don't work for footer
        if str(holder):
            footer_text += f' | {holder}'
    embed.set_footer(text=footer_text)
    return embed


def giveaway_result(
        winners: Iterable[str],
        prize: str,
        holder: Holder,
        giveaway_link: str,
        mention_users: Union[Iterable[str], bool] = False,
        reroll: bool = False) \
        -> Dict[str, Union[discord.Embed, str]]:
    """Return value to be used as kwargs for discord.abc.Messageable.send()"""

    # sets message content to winner arg if True
    # sets message content to mention_users if mention_users
    # sets message content to None if False
    if mention_users is True:
        mention_winners = ' '.join(winners)
    elif mention_users:
        mention_winners = ' '.join(mention_users)
    else:
        mention_winners = ''

    contact = holder.mention if holder.mention else holder.tag
    if reroll:
        title = 'Giveaway was rerolled'
        colour = discord.Colour.dark_blue()
    else:
        title = 'Giveaway result'
        colour = discord.Colour.blue()
    embed = discord.Embed(
        colour=colour,
        title=title
    )
    embed.add_field(name='Prize:', value=f'{prize}', inline=True)
    embed.add_field(**__contact_type__(holder))
    embed.add_field(name='Winners:', value='\n'.join(winners), inline=False)
    embed.add_field(name='Jump', value=f'[to giveaway]({giveaway_link})', inline=False)
    embed.set_footer(text=str(holder))

    return {
        'content': mention_winners,
        'embed': embed
    }


def __contact_type__(holder: Holder) -> dict:
    contact = holder.mention if holder.mention else holder.tag

    if not str(holder):
        raise Exception('__contact_type__ cannot be used when holder.string is empty or None')

    hosted_by = re.search('Hosted by: .*', str(holder), re.IGNORECASE)
    if hosted_by:
        return {'name': 'Hosted by:', 'value': contact, 'inline': True}
    elif re.search('Contact (.*) to claim your prize', str(holder), re.IGNORECASE):
        return {'name': 'Item Holder:', 'value': contact, 'inline': True}


def winner_guide(prize, giveaway_link, holder_tag):
    embed = discord.Embed(
        colour=discord.Colour.blue(),
        title="Congratulations!",
        description=f"You won: **{prize}**\n"
                    "Send a message here to contact item holder to claim your prize")
    embed.add_field(name="Jump", value=f"[to giveaway]({giveaway_link})")
    embed.set_footer(text=f"Item holder: {holder_tag}")

    return embed


def no_winner(jump_url, message: str=None) -> discord.Embed:
    embed = discord.Embed(
        title='No winner found!',
        description=message
    )
    embed.add_field(name='Jump', value=f'[to giveaway]({jump_url})')
    return embed


async def create_thread(
        channel: discord.TextChannel,
        name: str,
        type_=discord.ChannelType.private_thread,
        add_users: Iterable[int] = (),
        mention_users: Union[Iterable[int], bool] = False,
        add_roles: Iterable[int] = (),
        start_msg: Union[str, discord.Embed, dict] = None,
) -> discord.Thread:
    """Creates thread"""
    try:
        thread = await channel.create_thread(name=name, type=type_, invitable=False)
    except discord.HTTPException:
        thread = await channel.create_thread(name=name, type=discord.ChannelType.public_thread)

    if type(start_msg) == dict:
        message = await thread.send(**start_msg)
    else:
        if mention_users is True:
            message = await thread.send(content=f'<@{"".join([str(id_) for id_ in add_users])}>')
        elif mention_users:
            message = await thread.send(content=f'<@{"".join([str(id_) for id_ in mention_users])}>')
        else:
            message = await thread.send(content=f'.')
    edit_message = ''.join([f'<@{id_}>' for id_ in add_users])

    if add_roles:
        edit_message += f'<@&{"".join([str(id_) for id_ in add_roles])}>'

    kwargs = {'content': edit_message}
    if type(start_msg) == str:
        kwargs['content'] += start_msg
    elif isinstance(start_msg, discord.Embed):
        kwargs = {'content': edit_message, 'embed': start_msg}

    await message.edit(**kwargs)
    return thread


async def create_ticket(thread_channel: discord.TextChannel,
                        user_id: int,
                        start_msg: Union[str, discord.Embed, dict] = None
                        ) -> int:
    """Creates a ticket for user

    Parameter:
        thread_channel: (discord.TextChannel) text channel to create the ticket in
        user_id: (int) id of the user creating the ticket
        start_msg: (Union[str, discord.Embed]) Initial message on creating the thread
    """
    for thread in thread_channel.threads:
        if thread.name == str(user_id):
            if type(start_msg) == dict:
                kwargs = start_msg
            elif type(start_msg) == str:
                kwargs = {'content': start_msg}
            elif isinstance(start_msg, discord.Embed):
                kwargs = {'embed': start_msg}
            else:
                raise Exception('start_msg must be dict as kwargs for .send or str or embed')
            await thread.send(**kwargs)
            return thread.id

    thread_name = str(user_id)
    return (await create_thread(
        channel=thread_channel,
        name=thread_name,
        add_users=(user_id,),
        mention_users=(user_id,),
        start_msg=start_msg
    )).id

