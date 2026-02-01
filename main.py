from flask import Flask
from threading import Thread
import discord
from discord.ext import commands
from discord import app_commands
import os
import random

# --- Flask Server ---
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

# --- Storage ---
channelW = {}
reply = {}
badW = {}

# --- Bot Setup ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True # Make sure this is enabled in Developer Portal

bot = commands.Bot(command_prefix=["!", "?", ".", "$"], intents=intents, help_command=None)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Logged in as {bot.user.name}")
        print(f"Successfully loaded {len(synced)} slash commands")
    except Exception as e:
        print(f"Sync Error: {e}")

# --- Events ---

@bot.event
async def on_member_join(member):
    guild_id = member.guild.id
    if guild_id in channelW:
        channel_id = channelW[guild_id]
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(f"{member.mention} has joined the {member.guild.name} server")

@bot.event
async def on_message(message):
    if message.author == bot.user: 
        return
    
    # Custom Auto Reply
    if message.content in reply:
        await message.channel.send(reply[message.content])
    
    # Bad Word Filter
    if message.content.lower() in badW:   
        try:
            await message.delete()
            await message.channel.send(f"{message.author.mention}, No bad words allowed!")
        except:
            pass
    
    await bot.process_commands(message)

# --- Prefix Commands ---

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Blox Fruits Help", color=discord.Colour.blue())
    embed.description = "Here are the available commands"
    if bot.user.avatar:
        embed.set_thumbnail(url=bot.user.avatar.url)
    embed.add_field(name="Command Prefix", value="!, ?, . and $", inline=False)
    embed.add_field(name="Moderation", value="``kick``, ``ban``, ``unban``, ``alert``", inline=False)
    embed.set_footer(text="Developed by asma4563")
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"{member} has been kicked, reason: {reason}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"{member} has been banned, reason: {reason}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_input):
    found = False
    async for entry in ctx.guild.bans():
        user = entry.user
        if (user.name == user_input) or (str(user.id) == user_input):
            await ctx.guild.unban(user)
            await ctx.send(f"{user.name} is unbanned from the server")
            found = True
            break
    if not found:
        await ctx.send(f"Can't find user {user_input}")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def alert(ctx, member: discord.Member):
    await ctx.send(f"{member.mention}, You've been warned")
    try:
        await member.send(f"You've been warned from {ctx.guild.name}")
    except:
        pass

# --- Slash Commands ---

@bot.tree.command(name="setwelcome", description="set a channel for welcome")
@app_commands.checks.has_permissions(administrator=True)
async def setwelcome(interaction: discord.Interaction, channel: discord.TextChannel):
    channelW[interaction.guild.id] = channel.id
    await interaction.response.send_message(f"Your welcome channel set for {channel.mention}!")

@bot.tree.command(name="help", description="see all commands")
async def help_slash(interaction: discord.Interaction):
    embed = discord.Embed(title="Blox Fruits Help", color=discord.Colour.blue())
    embed.description = "Here are the available commands"
    if bot.user.avatar:
        embed.set_thumbnail(url=bot.user.avatar.url)
    embed.add_field(name="Prefixes", value="!, ?, . and $", inline=False)
    embed.add_field(name="Commands", value="``kick``, ``ban``, ``unban``", inline=False)
    embed.set_footer(text="Developed by asma4563")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="kick", description="kick a member")
@app_commands.describe(member="Select the member", reason="Type the reason")
@app_commands.checks.has_permissions(kick_members=True)
async def kick_slash(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    await member.kick(reason=reason)
    await interaction.response.send_message(f"{member} has been kicked, reason: {reason}")

@bot.tree.command(name="ban", description="ban a member")
@app_commands.describe(member="Select the member", reason="Type the reason")
@app_commands.checks.has_permissions(ban_members=True)
async def ban_slash(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    await member.ban(reason=reason)
    await interaction.response.send_message(f"{member} has been banned, reason: {reason}")

@bot.tree.command(name="unban", description="unban a member")
@app_commands.describe(user_input="User ID or Name")
@app_commands.checks.has_permissions(ban_members=True)
async def unban_slash(interaction: discord.Interaction, user_input: str):
    found = False
    async for entry in interaction.guild.bans():
        user = entry.user
        if (user.name == user_input) or (str(user.id) == user_input):
            await interaction.guild.unban(user)
            await interaction.response.send_message(f"{user.name} is unbanned from the server")
            found = True
            break
    if not found:
        await interaction.response.send_message(f"Can't find user {user_input}")

@bot.tree.command(name="userinfo", description='show your info')
@app_commands.describe(member="Select a member")
async def userinfo(interaction: discord.Interaction, member: discord.Member):
    embed = discord.Embed(title=f"{member.name}'s info", color=discord.Colour.blue())
    if member.avatar:
        embed.set_thumbnail(url=member.avatar.url)
    embed.add_field(name="Name", value=f"``{member.name}``", inline=True)
    embed.add_field(name="ID", value=f"``{member.id}``", inline=True)
    formatted_date = member.joined_at.strftime('%Y-%m-%d')
    embed.add_field(name="Joined At", value=f"``{formatted_date}``", inline=False)
    embed.set_footer(text=f"Requested by {interaction.user.name}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="roll", description="roll a number from 1 to 6")
async def roll(interaction: discord.Interaction):
    dice_links = {
        1: "https://i.postimg.cc/KY6v1Cv3/image1.png",
        2: "https://i.postimg.cc/RFwCKGNq/image2.png",
        3: "https://i.postimg.cc/nLycXNcq/image3.png",
        4: "https://i.postimg.cc/bJ1YkLsG/image4.png",
        5: "https://i.postimg.cc/fLYWm5Jt/image5.png",
        6: "https://i.postimg.cc/mD7ZCVt1/image6.png"
    }
    randomN = random.randint(1, 6)
    embed = discord.Embed(title="Dice", colour=discord.Color.blue())
    embed.add_field(name=f"Dice {randomN}", value=f"You've rolled {randomN} in the dice!")
    embed.set_thumbnail(url=dice_links[randomN])
    embed.set_footer(text=f"Requested by {interaction.user.name}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ask", description="bot will reply with yes, no or maybe")
async def ask(interaction: discord.Interaction, question: str):
    lis = ["yes", "no", "maybe", "ask me later", "I don't think so"]
    await interaction.response.send_message(random.choice(lis))

@bot.tree.command(name="setreply", description="set a message for reply")
@app_commands.checks.has_permissions(administrator=True)
async def setreply(interaction: discord.Interaction, rname: str, rreply: str):
    reply[rname] = rreply 
    await interaction.response.send_message(f"Added: {rname} -> {rreply}")

@bot.tree.command(name="setword", description="set bad words and I'll delete")
@app_commands.checks.has_permissions(manage_messages=True)
async def setwords(interaction: discord.Interaction, badws: str):
    badW[badws.lower()] = badws.lower()
    await interaction.response.send_message(f"Added `{badws}` to bad words list!")

# --- Run ---
keep_alive()
token = os.environ.get("TOKEN")
if token:
    bot.run(token)
else:
    print("❌ Error: TOKEN not found!")
