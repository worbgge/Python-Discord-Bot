import os,random,sys,subprocess

import aiosqlite,discord
from discord.ext import commands,tasks
from dotenv import load_dotenv

load_dotenv()
TOKEN=os.getenv('DISCORD_TOKEN')
GUILD=os.getenv('DISCORD_GUILD')

client=discord.Client(intents=discord.Intents.all())
client=commands.Bot(command_prefix='!',intents=discord.Intents.all())

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening,name="Peter Hammill"))
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name} (id: {guild.id})'
    )

@client.event
async def on_member_join(member):
    channel = client.get_channel(739300133702991937)
    await channel.send(f'Welcome {member.mention}!')

@client.command()
async def embed(ctx):
    embed=discord.Embed(title="Rules",description="1. pee\n2. penis",color=282828)
    await ctx.send(embed.embed)

client.run(TOKEN)
