import os

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
    await channel.send(f'Welcome {member.mention}! You are the {GUILD.member_count} member')
    #await member.add_roles(member.guild.get_role(739300133291950172))

@client.command()
async def rules(ctx):
    embed=discord.Embed(title="Rules")
    embed.set_author(name="Fish Groove Mod Team",icon_url="https://cdn.discordapp.com/attachments/676084092269363230/828073160791425024/FG_XTC_English_Settlemnt_loop.gif")
    embed.add_field(name="1. Respect others in the server space.",value="This includes no bigotry (racism, homophobia, ableism, etc.), using people’s pronouns, and not putting down others for different opinions than your own (that don’t fall under the bigotry/harmful categories). If a moderator believes that you have beliefs that would in any way be negative to the server community, they reserve the right to act on this rule.")
    embed.add_field(name="2. You must be 16 or older to use this server.",value="Sex, drug, and general “adult” related topics do come up in conversation, but please use judgement in what you say and how what you say can make other people uncomfortable. Long form/in depth discussion of adult topics should stay outside the server. NSFW images should not be posted if their content is too extreme. Even so, they should always be posted with a content warning and a spoiler.")
    embed.add_field(name="3. No Spam",value="Be mindful using reaction images and GIFs, as well as jokes/posts that take up extensive space on screens. Overuse/spam will result in a mute. Spam includes extensive bot commands in channels that aren’t <#739300134340395039>")
    embed.add_field(name="4. No Outside Server Drama.",value="Shit-talking is not useful to anyone. If you have an issue with another user here, bring it up with a moderator privately.")
    embed.add_field(name="5. Use common sense..",value="If you're wondering whether or not you should post something, don't post it.")
    embed.set_footer(text="Moderators reserve the right to act on any of these rules as they see fit. Mods reserve the right to change the rules and changes will be made note of in ⁠announcements. Violations of these rules will be acted on with warnings and mutes except for extreme circumstances. Repeated violations will result in a kick or ban.")
    await ctx.send(embed=embed)

client.run(TOKEN)
