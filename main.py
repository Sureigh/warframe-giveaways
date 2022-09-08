import asyncio
import json
import traceback

import discord
from discord.ext import tasks, commands
import mongodb as mongo

import cogs.giveaways as giveaways
import utils.parse_commands as parse
import utils.template as template


# I'll be leaving a lot of comments over your code, so feel free to have a look over
# what I wrote to get a good idea of what I've changed,
# and then delete it afterwards when you're done. 

# NOTE: I would recommend installing Jishaku.
# It allows you to safely evaluate and run code on your bot directly without having to 
# reboot or reload things, for quick and dirty testing.
# https://github.com/Gorialis/jishaku

# NOTE: Setting up logging can give you data about why your bot is causing issues.
# https://discordpy.readthedocs.io/en/stable/logging.html

# NOTE: Instead of importing data through JSON files, I would recommend importing
# variables through Python files instead. 

# JSON files can be notoriously slow to read, causes blocking
# (bot cannot perform tasks asynchronously), and if your bot dies while it's
# attempting to read the file, you will probably lose all the data on the file. 
# For local configurations on your bot (such as temporary data storage), it's fine,
# but for storing anything more long term, use MongoDB or a proper SQL database. 

mongodb = mongo.Collection(mongo.TestCloud)
with open('config.json', encoding='utf-8') as file:
    config = json.load(file)
    token = config['token']
    prefix = config['prefix']

# This could be: 
"""
# config.py
token = "discord token"
prefix = "bot prefix"

# main.py
import config

bot = commands.Bot(command_prefix=commands.when_mentioned_or(config.prefix), intents=intents)
...
bot.start(config.token)
"""
# You can also use starred imports for the config if you make sure no values get shadowed

# NOTE: Although there's no actual guidelines to follow for making bots,
# it's generally a standard to subclass the Bot class and create your own,
# in case there's things you want to do before the bot connects online.

COGS = ["errorhandle", ] #giveaways

class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(
            command_prefix=commands.when_mentioned_or(prefix), 
            intents=discord.Intents.default(), 
            **kwargs
        )

    async def setup_hook(self):
        # Load cogs
        for cog in COGS:
            try:
                await self.load_extension(cog)
                print(f"Loaded cog {cog}")
            except Exception as exc:
                print(f'Could not load extension {cog} due to {exc.__class__.__name__}: {exc}')

    async def on_ready(self):
        print(f'Logged on as {self.user} (ID: {self.user.id})')

# NOTE: I would also recommend keeping this main file as flat as possible, and 
# define the commands here in a cog - unless you always need the commands
# on the bot (for testing/evaluation purposes) 

# NOTE: discord.py (the module) actually comes with a helper script to help you
# create a simple bot and cogs, if you need an idea on how to structure your file.
# Type `python -m discord -h` to get an idea of what you can do. 

bot = Bot()

@bot.command(aliases=['say', 'repeat', 'print'])
async def echo(ctx):
    await ctx.channel.send(parse.get_args(ctx.message.content, arg_delimiter=''))


@bot.command()
async def embed(ctx):
    try:
        dict_ = json.loads(parse.get_args(ctx.message.content, arg_delimiter=''))
        embed_ = discord.Embed.from_dict(dict_)
        await ctx.send(embed=embed_)
    except (json.decoder.JSONDecodeError, TypeError) as error:
        return await ctx.send(embed=template.error(f'```{str(error)}```'))
    except discord.errors.HTTPException:
        correct_usage = {
            "title": "example title",
            "description": "example description",
            "footer": {
                "text": "footer text"
            },
            "fields": [
                {
                    "name": "field1",
                    "value": "field value 1"
                }
            ]
        }
        return await ctx.send(embed=template.error(f'incorrect format\n\n'
                                                   f'Correct example:```json\n{json.dumps(correct_usage, indent=4)}```'))


@bot.command(name='clear')
async def clear_threads(ctx):
    if ctx.author.id != 468631903390400527:
        return
    for thread in ctx.channel.threads:
        await thread.delete()


@bot.command(name='db')
async def db(ctx):
    message = '```json\n'
    for document in mongodb.find(None, True):
        document = json.dumps(document, indent=4, ensure_ascii=False)
        if len(message) + len(document) + 3 > 2000:
            await ctx.send(message+'```')
            message = '```json\n'
        message += '\n' + document
    await ctx.send(message + '```')


@bot.command()
async def callvote(ctx):
    """To be implemented"""
    pass

if __name__ == '__main__':
    bot.run(token)
