import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread
import os
import random

# --- 1. Flask Server (Keep Alive) ---
app = Flask('')

@app.route('/')
def home():
    return "I am alive! Boss!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# --- 2. Bot Configuration ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=["!", "?", ".", "$"], intents=intents, help_command=None)

# Data Storage (Note: Restart hole egulo muche jabe, persistence er jonno Database lage)
channelW = {}
reply_map = {}
bad_words = {}

# --- 3. Events ---
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Logged in as {bot.user.name}")
        print(f"Successfully synced {len(synced)} slash commands")
    except Exception as e:
        print(f"Sync Error: {e}")

@bot.event
async def on_member_join(member):
    guild_id = member.guild.id
    if guild_id in channelW:
        channel = bot.get_channel(channelW[guild_id])
        if channel:
            await channel.send(f"{member.mention} has joined the {member.guild.name} server!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Auto Reply Logic
    if message.content in reply_map:
        await message.channel.send(reply_map[message.content])

    # Bad Word Logic
    if message.content.lower() in bad_words:
        try:
            await message.delete()
            await message.channel.send(f"{message.author.mention}, no bad words allowed!")
        except:
            pass

    await bot.process_commands(message)

# --- 4. Prefix Commands (Moderation) ---
@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Blox Fruits Help", color=discord.Colour.blue(), description="Available commands:")
    if bot.user.avatar:
        embed.set_thumbnail(url=bot.user.avatar.url)
    embed.add_field(name="Prefixes", value="`!`, `?`, `.`, `$`", inline=False)
    embed.add_field(name="Moderation", value="`kick`, `ban`, `unban`, `alert`", inline=False)
    embed.set_footer(text="Developed by asma4563")
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"{member} has been kicked. Reason: {reason}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"{member} has been banned. Reason: {reason}")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def alert(ctx, member: discord.Member):
    await ctx.send(f"{member.mention}, You've been warned!")
    try:
        await member.send(f"You've been warned in {ctx.guild.name}")
    except:
        pass

# --- 5. Slash Commands (Utility & Fun) ---

@bot.tree.command(name="setwelcome", description="Set a channel for welcome messages")
@app_commands.checks.has_permissions(administrator=True)
async def setwelcome(interaction: discord.Interaction, channel: discord.TextChannel):
    channelW[interaction.guild.id] = channel.id
    await interaction.response.send_message(f"Welcome channel set to {channel.mention}!")

@bot.tree.command(name="userinfo", description="Show user information")
async def userinfo(interaction: discord.Interaction, member: discord.Member):
    embed = discord.Embed(title=f"{member.name}'s info", color=discord.Colour.blue())
    if member.avatar:
        embed.set_thumbnail(url=member.avatar.url)
    embed.add_field(name="Name", value=f"`{member.name}`", inline=True)
    embed.add_field(name="ID", value=f"`{member.id}`", inline=True)
    embed.add_field(name="Joined At", value=f"`{member.joined_at.strftime('%Y-%m-%d')}`", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="roll", description="Roll a dice (1-6)")
async def roll(interaction: discord.Interaction):
    dice_images = {
        1: "https://i.postimg.cc/KY6v1Cv3/image1.png",
        2: "https://i.postimg.cc/RFwCKGNq/image2.png",
        3: "https://i.postimg.cc/nLycXNcq/image3.png",
        4: "https://i.postimg.cc/bJ1YkLsG/image4.png",
        5: "https://i.postimg.cc/fLYWm5Jt/image5.png",
        6: "https://i.postimg.cc/mD7ZCVt1/image6.png"
    }
    n = random.randint(1, 6)
    embed = discord.Embed(title="🎲 Dice Roll", color=discord.Color.blue())
    embed.add_field(name=f"Result: {n}", value=f"You've rolled a {n}!")
    embed.set_thumbnail(url=dice_images[n])
    embed.set_footer(text=f"Requested by {interaction.user.name}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="setreply", description="Set an auto-reply word")
@app_commands.checks.has_permissions(manage_messages=True)
async def setreply(interaction: discord.Interaction, trigger: str, response: str):
    reply_map[trigger] = response
    await interaction.response.send_message(f"Auto-reply set: `{trigger}` -> `{response}`")

@bot.tree.command(name="setword", description="Add a bad word to blacklist")
@app_commands.checks.has_permissions(manage_messages=True)
async def setword(interaction: discord.Interaction, word: str):
    bad_words[word.lower()] = word.lower()
    await interaction.response.send_message(f"Word `{word}` added to blacklist!")

# --- 6. Run the Bot ---
keep_alive()
token = os.environ.get("TOKEN")
if token:
    bot.run(token)
else:
    print("❌ TOKEN not found in Environment Variables!")
