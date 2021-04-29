import os

from discord.ext import tasks, commands
import discord
from dotenv import load_dotenv
from datetime import datetime, time, timedelta
import asyncio
import random

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
TEAM = os.getenv('DISCORD_TEAM', 'Nobody')

description = 'A simple bot to serve a simple purpose for now.'
activity = discord.Activity(type=discord.ActivityType.watching, name=f'over {TEAM}')

intents = discord.Intents.all()
client = commands.Bot(command_prefix='?', description=description, intents=intents, activity=activity)

WHEN = time(3, 50, 0)


@client.event
async def on_ready():
    print(f'{client.user} is connected to the following guild:\n')

    guilds = client.guilds
    guilds_list = '\n - '.join([guild.name for guild in guilds])
    print(f'Part of the following Guilds:\n - {guilds_list}')

    for guild in guilds:
        print(f'{guild.name}(id: {guild.id})')
        members = '\n - '.join([member.name for member in guild.members])
        print(f'Guild Members:\n - {members}')


async def retrieve_and_send_shuffle_list():
    guild = discord.utils.get(client.guilds, name=GUILD)

    print(guild.channels[0].channels[1].id)
    print(guild.get_channel(834463800484429897))
    stand_up_channel = guild.get_channel(834463800484429897)
    members = []

    for member in stand_up_channel.members:
        members.append(member.mention)

    random.shuffle(members)

    msg_members_mention_list = '\n - '.join([member for member in members])
    await guild.channels[0].channels[1].send(f"Today's Stand Up Order:\n - {msg_members_mention_list}")


@client.command(description='Generate a shuffled list of members')
async def shuffle(ctx, channel: str):
    se_channel = discord.utils.get(client.get_all_channels(), guild__name=ctx.guild.name, name=channel)
    print(se_channel)
    if se_channel is None:
        await ctx.send("Hey, I dont think such a channel exist...")
    elif not se_channel.members:
        await ctx.send("Hey, there isnt anyone here for me to shuffle!")
    else:
        members = []
        for member in se_channel.members:
            members.append(member.mention)

        random.shuffle(members)
        msg_members_mention_list = '\n - '.join([member for member in members])
        await ctx.send(f"Today's Stand Up Order:\n - {msg_members_mention_list}")


@client.command(description='set daily reminders')
async def notification(ctx):
    await my_background_task.start(ctx)


@tasks.loop(seconds=60)
async def my_background_task(ctx):
    print('hello world running task')
    print(ctx.guild.name)
    guild = discord.utils.get(client.guilds, name=GUILD)
    channel = guild.channels[0].channels[1]
    await channel.send(ctx.message.content)
    # await retrieve_and_send_shuffle_list()


@my_background_task.before_loop
async def before_my_task():
    await client.wait_until_ready()

    now = datetime.now()
    target_time = datetime.combine(now.date(), WHEN)
    seconds_till_target = (target_time - now).total_seconds()
    print("counting down %s" % seconds_till_target)
    await asyncio.sleep(seconds_till_target)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    print(message.content)
    await client.process_commands(message)

# my_background_task.start()
client.run(TOKEN)
