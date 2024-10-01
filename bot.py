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
async def rules(ctx):
    embed=discord.Embed(title="Rules")
    embed.set_author(name="Fish Groove Mod Team",icon_url="https://cdn.discordapp.com/attachments/676084092269363230/828073160791425024/FG_XTC_English_Settlemnt_loop.gif")
    embed.add_field(name="1. Respect other people",value="Respect others in the server space. This includes no bigotry (racism, homophobia, ableism, etc.), using people’s pronouns, and not putting down others for different opinions than your own (that don’t fall under the bigotry/harmful categories). Getting respect you want means giving respect to others. If a moderator believes that you have beliefs that would in any way be negative to the server community they reserve the right to act on this rule.")
    embed.add_field(name="2. Must be older than 16",value="You must be 16 or older to use this server. Sex, drug, and general “adult” related topics do come up in conversation, but please use judgement in what you say and how you say it as to not make other people uncomfortable. NSFW images should be posted with consideration to content if they’re too extreme. Even so, they should always be posted with a content warning and a spoiler.")
    embed.add_field(name="3. No outside server drama",value="Don’t bring drama from other servers/outside of this server to this one. Shittalking is not useful to anyone. If you have an issue with another user here bring it up with a moderator privately.")
    embed.add_field(name="4. Use common sense",value="Use common sense. If you're wondering whether or not you should post something, don't post it.")
    embed.set_footer(text="Moderators reserve the right to act on any of these rules as they see fit. Mods reserve the right to change the rules and changes will be made note of in ⁠announcements. Violations of these rules will be acted on with warnings except for extreme circumstances. Repeated violations will result in a kick or ban.")
    await ctx.send(embed=embed)

client.run(TOKEN)
