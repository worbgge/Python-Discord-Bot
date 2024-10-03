import os,sys
import logging,logging.handlers
import subprocess as sp

import aiosqlite,discord,asyncio,random
from discord import File
from discord.ext import commands,tasks
from dotenv import load_dotenv
from easy_pil import Editor,load_image_async,Font,Text

### LOGGING ###

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

load_dotenv()
TOKEN=os.getenv('DISCORD_TOKEN')
GUILD=os.getenv('DISCORD_GUILD')

#client=discord.Client(intents=discord.Intents.all())
bot=commands.Bot(command_prefix='!',intents=discord.Intents.all())

### CHANGE DISCORD ACTIVITY AND SETUP DATABASE FOR STARBOARD ###

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening,name="Peter Hammill"))
    setattr(bot,"db",await aiosqlite.connect('starboard.db'))
    await asyncio.sleep(2)
    async with bot.db.cursor() as cursor:
        await cursor.execute("CREATE TABLE IF NOT EXISTS starSetup (starLimit INTEGER, channel INTEGER, guild INTEGER)")
    await bot.db.commit()
    for guild in bot.guilds:
        if guild.name==GUILD:
            break

    print(f'{bot.user} is connected to the following guild:\n'f'{guild.name} (id: {guild.id})'    )

### CUSTOM WELCOME IMAGES + ADD ROLES ON JOIN ###

@bot.event
async def on_member_join(member):
    channel=bot.get_channel(739300133702991937)
    background_images=os.listdir("assets/background_images")
    background=Editor("assets/background_images/" + random.choice(background_images)).resize((825,500)) # for reference: images should be 825,500
    profile_image=await load_image_async(str(member.avatar.url))
    profile=Editor(profile_image).resize((150,150)).circle_image()
    poppins=Font.poppins(variant="bold", size=50)
    poppins_small=Font.poppins(size=30,variant="bold")
    background.paste(profile,(325,90))
    background.ellipse((325,90),150,150,outline="white",stroke_width=5)
    background.text((400,260),f"Welcome {member.name}",font=poppins, color="white", align="center",stroke_width=2,stroke_fill="black")
    background.text((400,325),"Lets get fish grooving!",font=poppins_small, color="white", align="center",stroke_width=2,stroke_fill="black")
    file=File(fp=background.image_bytes,filename="1690987294635472.png")
    await channel.send(file=file)

    await member.add_roles(discord.Object(id=739300133291950172))

### STARBOARD FUNCTION ###

@bot.event
async def on_raw_reaction_add(payload):
    emoji=payload.emoji
    guild=bot.get_guild(payload.guild_id)
    channel=await guild.fetch_channel(payload.channel_id)
    message=await channel.fetch_message(payload.message_id)

    if emoji.name=="⭐":
        async with bot.db.cursor() as cursor:
            await cursor.execute("SELECT starLimit, channel FROM starSetup WHERE guild = ?",(guild.id,))
            data=await cursor.fetchone()
            if data:
                starData=data[0]
                channelData=await guild.fetch_channel(data[1])
                for reaction in message.reactions:
                    if reaction.emoji=="⭐":
                        if reaction.count>=starData:
                            embed=discord.Embed(title="New Starboard Message",description=f"{message.content}") # try change to instead be the amount of reactions, this seems redundant
                            try:
                                embed.set_image(url=message.attachments[0].url)
                            except:
                                pass
                            embed.set_author(name=f"{message.author.name}",icon_url=message.author.avatar.url)
                            embed.set_footer(text=f"Message ID: {message.id}")
                            await channelData.send(embed=embed)

@bot.group()
async def setup(ctx):
    if ctx.invoked_subcommand is None:
        return await ctx.send("That subcommand does not exist")

@setup.command()
@commands.has_permissions(manage_guild=True)
async def channel(ctx,channel:discord.TextChannel):
    async with bot.db.cursor()as cursor:
        await cursor.execute("SELECT channel FROM starSetup WHERE guild = ?",(ctx.guild.id,))
        channelData=await cursor.fetchone()
        if channelData:
            channelData=channelData[0]
            if channelData==channel.id:
                return await ctx.send("That channel is already setup")
            await cursor.execute("UPDATE starSetup SET channel = ? WHERE guild = ?",(channel.id,ctx.guild.id))
            await ctx.send(f"{channel.mention} is now the starboard channel!")
        else:
            await cursor.execute("INSERT INTO starSetup VALUES (?,?,?)",(5,channel.id,ctx.guild.id,))
            await ctx.send(f"{channel.mention} is now the starboard channel!")
    await bot.db.commit()

@setup.command()
@commands.has_permissions(manage_guild=True)
async def stars(ctx,star:int):
    async with bot.db.cursor()as cursor:
        await cursor.execute("SELECT starLimit FROM starSetup WHERE guild = ?",(ctx.guild.id,))
        starData=await cursor.fetchone()
        if starData:
            starData=starData[0]
            if starData==star:
                return await ctx.send("That is already the star limit")
            await cursor.execute("UPDATE starSetup SET starLimit = ? WHERE guild = ?",(star,ctx.guild.id))
            await ctx.send(f"{star} is now the star limit!")
        else:
            await cursor.execute("INSERT INTO starSetup VALUES (?,?,?)",(star,0,ctx.guild.id,))
            await ctx.send(f"{star} is now the star limit!")
    await bot.db.commit()

@bot.event
async def on_command_error(ctx,error):
    em=discord.Embed(title="Error",description=f"```{error}```")
    await ctx.send(embed=em,delete_after=90)
    return

### RULES COMMAND ###

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

bot.run(TOKEN)
