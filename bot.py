import os
import logging,logging.handlers

import aiosqlite,discord,asyncio,random
from discord import File
from discord.ext import commands,tasks
from dotenv import load_dotenv
from easy_pil import Editor,load_image_async,Font,Text

"""
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
logging.getLogger('discord.http').setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    filename='discord.log',
    encoding='utf-8',
    maxBytes=32 * 1024 * 1024,  # 32 MiB
    backupCount=5,  # Rotate through 5 files
)
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)
"""

load_dotenv()
TOKEN=os.getenv('DISCORD_TOKEN')
GUILD=os.getenv('DISCORD_GUILD')

client=discord.Client(command_prefix='!',intents=discord.Intents.all())
bot=commands.Bot(command_prefix='!',intents=discord.Intents.all())

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening,name="Peter Hammill"))
    for guild in client.guilds:
        if guild.name==GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name} (id: {guild.id})'
    )

@client.event
async def on_member_join(member):
    channel=client.get_channel(739300133702991937)
    background_images=os.listdir("assets/background_images")
    background=Editor("assets/background_images/" + random.choice(background_images)).resize((825,500)) # for reference: images should be 825,580
    profile_image=await load_image_async(str(member.avatar.url))
    profile=Editor(profile_image).resize((150,150)).circle_image()
    poppins=Font.poppins(variant="bold", size=50)
    poppins_small=Font.poppins(size=30,variant="bold")
    background.paste(profile,(325,90))
    background.ellipse((325,90),150,150,outline="white",stroke_width=5)
    background.text((400,260),f"Welcome {member.name}",font=poppins, color="white", align="center")
    background.text((400,325),"Lets get fish grooving!",font=poppins_small, color="white", align="center")
    file=File(fp=background.image_bytes,filename="1690987294635472.png")
    await channel.send(file=file)

    #role=discord.utils.get(member.guild.roles,id="739300133291950172")
    await member.add_roles(discord.Object(id=739300133291950172))

@bot.command()
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
