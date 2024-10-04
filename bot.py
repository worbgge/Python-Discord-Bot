import os,sys
import logging,logging.handlers
import subprocess as sp

import aiosqlite,discord,asyncio,random
from discord import File
from discord.ext import commands,tasks
from dotenv import load_dotenv
from easy_pil import Editor,Canvas,load_image_async,Font,Text

### LOGGING ###

logger=logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
logging.getLogger('discord.http').setLevel(logging.INFO)

handler=logging.handlers.RotatingFileHandler(filename='discord.log',encoding='utf-8',maxBytes=32*1024*1024,backupCount=5,)
dt_fmt='%Y-%m-%d %H:%M:%S'
formatter=logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}',dt_fmt,style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)

load_dotenv()
TOKEN=os.getenv('DISCORD_TOKEN')
GUILD=os.getenv('DISCORD_GUILD')

bot=commands.Bot(command_prefix='!',intents=discord.Intents.all())

### CHANGE DISCORD ACTIVITY AND SETUP DATABASE FOR STARBOARD ###

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening,name="Peter Hammill"))
    # database for starboard
    setattr(bot,"star_db",await aiosqlite.connect('starboard.db'))
    await asyncio.sleep(2)
    async with bot.star_db.cursor() as cursor:
        await cursor.execute("CREATE TABLE IF NOT EXISTS starSetup (starLimit INTEGER, channel INTEGER, guild INTEGER)")
    await bot.star_db.commit()
    for guild in bot.guilds:
        if guild.name==GUILD:
            break
    # database for levels
    setattr(bot,"lvl_db",await aiosqlite.connect('level.db'))
    await asyncio.sleep(3)
    async with bot.lvl_db.cursor() as cursor:
        await cursor.execute("CREATE TABLE IF NOT EXISTS levels (level INTEGER, xp INTEGER, user INTEGER, guild INTEGER)")

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
        async with bot.star_db.cursor() as cursor:
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
    async with bot.star_db.cursor()as cursor:
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
    await bot.star_db.commit()

@setup.command()
@commands.has_permissions(manage_guild=True)
async def stars(ctx,star:int):
    async with bot.star_db.cursor()as cursor:
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
    await bot.star_db.commit()

@bot.event
async def on_command_error(ctx,error):
    em=discord.Embed(title="Error",description=f"```{error}```")
    await ctx.send(embed=em,delete_after=90)
    return

### LEVEILING STUFF :D ###

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    author=message.author
    guild=message.guild
    async with bot.lvl_db.cursor() as cursor:
        await cursor.execute("SELECT xp FROM levels WHERE user = ? AND guild = ?",(author.id,guild.id,))
        xp=await cursor.fetchone()
        await cursor.execute("SELECT level FROM levels WHERE user = ? AND guild = ?",(author.id,guild.id,))
        level=await cursor.fetchone()

        if not xp or not level:
            await cursor.execute("INSERT INTO levels (level, xp, user, guild) VALUES (?, ?, ?, ?)",(0,0,author.id,guild.id,))

        try:
            xp=xp[0]
            level=level[0]
        except TypeError:
            xp=0
            level=0

        if level<5:
            xp+=random.randint(1,3)
            await cursor.execute("UPDATE levels SET xp = ? WHERE user = ? AND guild = ?",(xp,author.id,guild.id,))
        else:
            rand=random.randint(1,(level//4))
            if rand==1:
                xp+=random.randint(1,3)
                await cursor.execute("UPDATE levels SET xp = ? WHERE user = ? AND guild = ?",(xp,author.id,guild.id,))
        if xp>=100:
            level+=1
            await cursor.execute("UPDATE levels SET level = ? WHERE user = ? AND guild = ?",(level,author.id,guild.id,))
            await cursor.execute("UPDATE levels SET xp = ? WHERE user = ? AND guild = ?",(0,author.id,guild.id,))
            await message.channel.send(f"{author.mention} has leveled up to level **{level}**!")
    await bot.lvl_db.commit()
    await bot.process_commands(message)

@bot.command(aliases=['lvl','rank','r'])
async def level(ctx,member:discord.Member=None):
    if member is None:
        member=ctx.author
    async with bot.lvl_db.cursor() as cursor:
        await cursor.execute("SELECT xp FROM levels WHERE user = ? AND guild = ?",(member.id,ctx.guild.id,))
        xp=await cursor.fetchone()
        await cursor.execute("SELECT level FROM levels WHERE user = ? AND guild = ?",(member.id,ctx.guild.id,))
        level=await cursor.fetchone()

        if not xp or not level:
            await cursor.execute("INSERT INTO levels (level, xp, user, guild) VALUES (?, ?, ?, ?)",(0,0,member.id,ctx.guild.id,))

        try:
            xp=xp[0]
            level=level[0]
        except TypeError:
            xp=0
            level=0

    user_data={"name":f"{member.name}","xp":xp,"level":level,"next_level_xp":100,"percentage":xp,}

    background=Editor(Canvas((720,300),color="#282828"))
    profile_picture=await load_image_async(str(member.avatar.url))
    profile=Editor(profile_picture).resize((150,150)).circle_image()

    poppins=Font.poppins(size=40)
    poppins_small=Font.poppins(size=30)

    background.paste(profile,(30,30))

    background.rectangle((30,200),width=650,height=40,color="#fff")
    background.bar((30,200),max_width=650,height=41,percentage=user_data["percentage"],color="#C3B1E0",)
    background.text((200,100),user_data["name"],font=poppins,color="#fff")

    #background.rectangle((200,100),width=350,height=2,fill="#fff")
    background.text((600,100),f"lvl. {user_data['level']}",font=poppins,color="#fff")
    background.text((300,255),f"{user_data['xp']}/{user_data['next_level_xp']}",font=poppins_small,color="#fff")
    file=discord.File(fp=background.image_bytes,filename="levelcard.png")
    await ctx.send(file=file)

@bot.command(aliases=["lb","lvlboard"])
async def leaderboard(ctx):
    async with bot.lvl_db.cursor() as cursor:
        await cursor.execute("SELECT level, xp, user FROM levels WHERE guild = ? ORDER BY level DESC, xp DESC LIMIT 10",(ctx.guild.id,))
        data=await cursor.fetchall()
        if data:
            em=discord.Embed(title="Leveling Leaderboard")
            count=0
            for table in data:
                count+=1
                user=ctx.guild.get_member(table[2])
                em.add_field(name=f"{count}. {user.name}",value=f"Level: **{table[0]}** | XP: **{table[1]}**",inline=False)
            return await ctx.send(embed=em)
        return await ctx.send("There are no users stored in the leaderboard")

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
