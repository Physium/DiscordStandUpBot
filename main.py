import os

from discord.ext import tasks, commands
import discord
from dotenv import load_dotenv
from datetime import datetime, time, timedelta, date
import asyncio
import random
import json

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
TEAM = os.getenv('DISCORD_TEAM', 'Nobody')
USER = os.getenv('DISCORD_USER')
FILTER_MESSAGE = os.getenv('FILTER_MESSAGE')
CHANNELS = os.getenv('DISCORD_CHANNELS')

channels_json = json.loads(CHANNELS)

description = 'A simple bot to serve a simple purpose for now.'
activity = discord.Activity(type=discord.ActivityType.watching, name=f'over {TEAM}')
monitored_guild = None

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
        if guild.id == int(GUILD):
            global monitored_guild
            monitored_guild = guild

        print(f'{guild.name}(id: {guild.id})')
        members = '\n - '.join([member.name for member in guild.members])
        print(f'Guild Members:\n - {members}')

    print(monitored_guild)


def check_channel(channel_id):
    try:
        channels_json[channel_id]
        return True
    except KeyError:
        return False


def shuffle_members(channel):
    members = []
    for member in channel.members:
        if not member.bot: # Ignore bots in voice channels
            members.append(member.mention)

    random.shuffle(members)
    return members


@client.command(description='Generate a shuffled list of members')
async def shuffle(ctx, channel: str):
    se_channel = discord.utils.get(client.get_all_channels(), guild__name=ctx.guild.name, name=channel)
    print(se_channel)
    if se_channel is None:
        await ctx.send("Hey, I dont think such a channel exist...")
    elif not se_channel.members:
        await ctx.send("Hey, there isnt anyone here for me to shuffle!")
    else:
        members = shuffle_members(se_channel)
        msg_members_mention_list = '\n '.join([f'{i}) {member}' for i, member in enumerate(members, start=1)])
        await ctx.send(f"Today's Stand Up Order:\n {msg_members_mention_list}")


@client.command(description='Day(s) since last incident')
async def incident(ctx, input_date: str = ""):
    channel_id = str(ctx.channel.id)

    try:
        if check_channel(channel_id):
            text = ""
            if input_date != "":
                incident_date = datetime.strptime(input_date, '%d/%m/%Y')
                channels_json[channel_id]['incident_date'] = incident_date.strftime('%d/%m/%Y')
                text += "Added New Incident Date! "

            if channels_json[channel_id].get('incident_date') is None:
                raise Exception("No incidents set!")

            delta_days = datetime.today() - datetime.strptime(channels_json[channel_id]['incident_date'], "%d/%m/%Y")
            if delta_days.days < 0:
                raise Exception("You living in the future or what?")

            text += f"Its been {delta_days.days} days since last incident"
            await ctx.send(text)
    except ValueError:
        await ctx.send(f"Incorrect date format, use DD/MM/YYYY")
    except BaseException as err:
        await ctx.send(err)

# @client.command(description='set daily reminders')
# async def notification(ctx):
#     client.loop.create_task(my_background_task(ctx))
#     await my_background_task.start(ctx)


# @tasks.loop(seconds=60)
# async def my_background_task(ctx):
#     print('hello world running task')
#     print(ctx.guild.name)
#     guild = discord.utils.get(client.guilds, name=GUILD)
#     # channel = guild.channels[0].channels[1]
#     await ctx.send(ctx.message.content)


# @my_background_task.before_loop
# async def before_my_task():
#     await client.wait_until_ready()
#
#     now = datetime.now()
#     target_time = datetime.combine(now.date(), WHEN)
#     seconds_till_target = (target_time - now).total_seconds()
#     print("counting down %s" % seconds_till_target)
#     await asyncio.sleep(seconds_till_target)

async def carl_bot_message_filter(message):
    channel_id_str = str(message.channel.id)

    if message.guild == monitored_guild and message.author.name == USER and check_channel(channel_id_str):
        if FILTER_MESSAGE in message.content:
            if message.role_mentions:
                mention = ' ' + message.role_mentions[0].mention + '!'
            elif not message.role_mentions:
                mention = '!'
            countdown = channels_json[str(message.channel.id)]['shuffle_countdown']
            await message.channel.send(f'Thank you {message.author.mention} for the reminder!'
                                       f' Gather up{mention} '
                                       f"I will start shuffling in {countdown} seconds!")
            await asyncio.sleep(countdown)

            voice_ids = channels_json[channel_id_str]['voice_ids']
            text = f"{date.today().strftime('%B %d, %Y')} Shuffle Order(s)!"
            for voice_id in voice_ids:
                voice_channel = discord.utils.get(
                    message.guild.channels,
                    id=voice_id
                )
                members = shuffle_members(voice_channel)
                text += f"\nStand Up Order for {voice_channel.mention}:"
                if members:
                    msg_members_mention_list = '\n '.join([f'{i}) {member}' for i, member in enumerate(members, start=1)])
                    text += f"\n{msg_members_mention_list}"
                elif not members:
                    text += f"\n - What am I shuffling when there is no one here?!"

            if channels_json[channel_id_str].get('incident_date') is not None:
                incident_date = datetime.strptime(channels_json[channel_id_str]['incident_date'], "%d/%m/%Y")
                date_delta = datetime.today() - incident_date
                text += f"\n Its been {date_delta.days} day(s) since last incident on {incident_date.strftime('%B %d, %Y')}"

            await message.channel.send(text)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    await carl_bot_message_filter(message)

    print(message.content)
    await client.process_commands(message)

client.run(TOKEN)
