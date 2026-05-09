from email.mime import message
from discord import message

import discord
from discord.ext import commands
from datetime import timedelta

# =========================
# BOT TOKEN
# =========================
TOKEN = "MTUwMTg5NTMxNDA5MTY3NTcwOA.GqjHh2.MyzQT-qMcQ4we2C7RbRigyCwGi5n9kftlDXBbc"
# =========================
# INTENTS
# =========================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

# Disable default help command
bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

# =========================
# SETTINGS
# =========================

WELCOME_CHANNEL_ID = 1475200159578194136
FAREWELL_CHANNEL_ID = 1475203206396248094
MEMES_CHANNEL_ID = 1475393987551432755
# =========================
# DATABASES
# =========================

warnings_db = {}
filtered_words = ["badword"]

automod_enabled = True
antilink_enabled = True

# =========================
# EVENTS
# =========================

@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online!")

# =========================
# MESSAGE EVENT
# =========================

@bot.event
async def on_message(message):

    global automod_enabled
    global antilink_enabled

    if message.author.bot:
        return

    # =========================
    # BAD WORD FILTER
    # =========================

    if automod_enabled:

        for word in filtered_words:

            if word.lower() in message.content.lower():

                await message.delete()

                await message.channel.send(
                    f"❌ {message.author.mention}, that word is not allowed.",
                    delete_after=5
                )

                return

    # =========================
    # ANTI LINK
    # =========================

    # =========================
    # ANTI LINK
    # =========================

    if antilink_enabled:

        # Allow links in memes channel
        if message.channel.id != MEMES_CHANNEL_ID:

            if (
                "http://" in message.content.lower()
                or "https://" in message.content.lower()
                or "discord.gg/" in message.content.lower()
            ):

                await message.delete()

                await message.channel.send(
                    f"🔗 {message.author.mention}, links are not allowed here.",
                    delete_after=5
                )

                return

    await bot.process_commands(message)

# =========================
# HELP COMMAND
# =========================

@bot.command()
async def help(ctx):

    embed = discord.Embed(
        title="🛡️ WBot Commands",
        description="Here are all available commands",
        color=discord.Color.blue()
    )

    # MODERATION
    embed.add_field(
        name="⚔️ Moderation",
        value=(
            "!ban\n"
            "!unban\n"
            "!kick\n"
            "!timeout\n"
            "!warn\n"
            "!warnings\n"
            "!clearwarnings\n"
            "!purge"
        ),
        inline=False
    )

    # PROTECTION
    embed.add_field(
        name="🛡️ Protection",
        value=(
            "!automod\n"
            "!antilink\n"
            "!filteradd\n"
            "!filterremove"
        ),
        inline=False
    )

    # UTILITY
    embed.add_field(
        name="🔧 Utility",
        value=(
            "!ping\n"
            "!userinfo\n"
            "!serverinfo\n"
            "!lock\n"
            "!unlock\n"
            "!slowmode\n"
            "!slowoff"
        ),
        inline=False
    )

    await ctx.send(embed=embed)
# =========================
# PING
# =========================

@bot.command()
async def ping(ctx):

    latency = round(bot.latency * 1000)

    await ctx.send(f"🏓 Pong! `{latency}ms`")

# =========================
# BAN
# =========================

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member = None, *, reason=None):

    if member is None:
        await ctx.send("❌ Mention a user to ban.")
        return

    if reason is None:
        reason = "No reason provided."

    try:

        await member.ban(reason=reason)

        await ctx.send(
            f"🔨 {member.mention} has been banned.\nReason: {reason}"
        )

    except discord.Forbidden:
        await ctx.send("❌ I cannot ban this user.")
@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, user):

    banned_users = await ctx.guild.bans()

    # try both name#discriminator AND just name
    target = None

    for ban_entry in banned_users:

        banned_user = ban_entry.user

        # match full tag (old system)
        full_tag = f"{banned_user.name}#{banned_user.discriminator}"

        if user == full_tag or user == banned_user.name:
            target = banned_user
            break

    if target is None:
        await ctx.send("❌ User not found in ban list.")
        return

    await ctx.guild.unban(target)

    await ctx.send(f"🔓 Unbanned {target}")
# =========================
# KICK
# =========================

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member = None, *, reason=None):

    if member is None:
        await ctx.send("❌ Mention a user to kick.")
        return

    if reason is None:
        reason = "No reason provided."

    try:

        await member.kick(reason=reason)

        await ctx.send(
            f"👢 {member.mention} has been kicked.\nReason: {reason}"
        )

    except discord.Forbidden:
        await ctx.send("❌ I cannot kick this user.")

# =========================
# TIMEOUT
# =========================

@bot.command()
@commands.has_permissions(moderate_members=True)
async def timeout(
    ctx,
    member: discord.Member = None,
    minutes: int = 1,
    *,
    reason=None
):

    if member is None:
        await ctx.send("❌ Mention a user.")
        return

    if reason is None:
        reason = "No reason provided."

    duration = timedelta(minutes=minutes)

    try:

        await member.timeout(duration, reason=reason)

        await ctx.send(
            f"⏳ {member.mention} has been timed out for {minutes} minute(s)."
        )

    except discord.Forbidden:
        await ctx.send("❌ I cannot timeout this user.")

# =========================
# WARN
# =========================

@bot.command()
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member = None, *, reason=None):

    if member is None:
        await ctx.send("❌ Mention a user.")
        return

    if reason is None:
        reason = "No reason provided."

    # Create warning data
    if member.id not in warnings_db:
        warnings_db[member.id] = 0

    warnings_db[member.id] += 1

    warns = warnings_db[member.id]

    # Get roles
    warn1 = discord.utils.get(ctx.guild.roles, name="Warn 1")
    warn2 = discord.utils.get(ctx.guild.roles, name="Warn 2")
    warn3 = discord.utils.get(ctx.guild.roles, name="Warn 3")

    # Remove old roles
    for role in [warn1, warn2, warn3]:
        if role in member.roles:
            await member.remove_roles(role)

    # Warning levels
    if warns == 1:

        if warn1:
            await member.add_roles(warn1)

    elif warns == 2:

        if warn2:
            await member.add_roles(warn2)

    elif warns == 3:

        if warn3:
            await member.add_roles(warn3)

    elif warns >= 4:

        await member.ban(reason="Reached 4 warnings")

        await ctx.send(
            f"☠️ {member.mention} has been automatically banned for reaching 4 warnings."
        )

        return

    await ctx.send(
        f"⚠️ {member.mention} now has `{warns}` warning(s).\nReason: {reason}"
    )

# =========================
# WARNINGS
# =========================

@bot.command()
async def warnings(ctx, member: discord.Member = None):

    if member is None:
        await ctx.send("❌ Mention a user.")
        return

    warning_count = warnings_db.get(member.id, 0)

    await ctx.send(
        f"⚠️ {member.mention} has `{warning_count}` warning(s)."
    )

# =========================
# CLEAR WARNINGS
# =========================

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clearwarnings(ctx, member: discord.Member = None):

    if member is None:
        await ctx.send("❌ Mention a user.")
        return

    warnings_db[member.id] = 0

    warn1 = discord.utils.get(ctx.guild.roles, name="Warn 1")
    warn2 = discord.utils.get(ctx.guild.roles, name="Warn 2")
    warn3 = discord.utils.get(ctx.guild.roles, name="Warn 3")

    for role in [warn1, warn2, warn3]:

        if role and role in member.roles:
            await member.remove_roles(role)

    await ctx.send(
        f"✅ Cleared all warnings for {member.mention}."
    )

# =========================
# PURGE
# =========================

@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int = None):

    if amount is None:
        await ctx.send("❌ Enter amount of messages.")
        return

    await ctx.channel.purge(limit=amount + 1)

    msg = await ctx.send(f"🗑️ Deleted {amount} messages.")

    await msg.delete(delay=3)

# =========================
# AUTOMOD
# =========================

@bot.command()
@commands.has_permissions(administrator=True)
async def automod(ctx, setting=None):

    global automod_enabled

    if setting is None:
        await ctx.send("❌ Use `on` or `off`.")
        return

    if setting.lower() == "on":

        automod_enabled = True
        await ctx.send("🛡️ Automod enabled.")

    elif setting.lower() == "off":

        automod_enabled = False
        await ctx.send("🛡️ Automod disabled.")

# =========================
# ANTI LINK
# =========================

@bot.command()
@commands.has_permissions(administrator=True)
async def antilink(ctx, setting=None):

    global antilink_enabled

    if setting is None:
        await ctx.send("❌ Use `on` or `off`.")
        return

    if setting.lower() == "on":

        antilink_enabled = True
        await ctx.send("🔗 Anti-link enabled.")

    elif setting.lower() == "off":

        antilink_enabled = False
        await ctx.send("🔗 Anti-link disabled.")

# =========================
# FILTER ADD
# =========================

@bot.command()
@commands.has_permissions(administrator=True)
async def filteradd(ctx, *, word=None):

    if word is None:
        await ctx.send("❌ Enter a word.")
        return

    filtered_words.append(word.lower())

    await ctx.send(f"✅ Added `{word}` to filter.")

# =========================
# FILTER REMOVE
# =========================

@bot.command()
@commands.has_permissions(administrator=True)
async def filterremove(ctx, *, word=None):

    if word is None:
        await ctx.send("❌ Enter a word.")
        return

    if word.lower() in filtered_words:

        filtered_words.remove(word.lower())

        await ctx.send(f"✅ Removed `{word}` from filter.")

    else:
        await ctx.send("❌ Word not found.")

# =========================
# USER INFO
# =========================

@bot.command()
async def userinfo(ctx, member: discord.Member = None):

    member = member or ctx.author

    embed = discord.Embed(
        title=f"👤 User Info - {member}",
        color=discord.Color.green()
    )

    # BASIC INFO
    embed.add_field(name="ID", value=member.id, inline=False)
    embed.add_field(name="Display Name", value=member.display_name, inline=False)
    embed.add_field(name="Bot?", value="Yes 🤖" if member.bot else "No 👤", inline=False)

    # DATES (safe fallback in case joined_at is None)
    joined = member.joined_at.strftime("%d %B %Y") if member.joined_at else "Unknown"
    created = member.created_at.strftime("%d %B %Y")

    embed.add_field(name="Joined Server", value=joined, inline=False)
    embed.add_field(name="Account Created", value=created, inline=False)

    # ROLE INFO
    embed.add_field(name="Top Role", value=member.top_role.mention, inline=False)

    roles = [role.mention for role in member.roles if role.name != "@everyone"]
    embed.add_field(
        name="Roles",
        value=", ".join(roles) if roles else "No roles",
        inline=False
    )

    # STATUS (may require presence intent enabled)
    embed.add_field(name="Status", value=str(member.status).title(), inline=False)

    # AVATAR
    embed.set_thumbnail(url=member.display_avatar.url)

    await ctx.send(embed=embed)
# =========================
# SERVER INFO
# =========================

@bot.command(name="serverinfo")
async def serverinfo(ctx):

    guild = ctx.guild

    text_channels = len(guild.text_channels)
    voice_channels = len(guild.voice_channels)

    embed = discord.Embed(
        title=f"🌌 {guild.name}",
        description="Server overview.",
        color=discord.Color.purple()
    )

    embed.add_field(
        name="👑 Owner",
        value=guild.owner,
        inline=False
    )

    embed.add_field(
        name="👥 Members",
        value=guild.member_count,
        inline=False
    )

    embed.add_field(
        name="🎭 Roles",
        value=len(guild.roles),
        inline=False
    )

    embed.add_field(
        name="💬 Text Channels",
        value=text_channels,
        inline=True
    )

    embed.add_field(
        name="🔊 Voice Channels",
        value=voice_channels,
        inline=True
    )

    embed.add_field(
        name="🚀 Boosts",
        value=guild.premium_subscription_count,
        inline=False
    )

    embed.add_field(
        name="📅 Created",
        value=guild.created_at.strftime("%d %B %Y"),
        inline=False
    )

    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    await ctx.send(embed=embed)

# =========================
# LOCK
# =========================

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):

    await ctx.channel.set_permissions(
        ctx.guild.default_role,
        send_messages=False
    )

    await ctx.send("🔒 Channel locked.")

# =========================
# UNLOCK
# =========================

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):

    await ctx.channel.set_permissions(
        ctx.guild.default_role,
        send_messages=True
    )

    await ctx.send("🔓 Channel unlocked.")

# =========================
# SLOWMODE
# =========================

@bot.command()
@commands.has_permissions(manage_channels=True)
async def slowmode(ctx, seconds: int = None):

    if seconds is None:
        await ctx.send("❌ Enter seconds.")
        return

    await ctx.channel.edit(slowmode_delay=seconds)

    await ctx.send(
        f"🐢 Slowmode set to {seconds} second(s)."
    )

# =========================
# SLOWMODE OFF
# =========================

@bot.command()
@commands.has_permissions(manage_channels=True)
async def slowoff(ctx):

    await ctx.channel.edit(slowmode_delay=0)

    await ctx.send("🐢 Slowmode removed.")

# =========================
# MEMBER JOIN
# =========================

@bot.event
async def on_member_join(member):

    channel = bot.get_channel(WELCOME_CHANNEL_ID)

    if channel is None:
        return

    embed = discord.Embed(
        title="👋 Welcome!",
        description=(
            f"Hey {member.mention}, "
            f"welcome to **{member.guild.name}**!"
        ),
        color=discord.Color.green()
    )

    embed.set_thumbnail(url=member.display_avatar.url)

    embed.set_footer(
        text=f"Member #{member.guild.member_count}"
    )

    await channel.send(embed=embed)

# =========================
# MEMBER LEAVE
# =========================

@bot.event
async def on_member_remove(member):

    channel = bot.get_channel(FAREWELL_CHANNEL_ID)

    if channel is None:
        return

    embed = discord.Embed(
        title="👋 Goodbye!",
        description=f"{member.name} just left the server.",
        color=discord.Color.red()
    )

    embed.set_thumbnail(url=member.display_avatar.url)

    await channel.send(embed=embed)

# =========================
# ERROR HANDLER
# =========================

@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):

        await ctx.send(
            "❌ You do not have permission to use this command."
        )

    elif isinstance(error, commands.MissingRequiredArgument):

        await ctx.send(
            "❌ Missing required argument."
        )

    elif isinstance(error, commands.CommandNotFound):

        await ctx.send(
            "❌ Unknown command."
        )

    else:

        print(error)

# =========================
# RUN BOT
# =========================

bot.run(TOKEN)